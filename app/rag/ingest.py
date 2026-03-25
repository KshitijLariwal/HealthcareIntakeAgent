import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore  # <-- NEW: Using the official partner package

# Load environment variables (GOOGLE_API_KEY and QDRANT_URL)
load_dotenv()

def build_vector_db():
    print("1. Loading raw medical guidelines...")
    loader = TextLoader("../../data/sample_guidelines.txt")
    documents = loader.load()

    print("2. Chunking text for optimal retrieval...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   -> Created {len(chunks)} chunks.")

    print("3. Generating embeddings using Google Gemini and pushing to Qdrant...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    # NEW: Using QdrantVectorStore instead of the deprecated Qdrant class
    QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=qdrant_url,
        prefer_grpc=False,
        collection_name="medical_guidelines"
    )
    
    print("✅ Success! The vector database is populated and ready for retrieval.")

if __name__ == "__main__":
    build_vector_db()