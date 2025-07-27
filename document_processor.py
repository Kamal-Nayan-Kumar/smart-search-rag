import os
from typing import List, Dict
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor with local embeddings"""
        # Using SentenceTransformers for embeddings (free alternative)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts using SentenceTransformers"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    def load_documents(self, folder_path: str) -> List[Document]:
        """Load documents from a folder containing PDFs"""
        loader = DirectoryLoader(
            folder_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        documents = loader.load()
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks for better retrieval"""
        chunks = self.text_splitter.split_documents(documents)
        
        # Add metadata for better tracking
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = i
            chunk.metadata['chunk_size'] = len(chunk.page_content)
        
        return chunks
    
    def create_vector_store(self, chunks: List[Document], persist_directory: str = "./chroma_db"):
        """Create and persist vector store with local embeddings"""
        # Extract texts for embedding
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # Get embeddings
        embeddings = self.get_embeddings(texts)
        
        # Create ChromaDB collection
        chroma_client = chromadb.PersistentClient(path=persist_directory)
        collection = chroma_client.get_or_create_collection(name="documents")
        
        # Add documents with embeddings
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=[f"doc_{i}" for i in range(len(texts))]
        )
        
        return collection
    
    def load_vector_store(self, persist_directory: str = "./chroma_db"):
        """Load existing vector store"""
        chroma_client = chromadb.PersistentClient(path=persist_directory)
        collection = chroma_client.get_or_create_collection(name="documents")
        return collection
