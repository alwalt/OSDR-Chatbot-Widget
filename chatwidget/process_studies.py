from langchain_community.embeddings import HuggingFaceEmbeddings  # Use the embeddings relevant to your model
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader

def load_and_process_csv(file_path):
    # Use CSVLoader with metadata columns specified
    loader = CSVLoader(
        file_path=file_path,
        source_column='Study',  # Use 'Study' as the identifier for each document
        metadata_columns=[
            'Study', 'Title', 'Organism','Project Type', 'Description', 'Factors', 'Assays', 'Mission', 'Experiment Platform', 'DOI'
        ],  
        # Metadata columns for context during retrieval
        csv_args={
            'delimiter': ',',
            'quotechar': '"', 
        },
        # encoding = "utf-8",
    )
    documents = loader.load()

    # print(documents)

    # # Optional: Further filter out the metadata to focus only on specific columns if needed
    # filtered_documents = []
    # for doc in documents:
    #     metadata = {key: doc.metadata.get(key, '') for key in loader.metadata_columns}
    #     filtered_documents.append(doc.copy(update={"metadata": metadata}))


    # print('**************\n')
    # print(filtered_documents[0])

    # return filtered_documents

    return documents

def create_vector_store(documents):
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')

    # Create a FAISS vector store
    vector_store = FAISS.from_documents(documents, embeddings)

    # Save the FAISS index locally
    vector_store.save_local("faiss_index")

if __name__ == "__main__":
    file_path = "osdr_study_metadata.csv"  # Ensure this is in CSV format
    docs = load_and_process_csv(file_path)
    create_vector_store(docs)
