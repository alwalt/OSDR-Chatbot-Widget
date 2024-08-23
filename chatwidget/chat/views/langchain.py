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
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
# from langchain.chains import RetrievalQA
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
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


def load_vector_store():
    # Load the HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')

    # Load the FAISS vector store with the embeddings
    return FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

# def format_docs(docs):
#     formatted_texts = []
#     for doc in docs:
#         content = doc.page_content
#         # print('content:', content, '\n')
#         metadata = doc.metadata
#         # print('metadata:', metadata, '\n')
#         formatted_text = f"Study: {metadata.get('Study', '')}\nTitle: {metadata.get('Title', '')}\nOrganism: {metadata.get('Organism', '')}\nDescription: {metadata.get('Description','')}"
#         # print('formatted_text:', formatted_text, '\n')
#         print('XXXXXXXXX', metadata.get('Title', ''))
#         formatted_texts.append(formatted_text)
#     return "\n\n".join(formatted_texts)

def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # print('Received Data:', data)
            user_input = data.get('message')
            session_id = data.get('sessionId')

            if not user_input or not session_id:
                return JsonResponse({'error': 'Invalid request'}, status=400)
            
            ### Statefully manage chat history ###
            store = {}

            def get_session_history(session_id: str) -> BaseChatMessageHistory:
                if session_id not in store:
                    store[session_id] = ChatMessageHistory()
                return store[session_id]


            # # Cleanup expired sessions
            # cleanup_sessions()

            # # Initialize or retrieve memory for this session
            # if session_id not in memory_store:
            #     memory_store[session_id] = {
            #         'memory': ConversationBufferMemory(memory_key="chat_history", return_messages=True),
            #         'timestamp': time.time()
            #     }

            # session_data = memory_store[session_id]
            # session_data['timestamp'] = time.time()  # Update the last access time

            # memory = session_data['memory']

            # print(type(memory))

            # Set up the chat prompt with memory
            # prompt = ChatPromptTemplate.from_messages(
            #     [
            #         SystemMessage(content="You are a NASA assistant for question-answering tasks."),
            #         MessagesPlaceholder(variable_name="chat_history"),
            #         HumanMessagePromptTemplate.from_template("{human_input}")
            #     ]
            # )

            # Load the vector store for RAG
            vector_store = load_vector_store()
            retriever = vector_store.as_retriever()

            # Initialize the LLM using the local instance
            llm = ChatOpenAI(
                model="meta-llama/Llama-2-7b-chat-hf",
                temperature=0,
                base_url=host,
                timeout=None,
                api_key=OPENAI_API_KEY,
                http_client=httpx_client,
            )

            ### Contextualize question ###
            contextualize_q_system_prompt = """Given a chat history and the latest user question \
            which might reference context in the chat history, formulate a standalone question \
            which can be understood without the chat history. Do NOT answer the question, \
            just reformulate it if needed and otherwise return it as is."""
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
            qa_system_prompt = """You are an assistant for question-answering tasks. \
            Use the following pieces of retrieved context to answer the question. \
            If you don't know the answer, just say that you don't know. \
            Use three sentences maximum and keep the answer concise.\

            {context}"""
            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", qa_system_prompt),
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
            },  # constructs a key "abc123" in `store`.
            )["answer"]

            # print(result)
            
            # Extract the response content and ensure it's a string
            response_content = result.content if hasattr(result, 'content') else str(result)

            # # Update memory with the new interaction
            # memory.save_context({"input": user_input}, {"output": response_content})

            # Return the response content
            return JsonResponse({"response": response_content})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
