from __future__ import annotations
from abc import ABC, abstractmethod
from langchain.document_loaders.base import BaseLoader
from langchain.vectorstores import VectorStore


class Chatbot:

    vector_store: VectorStore = None

    @abstractmethod
    def load_vector_store(self, index_path: str = None, docs_path: str = None) -> None:
        pass

    @abstractmethod
    def chat(self):
        pass




