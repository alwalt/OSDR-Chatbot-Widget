from langchain_community.embeddings import HuggingFaceEmbeddings  # Use the embeddings relevant to your model
# from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader
# from langchain_community.vectorstores import Milvus
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
import time
import torch.nn.functional as F


# The easiest way is to use Milvus Lite where everything is stored in a local file.
# If you have a Milvus server you can use the server URI such as "http://localhost:19530".
from pymilvus import MilvusClient


def load_and_process_csv(file_path):
    # Use CSVLoader with metadata columns specified
    loader = CSVLoader(
        file_path=file_path,
        source_column='Study',  # Use 'Study' as the identifier for each document
        # metadata_columns=[
        #     'Study', 'Title', 'Organism','Project Type', 'Factors', 'Assays', 'Mission', 'Experiment Platform', 'DOI'
        # ],  
        # Metadata columns for context during retrieval
        csv_args={
            'delimiter': ',',
            'quotechar': '"', 
        },
        # encoding = "utf-8",
    )
    documents = loader.load()

    return documents

    # # Set up the page_content by combining relevant metadata fields
    # processed_documents = []
    # for doc in documents:
    #     # Create a meaningful page_content by combining relevant fields
    #     content = (
    #         f"Study: {doc.metadata.get('Study', '')}\n"
    #         f"Title: {doc.metadata.get('Title', '')}\n"
    #         f"Organism: {doc.metadata.get('Organism', '')}\n"
    #         f"Project Type: {doc.metadata.get('Project Type', '')}\n"
    #         f"Description: {doc.metadata.get('Description', '')}\n"
    #         f"Factors: {doc.metadata.get('Factors', '')}\n"
    #         f"Assays: {doc.metadata.get('Assays', '')}\n"
    #         f"Mission: {doc.metadata.get('Mission', '')}\n"
    #         f"Experiment Platform: {doc.metadata.get('Experiment Platform', '')}\n"
    #         f"DOI: {doc.metadata.get('DOI', '')}"
    #     )
    #     # Create a new Document object with the combined content and existing metadata
    #     processed_documents.append(Document(page_content=content, metadata=doc.metadata))

    # return processed_documents

