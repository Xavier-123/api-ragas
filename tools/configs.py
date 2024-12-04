import os
from tools.embedding import MyEmbedding

# 文件保存路径
save_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0] + "/file_save"
print("save_path:", save_path)

# 基础embedding模型
# base_embedding = MyEmbedding(os.path.join(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0], "models/m3e-small"))
base_embedding = os.environ.get("BASE_EMBEDDING", "models/m3e-small")

# omega rag接口信息
omegaRagUrl = "https://192.168.12.188:37778/api/v1/chat/completions"
omegaRagAuthorization2 = "Bearer eyJhbGciOiJIUzUxMiJ9.eyJsb2dpbl9hcHBfaWQiOiIxNjgxMTM4OTM2OTUyMzExODA5Iiwic3ViIjoiSW5zcHVyLUF1dGgtTWFuYWdlciIsImxvZ2luX3VpZCI6IjE2OTY0MjE2NzM0NjQ2NzIyNTgiLCJsb2dpbl9hY2NvdW50X2lkIjoiMTY0MTY0NzU0Mjc1NDQ3MTkzOCIsImlzcyI6Ikluc3B1ciIsImxvZ2luX2xvZ2lubmFtZSI6ImlhaS1hZG1pbiIsImNsaWVudF9pcCI6IjE5Mi4xNjguMTIuNzQiLCJsb2dpbl9hY2NvdW50X25hbWUiOiJBSeW5s-WPsOeuoeeQhuWRmCIsInVzZXJzX2FwcF9pZCI6Imdsb2JhbCIsImp0aSI6IjEuMCIsImxvZ2luX3VuYW1lIjoiQUnlubPlj7DnrqHnkIblkZgiLCJleHAiOjE3MzIzNDQxNjEsIm5iZiI6MTczMjI1Nzc2MX0.5VXCO3NA3XXJ541SxDry8UglRp3zjsW12-wuLKkVaozVWJ9HDkbr4IcV9YX_k8V9H_HY6GC51J9LlDYpdHAqQA"
omegaRagCookie = "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NmYwZDUxMDZjMjhmODYwMWZiMDI5ODIiLCJ0ZWFtSWQiOiI2NmYwYmMwYzZjMjhmODYwMWZiMDI4NDgiLCJ0bWJJZCI6IjY2ZjBkNTEwNmMyOGY4NjAxZmIwMjk4NSIsImV4cCI6MTczMjM0NTc1OSwiaWF0IjoxNzMyMjU5MzU5fQ.92f6zZvQNrXohklv6EwDsG2OYIS1liUwuTV5u6_Nolg"





