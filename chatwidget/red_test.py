import os
import inspect

# Use the environment variable if set, otherwise default to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
print(f"Connecting to Redis at: {REDIS_URL}")

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_redis import RedisChatMessageHistory


# Inspect the source code of the class
#print(inspect.getsource(RedisChatMessageHistory))

# Initialize RedisChatMessageHistory
history = RedisChatMessageHistory(session_id="user_123", redis_url=REDIS_URL)

# Add messages to the history
history.add_user_message("Hello, AI assistant!")
history.add_ai_message("Hello! How can I assist you today?")

# Retrieve messages
print("Chat History:")
for message in history.messages:
    print(f"{type(message).__name__}: {message.content}")