def create_vector_store(docs):
    #embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
    # embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L12-v2')

    model_name = "sentence-transformers/all-MiniLM-L12-v2"

    # Initialize torch settings for device-agnostic code.
    N_GPU = torch.cuda.device_count()
    DEVICE = torch.device('cuda:N_GPU' if torch.cuda.is_available() else 'cpu')

    encoder = SentenceTransformer(model_name, device=DEVICE)

    # Get the model parameters and save for later.
    EMBEDDING_DIM = encoder.get_sentence_embedding_dimension() # Size of embedding vector (384 on Mac)
    MAX_SEQ_LENGTH_IN_TOKENS = encoder.get_max_seq_length() # The maximum sequence length (in tokens) that the model can handle. (128 on Mac)

    # Inspect model parameters.
    print(f"model_name: {model_name}")
    print(f"EMBEDDING_DIM: {EMBEDDING_DIM}")
    print(f"MAX_SEQ_LENGTH: {MAX_SEQ_LENGTH_IN_TOKENS}")

    from langchain.text_splitter import RecursiveCharacterTextSplitter

    CHUNK_SIZE = 512 
    chunk_overlap = np.round(CHUNK_SIZE * 0.10, 0)
    print(f"chunk_size: {CHUNK_SIZE}, chunk_overlap: {chunk_overlap}")

    # Define the splitter.
    child_splitter = RecursiveCharacterTextSplitter(
       chunk_size=CHUNK_SIZE,
       chunk_overlap=chunk_overlap)

    # Chunk the docs.
    chunks = child_splitter.split_documents(docs)
    print(f"{len(docs)} docs split into {len(chunks)} child documents.")

    # Encoder input is doc.page_content as strings.
    list_of_strings = [doc.page_content for doc in chunks if hasattr(doc, 'page_content')] # Extracts page_content from documents and creates a list

    # Embedding inference using HuggingFace encoder.
    embeddings = torch.tensor(encoder.encode(list_of_strings)) 

    # Normalize the embeddings.
    embeddings = np.array(embeddings / np.linalg.norm(embeddings))

    # Milvus expects a list of `numpy.ndarray` of `numpy.float32` numbers.
    converted_values = list(map(np.float32, embeddings))

    # Create dict_list for Milvus insertion.
    dict_list = []
    for chunk, vector in zip(chunks, converted_values):
       # Assemble embedding vector, original text chunk, metadata.
       chunk_dict = {
           'chunk': chunk.page_content,
           'source': chunk.metadata.get('source', ""),
           'vector': vector,
       }
       dict_list.append(chunk_dict)

    # Connect a client to the Milvus Lite server.
    mc = MilvusClient("milvus_osdr.db")
    COLLECTION_NAME = "MilvusDocsOSDR"

    # Create a new collection every run 
    if mc.has_collection(COLLECTION_NAME):
        mc.drop_collection(COLLECTION_NAME)

    # Create a collection with flexible schema and AUTOINDEX.
    mc.create_collection(COLLECTION_NAME,
           EMBEDDING_DIM,
           consistency_level="Eventually",
           auto_id=True, 
           overwrite=True)

    # Insert data into the Milvus collection.
    print("Start inserting entities")
    start_time = time.time()
    mc.insert(
       COLLECTION_NAME,
       data=dict_list,
       progress_bar=True)


    end_time = time.time()
    print(f"Milvus insert time for {len(dict_list)} vectors: ", end="")
    print(f"{round(end_time - start_time, 2)} seconds")

    res = mc.describe_collection(
    collection_name=COLLECTION_NAME
    )

    print(res)
    print('before flush')

    SAMPLE_QUESTION = "How did spaceflight affect SERCA?"

    # Embed the question using the same encoder.
    query_embeddings = torch.tensor(encoder.encode(SAMPLE_QUESTION))

    # Check the shape of query_embeddings
    # print("Shape of query_embeddings:", query_embeddings.shape)
    # q_embed_shape = int(query_embeddings)

    # Normalize embeddings to unit length.
    # query_embeddings = F.normalize(query_embeddings, p=2, dim=1)
    query_embeddings = F.normalize(query_embeddings, p=2, dim=-1)

    # Convert the embeddings to list of list of np.float32.
    query_embeddings = list(map(np.float32, query_embeddings))

    query_embeddings = [query_embeddings]


    # Define metadata fields you can filter on.
    OUTPUT_FIELDS = list(dict_list[0].keys())
    print('OUTPUT FIELDS', OUTPUT_FIELDS)
    print('-------')
    OUTPUT_FIELDS.remove('vector')
    print('OUTPUT FIELDS', OUTPUT_FIELDS)


    # Define how many top-k results you want to retrieve.
    TOP_K = 2

    # Run semantic vector search using your query and the vector database.
    results = mc.search(
        COLLECTION_NAME,
        data=query_embeddings,
        output_fields=OUTPUT_FIELDS,
        limit=TOP_K,
        consistency_level="Eventually")
    
    print(results)




#     res = client.insert(
#     collection_name="demo_collection",
#     data=documents
# )

    # vector_store = Milvus(
    # embedding_function=embeddings,
    # connection_args={"uri": URI},
    # )

    # URI = "./milvus_demo.db"
    # Milvus.from_documents(  
    # documents=documents,
    # embedding=embeddings,
    # collection_name=collection_name,
    # connection_args={
    #     "uri": URI,
    # },
    # drop_old=True,  # Drop the old Milvus collection if it exists
    # )

    # Create a Milvus vector store
    # vector_store.add_documents(documents=documents)

    # # Create a FAISS vector store
    # vector_store = FAISS.from_documents(documents, embeddings)

    # Save the FAISS index locally
    # vector_store.save_local("mi_index")

if __name__ == "__main__":
    file_path = "./osdr_study_metadata.csv"  # Ensure this is in CSV format
    docs = load_and_process_csv(file_path)
    create_vector_store(docs)
