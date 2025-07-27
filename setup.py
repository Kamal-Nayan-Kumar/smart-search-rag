#!/usr/bin/env python3
"""
Setup script for Smart Search RAG system with Perplexity API
"""

import os
import sys
from document_processor import DocumentProcessor

def setup_project():
    """Setup the project structure and process documents"""
    print("🚀 Setting up Smart Search RAG system with Perplexity API...")
    
    # Check if API key is set
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("❌ PERPLEXITY_API_KEY not found in environment variables")
        print("Please set your Perplexity API key in .env file")
        print("Get your key from: https://www.perplexity.ai (Settings > API)")
        return False
    
    # Create necessary directories
    directories = ["./documents", "./chroma_db"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
    
    # Check for documents
    doc_processor = DocumentProcessor()
    
    if os.path.exists("./documents") and os.listdir("./documents"):
        print("📚 Processing documents...")
        try:
            documents = doc_processor.load_documents("./documents")
            print(f"📄 Loaded {len(documents)} documents")
            
            chunks = doc_processor.split_documents(documents)
            print(f"✂️ Split into {len(chunks)} chunks")
            
            vectorstore = doc_processor.create_vector_store(chunks)
            print("💾 Created vector database with local embeddings")
            
            print("✅ Setup completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            return False
    else:
        print("📋 Please add PDF documents to './documents' folder")
        print("📋 Then run this setup script again")
        return False

if __name__ == "__main__":
    success = setup_project()
    if success:
        print("\n🎉 You can now run: streamlit run main.py")
        print("💡 Using Perplexity API for enhanced analysis with real-time web search!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
