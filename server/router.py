from fastapi import APIRouter
from pydantic import BaseModel, Field

class RequestModel(BaseModel):
    text: str = Field("", example="")


class ResponseModel(BaseModel):
    isSuc: bool = Field(True, example=True)
    code: int = Field(0, example=0)
    msg: str = Field("Succeed~", example="Succeed~")
    res: dict = Field({}, example={})


# 路由
utils_router = APIRouter()
ragas_router = APIRouter()

# utils_api
from server.utils_api import upload_file, delete_file, retrieve_file

# ragas_api
from server.ragas_api import ragas_evaluate, getOmegaRag, query_omega_evaluate, query_ragas_evaluate

