import pandas as pd
import requests
import json
import time
from langchain_openai.chat_models import ChatOpenAI
from fastapi.responses import FileResponse
from fastapi import status

from tools.omega_rag_request import get_request_param
from tools.log import logger
from tools.configs import *
from tools.embedding import LocalEmbedding, OpenAIEmbedding

from ragas.metrics import faithfulness, context_recall, context_precision, answer_relevancy, answer_correctness, \
    answer_similarity, context_entity_recall
from ragas import evaluate
from ragas.llms.base import LangchainLLMWrapper
from ragas.run_config import RunConfig


def getContextsAndAnswerByOmega(
        logger,
        data_samples=None,
        filepath="",
        task_id=None,
        task_dict=None,
        req=None,
):
    timestamp0 = time.time()

    if req.rag_url == "":
        req.rag_url = omegaRagUrl
    if req.rag_authorization2 == "":
        req.rag_authorization2 = omegaRagAuthorization2
    if req.rag_cookie == "":
        req.rag_cookie = omegaRagCookie

    header = {
        "Content-Type": "application/json",
        "Authorization2": req.rag_authorization2,
        "cookie": req.rag_cookie
    }
    answer_list, contexts_list = [], []

    try:
        # 切分数据
        n_len = len(data_samples["question"])
        logger.info(f"data nums: {n_len}")
        for i in range(n_len):
            count, flag = 0, False
            question = data_samples["question"][i]
            while count < 2:
                try:
                    data = json.dumps(get_request_param(question))
                    logger.info(f"\nidx: {i}, question: {question}")

                    # if i == 10:
                    #     print(i)

                    # 调用接口
                    response = requests.post(url=req.rag_url, data=data, headers=header, verify=False)
                    text = response.text
                    request_obj = json.loads(text)

                    # 合并数据
                    # 判断返回结果是否正确
                    state_code = request_obj.get("code", 0)
                    if state_code != 200 and state_code != 0:
                        res_dict = {"time": time.time(), "code": 1, "msg": f"{text}"}
                        elapse = computing_task_time(timestamp0)
                        logger.info(f"失败!, task_id:{task_id}, elapse:{elapse}s, msg:{text}")
                        if isinstance(task_dict, dict):
                            task_dict[task_id] = res_dict
                        return res_dict
                    if state_code == 0:
                        answersStr = request_obj["responseData"][1]["historyPreview"][-1]["value"]
                        contextStr = \
                            request_obj["responseData"][1]["historyPreview"][-2]["value"].split("<Data>")[2].split(
                                "</Data>")[0]

                        answer_list.append(answersStr)
                        contexts_list.append([contextStr])
                        logger.info(f"************* idx {i} 成功")
                        flag = True
                        break

                except Exception as e:
                    count += 1
                    logger.info(f"idx {i} 第二次尝试。")
                    question += "，总结为300字以内回答。"

            if not flag:
                question = data_samples["question"][i] + "，总结为200字以内回答。"
                data = json.dumps(get_request_param(question))
                logger.info(f"\nidx: {i} 第三次尝试, question: {question}")

                # 调用接口
                response = requests.post(url=req.rag_url, data=data, headers=header, verify=False)
                text = response.text
                request_obj = json.loads(text)

                # 合并数据
                # 判断返回结果是否正确
                state_code = request_obj.get("code", 0)
                if state_code != 200 and state_code != 0:
                    res_dict = {"time": time.time(), "code": 1, "msg": f"{text}"}
                    elapse = computing_task_time(timestamp0)
                    logger.info(f"失败!, task_id:{task_id}, elapse:{elapse}s, msg:{text}")
                    if isinstance(task_dict, dict):
                        task_dict[task_id] = res_dict
                    return res_dict
                if state_code == 0:
                    answersStr = request_obj["responseData"][1]["historyPreview"][-1]["value"]
                    contextStr = \
                        request_obj["responseData"][1]["historyPreview"][-2]["value"].split("<Data>")[2].split(
                            "</Data>")[0]

                    answer_list.append(answersStr)
                    contexts_list.append([contextStr])
                    logger.info(f"************* idx {i} 成功")

        data_samples["answer"] = answer_list
        data_samples["contexts"] = contexts_list

        # 保存数据
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_samples, f)

        res_dict = {"time": time.time(), "code": 0, "msg": "任务已完成~"}
        elapse = computing_task_time(timestamp0)
        logger.info(f"已完成~, task_id:{task_id}, sample_size:{len(data_samples['answer'])}, elapse:{elapse}s")

    except Exception as e:
        res_dict = {"time": time.time(), "code": 1, "msg": f"{e}"}

        elapse = computing_task_time(timestamp0)
        logger.info(f"失败!, task_id:{task_id}, elapse:{elapse}s, msg:{e}")

    if isinstance(task_dict, dict):
        task_dict[task_id] = res_dict

    return res_dict


