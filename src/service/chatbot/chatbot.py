from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from langchain.document_loaders.base import BaseLoader
from langchain.vectorstores import VectorStore


class Chatbot:

    vector_store: VectorStore = None

    @abstractmethod
    def load_vector_store(self, persist_directory: str, docs_path: str = None, replace: bool = True) -> None:
        pass

    @abstractmethod
    def chat(self, query: str, **kwargs) -> dict[str, Any]:
        pass




