import sys
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import httpx

# Initialize the memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Base URL of the local LLM API
host = "https://ec2-35-95-160-121.us-west-2.compute.amazonaws.com/v1/"
httpx_client = httpx.Client(verify=False)

# API key for the local LLM instance (not used in this case)
OPENAI_API_KEY = "EMPTY"

# Set up the chat prompt with memory
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content="You are a chatbot having a conversation with a human."),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{human_input}")
    ]
)

# Initialize the LLM using the local instance
llm = ChatOpenAI(
    model="meta-llama/Llama-2-7b-chat-hf",  # Replace with your specific model
    temperature=0,
    base_url=host,
    timeout=None,
    api_key=OPENAI_API_KEY,  # API key placeholder, not needed for local instance
    http_client=httpx_client,
)

# Create the RunnableSequence using the `|` operator
sequence = prompt | llm

# Function to get the response from the LLM
def get_response(human_input):
    # Run the sequence with input and memory context
    result = sequence.invoke({
        "human_input": human_input,
        "chat_history": memory.load_memory_variables({})["chat_history"]
    })

    # Extract the content from the result
    if hasattr(result, 'content'):
        result_content = result.content
    elif isinstance(result, dict) and 'content' in result:
        result_content = result['content']
    elif isinstance(result, str):
        result_content = result
    else:
        raise ValueError("Unexpected response format from LLM.")

    # Update memory with the new context and output
    memory.save_context({"input": human_input}, {"output": result_content})
    
    return result_content

# Get the user's input from the command line argument
#if __name__ == "__main__":
    #user_input = sys.argv[1]
    #response = get_response(user_input)
    #print(response)
    # Main loop to keep the conversation going
if __name__ == "__main__":
    print("You can start chatting with the AI. Type 'exit' to end the conversation.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Ending the conversation.")
            break

        response = get_response(user_input)
        print(f"AI: {response}")

