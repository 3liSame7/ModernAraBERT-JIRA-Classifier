import os
from pathlib import Path
from decouple import Config, RepositoryEnv
from .configuration_manager_base import ConfigurationManagerBase


class ConfigurationManager(ConfigurationManagerBase):
    _BASE_DIR = os.getenv("CONF_PATH", os.path.join(Path(__file__).resolve().parent.parent, 'resources'))
    _FILE_NAME = 'config.env'
    _FILE_PATH = os.path.join(_BASE_DIR, _FILE_NAME)

    # Load configuration from the .env file or fallback to default
    try:
        config = Config(RepositoryEnv(_FILE_PATH))
    except Exception:
        config = None

    @property
    def model_path(self) -> str:
        """
        Returns the path to the pickled ML model.
        """
        return self.config('MODEL_PATH', default=os.path.join(self._BASE_DIR, 'model.pkl'))

    @property
    def label_path(self) -> str:
        """
        Returns the path to the label encoder.
        """
        return self.config('LABEL_PATH', default=os.path.join(self._BASE_DIR, 'label_encoders.pkl'))

    @property
    def scaler_path(self) -> str:
        """
        Returns the path to the scaler.
        """
        return self.config('SCALER_PATH', default=os.path.join(self._BASE_DIR, 'scaler.pkl'))
    
    @property
    def qdrant_url(self) -> str:
        """Returns the Qdrant database URL."""
        return self.config.get("QDRANT_URL", "http://localhost:6333") if self.config else os.getenv("QDRANT_URL", "http://localhost:6333")

    @property
    def collection_name(self) -> str:
        """Returns the Qdrant collection name."""
        return self.config.get("COLLECTION_NAME", "ticket_embeddings_django") if self.config else os.getenv("COLLECTION_NAME", "ticket_embeddings_django")

    @property
    def embedding_model(self) -> str:
        """Returns the embedding model path."""
        return self.config.get("EMBEDDING_MODEL", "sentence-transformers/paraphrase-MiniLM-L3-v2") if self.config else os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-MiniLM-L3-v2")
