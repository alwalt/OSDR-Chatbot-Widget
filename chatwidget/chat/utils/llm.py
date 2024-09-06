# load_llm.py
import httpx
from langchain_openai import ChatOpenAI
import torch

# Clear the GPU memory cache, you're going to need it all!
torch.cuda.empty_cache()

# Base URL of the local LLM API
host = "https://ec2-35-95-160-121.us-west-2.compute.amazonaws.com/serve/v1/"
httpx_client = httpx.Client(
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
    timeout=30.0,  
    verify=False)

# API key for the local LLM instance (not used in this case)
OPENAI_API_KEY = "EMPTY"

# Choose a model
MODELTORUN = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# Instantiate a vLLM model instance.
def load_llm():
    """Loads and returns the LLM instance."""
    llm = ChatOpenAI(
        model=MODELTORUN,
        temperature=0,
        base_url=host,
        timeout=None,
        api_key=OPENAI_API_KEY,
        http_client=httpx_client,
        streaming=True,
    )
    return llm