import json
import os
from datasets import Dataset
from fastapi.responses import JSONResponse, FileResponse
from fastapi import status
from pydantic import BaseModel, Field
import uuid
from threading import Thread
import time

from tools.log import logger
from tools.ragas_utils import getContextsAndAnswerByOmega, getRagasEvaluate, queryOmegaDict, ragas_load_data, save_path
from server.router import ragas_router, ResponseModel

omega_task_dict = {}
ragas_task_dict = {}
threads_list = []


def update_task_dict(task_dict, thr_second=3600):
    """删除历史任务(1小时)"""
    timestamp = time.time()
    for task_id in [key for key, val in task_dict.items() if abs(timestamp - val["time"]) > thr_second]:
        del task_dict[task_id]

        # 删除 task_id 相关文件
        pass


class FileRequestModel(BaseModel):
    # 传文件参数
    task_id: str = Field("", description="任务id")
    user_id: str = Field("", description="用户id")
    file_name: str = Field("", description="文件名")
    update_file: bool = Field(True, description="只获取上传文件, False则获取结果文件")

class OmegaRequestModel(BaseModel):
    # omega相关参数
    rag_url: str = Field("https://192.168.12.188:37778/api/v1/chat/completions", description="omega rag对话接口")
    rag_authorization2: str = Field("", description="Authorization2")
    rag_cookie: str = Field("", description="cookie")

    # 其他参数
    task_id: str = Field("", description="任务id")
    user_id: str = Field("", description="用户id")
    file_name: str = Field("", description="文件名")


class RagasRequestModel(BaseModel):
    # LLm相关参数
    model: str = Field("qwen2-72b-instruct", example="")
    base_url: str = Field("http://120.222.7.146:1025/v1", example="")

    # embedding相关参数
    embedding_local_model_path: str = Field("",
                                            description="指定加载本地embedding模型,若使用此参数,embedding_openai_model_url和embedding_openai_model_name则无需使用")
    embedding_openai_model_url: str = Field("", examples=["http://120.222.7.146:18019/v1/embeddings"], description="远程embedding地址")
    embedding_openai_model_name: str = Field("", examples=["m3e-large"], description="远程embedding模型名称")

    # ragas指标
    faithfulness: bool = Field(True, example=True, description="指标1 ‘忠实度’")
    context_recall: bool = Field(True, example=True, description="指标2 ‘上下文召回率’")
    context_precision: bool = Field(True, example=True, description="指标3 ‘上下文精度’")
    answer_relevancy: bool = Field(True, example=True, description="指标4 ‘答案相关性’")
    answer_correctness: bool = Field(False, example=False, description="指标5")
    answer_similarity: bool = Field(False, example=False, description="指标6")
    context_entity_recall: bool = Field(False, example=True, description="指标7 ‘上下文相关性’")

    # 其他参数
    task_id: str = Field("", description="任务id")
    user_id: str = Field("", description="用户id")
    file_name: str = Field("", description="文件名")


@ragas_router.post(path="/getOmegaRag", summary="bytes", response_model=ResponseModel,
                   tags=["RAGAs 评估"])
