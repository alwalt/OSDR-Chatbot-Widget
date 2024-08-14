from django.urls import path
from .views.chat_api import chat_api  # Import the chat_api view from chat_api.py
from .views.pages import index_view  # Import the home view


urlpatterns = [
    path('chat/', chat_api, name='chat_api'),  # Route for chat API
    path('', index_view, name='index'),  # Serve home view at the root URL
]
