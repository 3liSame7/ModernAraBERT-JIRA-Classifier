from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Qdrant
from django.conf import settings

# Connect to Qdrant
client = QdrantClient(settings.QDRANT_URL)


# Collection name
COLLECTION_NAME = settings.COLLECTION_NAME


def ensure_collection_exists(client, collection_name):
    try:
        # Try to fetch collection details
        client.get_collection(collection_name)
        print(f"Collection '{collection_name}' already exists. Skipping recreation.")
    except Exception:
        # If collection doesn't exist, create it
        print(f"Collection '{collection_name}' not found. Creating...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,  # Embedding vector size
                distance="Cosine"
            )
        )

# Call the function
ensure_collection_exists(client, COLLECTION_NAME)


# Load embedding model
embedding_function = SentenceTransformerEmbeddings(model_name=settings.EMBEDDING_MODEL)

# Initialize Qdrant vector store
vectorstore = Qdrant(
    client=client,
    collection_name=COLLECTION_NAME,
    embeddings=embedding_function
)
