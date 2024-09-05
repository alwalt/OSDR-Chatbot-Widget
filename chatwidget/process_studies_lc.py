from langchain_community.embeddings import HuggingFaceEmbeddings  # Use the embeddings relevant to your model
from langchain_community.document_loaders.csv_loader import CSVLoader
# import numpy as np
# import torch.nn.functional as F
from langchain_milvus import Milvus
from langchain.docstore.document import Document





# The easiest way is to use Milvus Lite where everything is stored in a local file.
# If you have a Milvus server you can use the server URI such as "http://localhost:19530".
# from pymilvus import MilvusClient


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


def create_vector_store(docs):
    docs = load_and_process_csv(file_path)

    #embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L12-v2')

    # model_name = "sentence-transformers/all-MiniLM-L12-v2"

    # The easiest way is to use Milvus Lite where everything is stored in a local file.
    # If you have a Milvus server you can use the server URI such as "http://localhost:19530".
    URI = "./milvus_osdr_lc.db"
    COLLECTION_NAME = "MilvusDocsOSDR"

    vector_store = Milvus(
        embedding_function=embeddings,
        connection_args={"uri": URI},
        auto_id=True,
        drop_old=True,
        collection_name=COLLECTION_NAME,
    )

    print(docs)

    vector_store.add_documents(documents=docs)

    # Custom Document
    osdr_q = "NASA's OSDR stands for Open Science Data Repository. "
    "It is a platform designed to store, share, and provide access "
    "to scientific data collected from various NASA missions and "
    "experiments. The goal of OSDR is to foster collaboration among "
    "scientists, researchers, and the public by making data easily "
    "accessible for analysis and further research. This aligns with "
    "NASA's commitment to open science and transparency in sharing "
    "mission data to enhance scientific discovery."

    from langchain_core.documents import Document

    # Define the OSDR FAQ document
    osdr_faq = Document(
        metadata={'source': 'FAQ', 'row': 1},
        page_content=osdr_q    
        )


    vector_store.add_documents([osdr_faq])

    print('------------------------------\n')

    results = vector_store.similarity_search(query="SERCA",k=1)
    for doc in results:
        print(f"* {doc.page_content} [{doc.metadata}]")

    # vector_store = Milvus.from_documents(
    #         docs,
    #         embedding=embeddings,
    #         collection_name=COLLECTION_NAME,
    #         connection_args={URI},
    # )

    # vector_store_saved = Milvus.from_documents(
    #     docs,
    #     embeddings,
    #     collection_name="MilvusDocsOSDR",
    #     connection_args={"uri": URI},
    # )

    # vector_store_loaded = Milvus(
    #     embeddings,
    #     connection_args={"uri": URI},
    #     collection_name="MilvusDocsOSDR",
    # )

    results = vector_store.similarity_search(
        "How does spaceflight affect SERCA?",
        k=2,
    )

    for res in results:
        print(f"* {res.page_content} [{res.metadata}]")
    
    # print(results)




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
