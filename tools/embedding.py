from typing import List
from langchain.schema.embeddings import Embeddings
from langchain_core.runnables.config import run_in_executor
from FlagEmbedding import FlagModel
import os


class MyEmbedding(Embeddings):

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


if __name__ == '__main__':
    emb_path = "F:\inspur\EMBEDDING_MODEL\m3e-small"
    embedding_model = MyEmbedding(emb_path)
    # print(embedding_model.embed_query("123awe"))
    # print(embedding_model.embed_documents(["sasdadasd", "123awe"]))

    # Python 的函数异步调用方式
    import asyncio
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(embedding_model.aembed_query("sasdadasd")),
        loop.create_task(embedding_model.aembed_documents(["sasdadasd", "123awe"])),
        loop.create_task(embedding_model.aembed_documents(["sasdadasd", "123awe"])),
    ]
    result = loop.run_until_complete(asyncio.wait(tasks))
    print(result)