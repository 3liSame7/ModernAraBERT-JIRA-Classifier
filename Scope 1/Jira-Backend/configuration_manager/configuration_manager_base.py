from abc import ABC, abstractmethod
from .singleton import SingletonABC

class ConfigurationManagerBase(ABC, metaclass=SingletonABC):
    @property
    @abstractmethod
    def qdrant_url(self) -> str:
        """Returns the Qdrant URL."""
        pass

    @property
    @abstractmethod
    def collection_name(self) -> str:
        """Returns the Qdrant collection name."""
        pass

    @property
    @abstractmethod
    def embedding_model(self) -> str:
        """Returns the embedding model name/path."""
        pass
