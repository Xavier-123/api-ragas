import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from server.router import utils_router, ragas_router
from tools.error_define import CustomError
from tools.log import logger

# app = FastAPI(title='ragas api', version='v1.0')
app = FastAPI(title='ragas api', version='v1.0', docs_url=None)
app.include_router(utils_router, prefix="/utils")
app.include_router(ragas_router, prefix="/ragas")


# 自定义错误
@app.exception_handler(CustomError)
async def unexcept_exception_handler(_, exc: CustomError):
    content = {"isSuc": False, "code": exc.code, "msg": str(exc), "res": {}}
    logger.error(f"{content}")

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


# 意料之外的错误
@app.exception_handler(Exception)
async def unexcept_exception_handler(_, exc: Exception):
    content = {"isSuc": False, "code": -1, "msg": str(exc), "res": {}}

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8018)