def computing_task_time(timestamp1, timestamp2=None):
    if not timestamp2:
        timestamp2 = time.time()
    elapse = round(abs(timestamp2 - timestamp1), 2)

    return elapse


def getRagasEvaluate(req, dataset, task_id, task_dict, logger):
    timestamp0 = time.time()
    try:
        openai_model = ChatOpenAI(
            model=req.model,
            timeout=None,
            default_headers=None,
            base_url=req.base_url)

        run_config = RunConfig()
        my_llm = LangchainLLMWrapper(openai_model, run_config)

        # 选择评估的指标
        # Ragas提供5种评估指标
        metrics = []
        if req.faithfulness:
            faithfulness.llm = my_llm  # 忠实度
            metrics.append(faithfulness)
        if req.context_recall:
            context_recall.llm = my_llm  # 上下文召回率
            metrics.append(context_recall)
        if req.context_precision:
            context_precision.llm = my_llm  # 上下文精度
            metrics.append(context_precision)
        if req.answer_relevancy:
            answer_relevancy.llm = my_llm  # 上下文相关性
            # 替换模型embedding模型
            if req.embedding_local_model_path != "":
                logger.info(f"load local embedding model {req.embedding_local_model_path}")
                embedding_model = LocalEmbedding(req.embedding_local_model_path)
            elif req.embedding_openai_model_url != "" and req.embedding_openai_model_url != "":
                logger.info(f"load remote embedding model {req.embedding_openai_model_name}")
                embedding_model = OpenAIEmbedding(req.embedding_openai_model_url, req.embedding_openai_model_name)
            else:
                logger.info(f"load base embedding model {base_embedding}")
                embedding_model = base_embedding
            answer_relevancy.embeddings = embedding_model  # 答案相关性
            metrics.append(answer_relevancy)
        if req.answer_correctness:
            answer_correctness.llm = my_llm
            # 替换模型embedding模型
            if req.embedding_local_model_path != "":
                logger.info(f"load local embedding model {req.embedding_local_model_path}")
                embedding_model = LocalEmbedding(req.embedding_local_model_path)
            elif req.embedding_openai_model_url != "" and req.embedding_openai_model_url != "":
                logger.info(f"load remote embedding model {req.embedding_openai_model_name}")
                embedding_model = OpenAIEmbedding(req.embedding_openai_model_url, req.embedding_openai_model_name)
            else:
                logger.info(f"load base embedding model {base_embedding}")
                embedding_model = base_embedding
            answer_correctness.embeddings = embedding_model
            metrics.append(answer_correctness)
        if req.answer_similarity:
            answer_similarity.llm = my_llm
            # 替换模型embedding模型
            if req.embedding_local_model_path != "":
                logger.info(f"load local embedding model {req.embedding_local_model_path}")
                embedding_model = LocalEmbedding(req.embedding_local_model_path)
            elif req.embedding_openai_model_url != "" and req.embedding_openai_model_url != "":
                logger.info(f"load remote embedding model {req.embedding_openai_model_name}")
                embedding_model = OpenAIEmbedding(req.embedding_openai_model_url, req.embedding_openai_model_name)
            else:
                logger.info(f"load base embedding model {base_embedding}")
                embedding_model = base_embedding
            answer_similarity.embeddings = embedding_model
            metrics.append(answer_similarity)
        if req.context_entity_recall:
            context_entity_recall.llm = my_llm
            metrics.append(context_entity_recall)

        result = evaluate(
            dataset,
            metrics=metrics
        )

        df = result.to_pandas()
        df = df.fillna(0.00015)
        df_columns = df.columns.tolist()

        # 平均分
        faithfulness_mean = df["faithfulness"].mean()
        context_recall_mean = df["context_recall"].mean()
        context_precision_mean = df["context_precision"].mean()
        answer_relevancy_mean = df["answer_relevancy"].mean()
        print("faithfulness mean:", df["faithfulness"].mean())
        print("context_recall mean:", df["context_recall"].mean())
        print("context_precision mean:", df["context_precision"].mean())
        print("answer_relevancy mean:", df["answer_relevancy"].mean())
        # print("context_entity_recall mean:", df["context_entity_recall"].mean())

        # 计算总分
        new_row = {'user_input': '', 'retrieved_contexts': '', 'response': '', 'reference': ''}
        count = 0
        for i in df_columns:
            if i == "faithfulness":
                new_row[i] = str(faithfulness_mean)
                count += 1
            if i == "context_recall":
                new_row[i] = str(context_recall_mean)
                count += 1
            if i == "context_precision":
                new_row[i] = str(context_precision_mean)
                count += 1
            if i == "answer_relevancy":
                new_row[i] = str(answer_relevancy_mean)
                count += 1

        new_row["Total Average Score"] = "总分：" + str((faithfulness_mean + context_recall_mean +
                                                        context_precision_mean + answer_relevancy_mean) / count)

        df = df._append(pd.Series(new_row), ignore_index=True)
        df.to_excel(os.path.join(save_path, f"{req.user_id}/result_{task_id}.xlsx"), index=False)

        res_dict = {"time": time.time(), "code": 0, "msg": "任务已完成~"}

        elapse = computing_task_time(timestamp0)
        logger.info(f"已完成~, task_id:{task_id}, sample_size:{df.shape[0]}, elapse:{elapse}s")
    except Exception as e:
        res_dict = {"time": time.time(), "code": 1, "msg": f"{e}"}

        elapse = computing_task_time(timestamp0)
        logger.info(f"失败!, task_id:{task_id}, elapse:{elapse}s, msg:{e}")

    if isinstance(task_dict, dict):
        task_dict[task_id] = res_dict

    return res_dict