async def getOmegaRag(
        # req: RequestModel,
        req: OmegaRequestModel,
):
    '''通过omega获取answer和contexts'''

    task_id = req.task_id
    if task_id == "":
        task_id = uuid.uuid4()

    # 判断task_id是否存在
    if task_id in omega_task_dict or task_id in ragas_task_dict:
        content = {"isSuc": False, "code": 0, "msg": f"task_id {task_id} is exist in omega_task", "res": {}}
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)

    filepath = os.path.join(save_path, f"{req.user_id}/ragas_{task_id}.json")

    try:
        org_file_path = os.path.join(save_path, f"{req.user_id}/update_file/{req.file_name}")
        with open(org_file_path, 'r', encoding='utf-8') as f:
            data_samples = json.load(f)

        # 调用 Omega 获取
        omega_task_dict[task_id] = {"time": time.time(), "code": 2, "msg": ""}

        thr = Thread(target=getContextsAndAnswerByOmega,
                     args=(logger, data_samples, filepath, task_id, omega_task_dict, req))
        thr.daemon = True
        threads_list.append(thr)
        thr.start()

        content = {"isSuc": True, "code": 2, "msg": "任务已开启~", "res": {"task_id": task_id}}
        logger.info(f">>> task_id:{task_id}, response:{content}, filepath:{filepath}")

        return JSONResponse(status_code=status.HTTP_200_OK, content=content)

    except Exception as e:
        content = {"isSuc": True, "code": -1, "msg": str(e), "res": {}}
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@ragas_router.post(path="/ragas_evaluate", summary="bytes", response_model=ResponseModel, tags=["RAGAs 评估"])
async def ragas_evaluate(
        # req: RequestModel,
        req: RagasRequestModel,
):
    '''通过 RAGAs 评估数据'''
    task_id = req.task_id

    # 判断task_id是否存在
    if task_id in omega_task_dict or task_id in ragas_task_dict:
        content = {"isSuc": False, "code": 0, "msg": f"task_id {task_id} is exist in ragas_task", "res": {}}
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)

    data_samples, isComplete, error_info = ragas_load_data(req)
    if not isComplete:
        content = {"isSuc": True, "code": -1, "msg": str(error_info), "res": {}}
        return JSONResponse(status_code=200, content=content)
    dataset = Dataset.from_dict(data_samples)

    # ragas评估
    try:
        # 记录一个任务, 并将状态设为"进行中"(code=2)
        ragas_task_dict[task_id] = {"time": time.time(), "code": 2, "msg": ""}

        thr2 = Thread(target=getRagasEvaluate, args=(req, dataset, task_id, ragas_task_dict, logger))
        thr2.daemon = True

        thr2.start()

        content = {"isSuc": True, "code": 0, "msg": "任务已开启~", "res": {}}
        logger.info(f">>> task_id:{task_id}, response:{content}")

        return JSONResponse(status_code=status.HTTP_200_OK, content=content)

    except Exception as e:
        content = {"isSuc": True, "code": 0, "msg": "Success ~", "res": {}}
        return JSONResponse(status_code=status.HTTP_100_CONTINUE, content=content)


@ragas_router.post(path="/query_omega_evaluate", summary="查询结果",
                   response_model=ResponseModel,
                   tags=["查询结果"])
async def query_omega_evaluate(
        req: OmegaRequestModel,
):
    update_task_dict(omega_task_dict)
    omegaMsg, oemagaIsSuc, omeaga_task_code, file = queryOmegaDict(req, omega_task_dict)

    if file != "":
        return file

    content = {"isSuc": oemagaIsSuc, "code": omeaga_task_code, "msg": omegaMsg, "res": {}}
    logger.info(f">>> task_id:{req.task_id}, response:{content}")
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@ragas_router.post(path="/query_ragas_evaluate", summary="查询结果",
                   response_model=ResponseModel,
                   tags=["查询结果"])
async def query_ragas_evaluate(
        req: RagasRequestModel,
):
    task_id = req.task_id
    update_task_dict(ragas_task_dict)
    logger.info(ragas_task_dict)

    if task_id in ragas_task_dict:
        ragas_task_code = ragas_task_dict[task_id]["code"]
        match ragas_task_code:
            case 0:
                ragasMsg = "ragas 任务已完成~"
                ragasIsSuc = True
                content = {"isSuc": ragasIsSuc, "code": ragas_task_code, "msg": ragasMsg, "res": {}}
                logger.info(f">>> task_id:{task_id}, response:{content}")
                return FileResponse(path=os.path.join(save_path, f"{req.user_id}/result_{task_id}.xlsx"),
                                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    status_code=status.HTTP_200_OK)
            case 1:
                ragasMsg = f"ragas 任务失败! {ragas_task_code[task_id]['msg']}" if "msg" in ragas_task_code[
                    task_id] else "ragas 任务失败!"
                ragasIsSuc = False
            case 2:
                ragasMsg = "ragas 任务进行中~"
                ragasIsSuc = True
            case _:
                ragasMsg = "ragas 任务异常!"
                ragasIsSuc = False

        content = {"isSuc": ragasIsSuc, "code": ragas_task_code, "msg": ragasMsg, "res": {}}
        logger.info(f">>> task_id:{task_id}, response:{content}")
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)
    else:
        content = {"isSuc": False, "code": 3, "msg": "ragas 任务不存在!", "res": {}}
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)


if __name__ == '__main__':
    answer, context = getContextsAndAnswerByOmega()
    print(answer)
    print(context)
