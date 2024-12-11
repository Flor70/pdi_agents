import os
import time
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = pinecone.Pinecone(
    api_key=os.getenv('PINECONE_API_KEY')
)

def process_and_store_documents():
    # Initialize embeddings with API key
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Create or get index
    index_name = "poker-docs"
    dimension = 1536  # dimensionality of text-embedding-ada-002
    
    # List all indexes
    existing_indexes = pc.list_indexes().names()
    print(f"Existing indexes: {existing_indexes}")
    
    # Create index if it doesn't exist
    if index_name not in existing_indexes:
        print("Creating new index...")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric='cosine'
        )
        # Wait for index to be ready
        while not pc.describe_index(index_name).status['ready']:
            print("Index not ready yet, waiting...")
            time.sleep(5)
    else:
        print(f"Index {index_name} already exists")
    
    print("Loading documents...")
    # Load PDF
    pdf_path = 'data/Kill Everyone_ Advanced Strategies for No-Limit Hold Em Poker Tournaments and Sit-n-Gos - PDF Room.pdf'
    pdf_loader = PyPDFLoader(pdf_path)
    pdf_docs = pdf_loader.load()
    
    # Load CSV
    csv_path = 'data/Gui Report total.csv'
    csv_loader = CSVLoader(csv_path)
    csv_docs = csv_loader.load()
    
    # Combine documents
    all_docs = pdf_docs + csv_docs
    print(f"Loaded {len(all_docs)} documents")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(all_docs)
    print(f"Split into {len(splits)} chunks")
    
    print("Storing documents in Pinecone...")
    # Store documents in Pinecone
    vectorstore = PineconeVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        index_name=index_name
    )
    print("Documents stored successfully!")
    
    return vectorstore

if __name__ == "__main__":
    process_and_store_documents()