def queryOmegaDict(req, omega_task_dict):
    task_id = req.task_id
    if task_id in omega_task_dict:
        omeaga_task_code = omega_task_dict[task_id]["code"]
        match omeaga_task_code:
            case 0:
                omegaMsg = "omega 任务已完成~"
                oemagaIsSuc = True
                content = {"isSuc": oemagaIsSuc, "code": omeaga_task_code, "msg": omegaMsg, "res": {}}
                logger.info(f">>> task_id:{task_id}, response:{content}")
                file = FileResponse(path=os.path.join(save_path, f"{req.user_id}/ragas_{task_id}.json"),
                                    # media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    status_code=status.HTTP_200_OK)
                return omegaMsg, oemagaIsSuc, omeaga_task_code, file
            case 1:
                omegaMsg = f"omega 任务失败! {omega_task_dict[task_id]['msg']}" if "msg" in omega_task_dict[
                    task_id] else "omega 任务失败!"
                oemagaIsSuc = False
            case 2:
                omegaMsg = "omega 任务进行中~"
                oemagaIsSuc = True
            case _:
                omegaMsg = "omega 任务异常!"
                oemagaIsSuc = False

    else:
        omegaMsg = "omega 任务不存在!"
        oemagaIsSuc = False
        omeaga_task_code = 3

    return omegaMsg, oemagaIsSuc, omeaga_task_code, ""


def ragas_load_data(req):
    if req.file_name != "":
        filePath = os.path.join(save_path, f"{req.user_id}/update_file/{req.file_name}")
    else:
        filePath = os.path.join(save_path, f"{req.user_id}/ragas_{req.task_id}.json")

    try:
        # 读取ragas数据
        with open(filePath, 'r', encoding='utf-8') as f:
            data_samples = json.load(f)

        # 检查数据是否完整
        if len(data_samples["answer"]) != len(data_samples["question"]) or len(data_samples["contexts"]) != len(
                data_samples["question"]):
            logger.error("Incomplete data, please execute the 'http://ip:port/getOmegaRag' interface first.")
            return data_samples, False, "Incomplete data, please execute the 'http://ip:port/getOmegaRag' interface first."
        return data_samples, True, ""
    except Exception as e:
        logger.info(e)
        return "", False, e



if __name__ == '__main__':
    path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
    print(path)
