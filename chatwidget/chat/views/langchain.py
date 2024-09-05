import time
import httpx
import json
import torch
from django.http import JsonResponse
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_milvus import Milvus

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# In-memory store for session-based conversation memory with expiry
memory_store = {}
session_timeout = 3600  # Session expiry time in seconds (e.g., 1 hour)

# Base URL of the local LLM API
host = "https://ec2-35-95-160-121.us-west-2.compute.amazonaws.com/serve/v1/"
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

def get_session_history(session_id: str) -> ChatMessageHistory:
    # Cleanup expired sessions
    cleanup_sessions()

    # Initialize or retrieve memory for this session
    if session_id not in memory_store:
        memory_store[session_id] = {
            'memory': ChatMessageHistory(),  # Use ChatMessageHistory to store the conversation
            'timestamp': time.time()  # Store the timestamp for session expiration management
        }

    # Update the timestamp each time the session is accessed
    session_data = memory_store[session_id]
    session_data['timestamp'] = time.time()  # Refresh the last access time

    # Return the memory object (chat history)
    return session_data['memory']
 
# TODO: Needs to be intialized at django app boot to prevent multiple loads
# Function to initialize and load the Milvus connection and collection
def load_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L12-v2')
    URI = "./milvus_osdr_lc.db"
    COLLECTION_NAME = "MilvusDocsOSDR"

    vector_store_loaded = Milvus(
        embedding_function=embeddings,
        connection_args={"uri": URI},
        collection_name=COLLECTION_NAME,
    )
    
    return vector_store_loaded
    

def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # print('Received Data:', data)
            user_input = data.get('message')
            session_id = data.get('sessionId')

            if not user_input or not session_id:
                return JsonResponse({'error': 'Invalid request'}, status=400)
            
            # 1. Choose a model
            MODELTORUN = "meta-llama/Meta-Llama-3.1-8B-Instruct"

            # 2. Clear the GPU memory cache, you're going to need it all!
            torch.cuda.empty_cache()

            # 3. Instantiate a vLLM model instance.
            llm = ChatOpenAI(model=MODELTORUN,
                # enforce_eager=True,
                temperature=0,
                base_url=host,
                timeout=None,
                api_key=OPENAI_API_KEY,
                http_client=httpx_client,)
            

            vector_store = load_vector_store()
            retriever = vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 1, "fetch_k": 2, "lambda_mult": 0.5},
            )

            ### Contextualize question ###
            contextualize_q_system_prompt = (
                "Given a chat history and the latest user question "
                "which might reference context in the chat history, "
                "formulate a standalone question which can be understood "
                "without the chat history. Do NOT answer the question, "
                "just reformulate it if needed and otherwise return it as is."
            )
            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", contextualize_q_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            history_aware_retriever = create_history_aware_retriever(
                llm, retriever, contextualize_q_prompt
            )

            ### Answer question ###
            system_prompt = (
                "You are an assistant for question-answering tasks for NASA's Open Science Data Repository (OSDR). "
                "Use the following pieces of retrieved context to answer "
                "the question. If you don't know the answer, say that you "
                "don't know. Use three sentences maximum and keep the "
                "answer concise."
                "\n\n"
                "{context}"
            )
            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

            conversational_rag_chain = RunnableWithMessageHistory(
                rag_chain,
                get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )

            result = conversational_rag_chain.invoke(
            {"input": user_input},
            config={
                "configurable": {"session_id": session_id}
            },
            )["answer"]


            # Check memory store
            # def print_memory_store():
            #     # Use pprint to print the memory store in a readable format
            #     pprint.pprint(memory_store)

            # # Example usage in your code
            # print_memory_store()


            # Extract the response content and ensure it's a string
            response_content = result.content if hasattr(result, 'content') else str(result)

            # Return the response content
            return JsonResponse({"response": response_content})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
