from django.apps import AppConfig
from chat.utils.vector_store import init_vector_store 

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        """Initialize Milvus vector store once at app startup."""
        init_vector_store()  # Call the modular init function
        print("Milvus vector store initialized at startup.")