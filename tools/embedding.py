from typing import List
from langchain.schema.embeddings import Embeddings
from langchain_core.runnables.config import run_in_executor
from FlagEmbedding import FlagModel
import requests
import json


class LocalEmbedding(Embeddings):

    def __init__(self, path, max_length=512, batch_size=256):
        self.model = FlagModel(path, query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：")

        # 读取配置文件
        if self.model.tokenizer.model_max_length:
            self.max_length = self.model.tokenizer.model_max_length
        else:
            self.max_length = max_length
        self.batch_size = batch_size

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode_corpus(texts, self.batch_size, self.max_length).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode_queries(text, self.batch_size, self.max_length).tolist()

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Asynchronous Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings.
        """
        return await run_in_executor(None, self.embed_documents, texts)

    async def aembed_query(self, text: str) -> list[float]:
        """Asynchronous Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """
        return await run_in_executor(None, self.embed_query, text)


class OpenAIEmbedding(Embeddings):
    def __init__(self, url, model_name):
        self.url = url
        self.model_name = model_name

    # @staticmethod
    def request_embedding(self, data: dict):
        response = requests.post(url=self.url, data=json.dumps(data))
        texts = json.loads(response.text.encode())
        return [text["embedding"] for text in texts["data"]]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        data = {
            "model": self.model_name,
            "inputs": texts
        }
        return self.request_embedding(data)
        # return self.model.encode_corpus(texts, self.batch_size, self.max_length).tolist()

    def embed_query(self, text: str) -> List[float]:
        data = {
            "model": self.model_name,
            "inputs": [text]
        }
        # return self.model.encode_queries(text, self.batch_size, self.max_length).tolist()
        return self.request_embedding(data)[0]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Asynchronous Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings.
        """
        return await run_in_executor(None, self.embed_documents, texts)

    async def aembed_query(self, text: str) -> list[float]:
        """Asynchronous Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """
        return await run_in_executor(None, self.embed_query, text)




if __name__ == '__main__':
    # 调用本地embedding
    emb_path = "F:\inspur\EMBEDDING_MODEL\m3e-small"
    embedding_model = LocalEmbedding(emb_path)
    print(embedding_model.embed_query("123awe"))
    # print(embedding_model.embed_documents(["sasdadasd", "123awe"]))
    res_documents = embedding_model.embed_documents(["sasdadasd", "123awe"])
    res_query = embedding_model.embed_query("sasdadasd")
    print(res_documents)
    print(res_query)


    # # Python 的函数异步调用方式
    # import asyncio
    #
    # loop = asyncio.get_event_loop()
    # tasks = [
    #     loop.create_task(embedding_model.aembed_query("sasdadasd")),
    #     loop.create_task(embedding_model.aembed_documents(["sasdadasd", "123awe"])),
    #     loop.create_task(embedding_model.aembed_documents(["sasdadasd", "123awe"])),
    # ]
    # result = loop.run_until_complete(asyncio.wait(tasks))
    # print(result)


    # url = "http://120.222.7.146:18019/v1/embeddings"
    # data = {
    #     "model": "m3e-large",
    #     "inputs": [
    #         "m3e-large", "requests"
    #     ]
    # }
    # response = requests.post(url=url, data=json.dumps(data))
    # texts = json.loads(response.text.encode())
    # res = [text["embedding"] for text in texts["data"]]
    # print(texts["data"][0]["embedding"])


    # 调用远程embedding
    obj = OpenAIEmbedding("http://120.222.7.146:18019/v1/embeddings", "m3e-large")
    res_query2 = obj.embed_query("qwer")
    res_documents2 = obj.embed_documents(["qwer", "zse"])
    print(res_documents2)
    print(res_query2)