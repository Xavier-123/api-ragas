import os
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File, status
from tools.error_define import BinaryDecodingError
from tools.configs import save_path
from server.ragas_api import FileRequestModel
from server.router import utils_router, ResponseModel



'''上传文件'''


@utils_router.post(path="/upload_file", summary="bytes", response_model=ResponseModel, tags=["上传文件"])
async def upload_file(
        file: UploadFile = File(description="一个二进制文件"),
        user_id: str = File(default="zhangliang01", description="用户id")
):
    # task_id = uuid.uuid4()
    # 验证文件
    pass

    # 将文件保存
    pre_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0] + f"/file_save/{user_id}/update_file"
    os.makedirs(pre_path, exist_ok=True)
    saved_path = os.path.join(pre_path, f"{file.filename}")
    print("saved_path:", saved_path)
    try:
        file_content = await file.read()  # 读取上传文件的内容
        if os.path.exists(saved_path) and os.path.getsize(saved_path) == len(file_content):
            file_status = f"文件 {file.filename} 已存在。"
            content = {"isSuc": True, "code": 0, "msg": file_status, "res": {}}
            return JSONResponse(status_code=status.HTTP_200_OK, content=content)
        with open(saved_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        raise BinaryDecodingError(e)
    content = {"isSuc": True, "code": 0, "msg": "Success ~", "res": {
        # 'task_id': f'{task_id}',
        'fileName':
        file.filename, 'user_id': user_id}}
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@utils_router.post(path="/delete_file", summary="bytes", response_model=ResponseModel, tags=["上传文件"])
async def delete_file(
        req: FileRequestModel
):
    try:
        del_count = 0
        if req.user_id == "":
            content = {"isSuc": False, "code": -1, "msg": "user_id is null", "res": {}}
            return JSONResponse(status_code=status.HTTP_200_OK, content=content)

        # 删除所有
        user_path = os.path.join(save_path, req.user_id)
        if not os.path.exists(user_path):
            os.makedirs(user_path, exist_ok=True)
            content = {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"del_file_nums": del_count}}
            return JSONResponse(status_code=status.HTTP_200_OK, content=content)

        if req.file_name == "" and req.task_id == "" and req.user_id != "":
            # os.remove(os.path.join(save_path, req.user_id))
            for root, dirs, files in os.walk(os.path.join(save_path, req.user_id)):
                for file in files:
                    os.remove(os.path.join(root, file))
                    del_count += 1
        else:
            for root, dirs, files in os.walk(os.path.join(save_path, req.user_id)):
                for file in files:
                    if req.file_name != "" and req.file_name == file:
                        os.remove(os.path.join(root, file))
                        del_count += 1
                    if req.task_id != "" and req.task_id in file:
                        os.remove(os.path.join(root, file))
                        del_count += 1
        content = {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"del_file_nums": del_count}}
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)

    except Exception as e:
        content = {"isSuc": False, "code": -1, "msg": str(e), "res": {}}
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@utils_router.post(path="/retrieve_file", summary="bytes", response_model=ResponseModel, tags=["上传文件"])
async def retrieve_file(
        req: FileRequestModel
):
    try:
        '''查询账号下所有上传的文件'''
        files = []
        user_path = os.path.join(save_path, req.user_id)
        if not os.path.exists(user_path):
            os.makedirs(user_path, exist_ok=True)
            content = {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"files": []}}
            return JSONResponse(status_code=status.HTTP_200_OK, content=content)

        for root, dirs, _files in os.walk(user_path):
            if req.update_file:
                if len(dirs) != 0:
                    continue
                else:
                    files.extend(_files)
                    break
            if len(req.task_id) == 0 and len(req.user_id) != 0:
                if len(dirs) == 0:
                    continue
                files.extend(_files)
            else:
                for file in _files:
                    if req.task_id in file:
                        files.append(file)

        content = {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"files": files}}
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)
    except Exception as e:
        content = {"isSuc": False, "code": -1, "msg": e, "res": {}}
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)



if __name__ == '__main__':
    for root, dirs, files in os.walk(os.path.join(save_path, "zhangliang01")):
        print(root, dirs, files)
        print(123)
