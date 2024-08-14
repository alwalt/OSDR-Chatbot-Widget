import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import httpx
import json

# In-memory store for session-based conversation memory with expiry
memory_store = {}
session_timeout = 3600  # Session expiry time in seconds (e.g., 1 hour)

# Base URL of the local LLM API
host = "https://ec2-35-95-160-121.us-west-2.compute.amazonaws.com/v1/"
httpx_client = httpx.Client(verify=False)

# API key for the local LLM instance (not used in this case)
OPENAI_API_KEY = "EMPTY"

def cleanup_sessions():
    """Remove expired sessions from memory."""
    current_time = time.time()
    expired_sessions = [session_id for session_id, data in memory_store.items()
                        if current_time - data['timestamp'] > session_timeout]
    for session_id in expired_sessions:
        del memory_store[session_id]

def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('Received Data:', data)

            user_input = data.get('message')
            session_id = data.get('sessionId')

            if not user_input or not session_id:
                return JsonResponse({'error': 'Invalid request'}, status=400)

            # Cleanup expired sessions
            cleanup_sessions()

            # Initialize or retrieve memory for this session
            if session_id not in memory_store:
                memory_store[session_id] = {
                    'memory': ConversationBufferMemory(memory_key="chat_history", return_messages=True),
                    'timestamp': time.time()
                }

            session_data = memory_store[session_id]
            session_data['timestamp'] = time.time()  # Update the last access time

            memory = session_data['memory']

            # Set up the chat prompt with memory
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content="You are a friendly NASA assistant named Astro."),
                    MessagesPlaceholder(variable_name="chat_history"),
                    HumanMessagePromptTemplate.from_template("{human_input}")
                ]
            )

            # Initialize the LLM using the local instance
            llm = ChatOpenAI(
                model="meta-llama/Llama-2-7b-chat-hf",
                temperature=0,
                base_url=host,
                timeout=None,
                api_key=OPENAI_API_KEY,
                http_client=httpx_client,
            )

            # Create the RunnableSequence using the `|` operator
            sequence = prompt | llm

            # Function to get the response from the LLM
            result = sequence.invoke({
                "human_input": user_input,
                "chat_history": memory.load_memory_variables({})["chat_history"]
            })

            # Extract the response content and ensure it's a string
            response_content = result.content if hasattr(result, 'content') else str(result)

            # Update memory with the new interaction
            memory.save_context({"input": user_input}, {"output": response_content})

            # Return the response content
            return JsonResponse({"response": response_content})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
