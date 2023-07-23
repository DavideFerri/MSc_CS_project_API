from abc import ABC

from langchain.document_loaders.base import BaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, VectorStore

from src.api import S3Connector
from src.service.chatbot.loaders.s3_directory_loader import S3DirectoryLoader
from src.service.chatbot.chatbot import Chatbot


class BaseChatbot(Chatbot, ABC):

    vector_store: VectorStore = None

    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store

    def load_vector_store(self, index_path: str = None, docs_path: str = None) -> None:

        embeddings = OpenAIEmbeddings()
        if index_path:
            # load index
            db = Chroma(persist_directory=index_path, embedding_function=embeddings)
        else:
            loader = S3DirectoryLoader(prefix=docs_path)
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            texts = text_splitter.split_documents(documents)
            db = Chroma.from_documents(texts, embeddings, persist_directory=index_path)
            db.persist()
        self.vector_store = db
