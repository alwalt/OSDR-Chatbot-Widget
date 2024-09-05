# vector_store.py
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus

# Global variable for the vector store
vector_store = None

# Function to initialize and load the Milvus connection and collection
def load_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L12-v2')
    URI = "./milvus_osdr_lc.db"
    COLLECTION_NAME = "MilvusDocsOSDR"

    return Milvus(
        embedding_function=embeddings,
        connection_args={"uri": URI},
        collection_name=COLLECTION_NAME,
    )

def init_vector_store():
    """Initialize the vector store if not already loaded."""
    global vector_store
    if vector_store is None:
        vector_store = load_vector_store()
        print("Milvus vector store loaded once at startup.")
    return vector_store