#!/usr/bin/env python3
"""
Test script to verify document loading and chatbot functionality
"""

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    PyPDFDirectoryLoader, 
    DirectoryLoader,
    TextLoader
)

# Load environment variables
load_dotenv()

DATA_PATH = "data"

def test_document_loading():
    """Test loading documents from the data folder"""
    print("Testing document loading from data folder...")
    print(f"Data path: {os.path.abspath(DATA_PATH)}")
    
    if not os.path.exists(DATA_PATH):
        print("ERROR: Data directory not found!")
        return False
    
    # List files in data directory
    files = os.listdir(DATA_PATH)
    print(f"Found {len(files)} files: {files}")
    
    raw_documents = []
    
    # Test PDF loading
    try:
        pdf_loader = PyPDFDirectoryLoader(DATA_PATH)
        pdf_docs = pdf_loader.load()
        raw_documents.extend(pdf_docs)
        print(f"SUCCESS: Loaded {len(pdf_docs)} PDF documents")
    except Exception as e:
        print(f"WARNING: Could not load PDF documents: {e}")
    
    # Test text document loading
    try:
        txt_loader = DirectoryLoader(
            DATA_PATH, 
            glob="**/*.txt", 
            loader_cls=TextLoader
        )
        txt_docs = txt_loader.load()
        raw_documents.extend(txt_docs)
        print(f"SUCCESS: Loaded {len(txt_docs)} text documents")
    except Exception as e:
        print(f"WARNING: Could not load text documents: {e}")
    
    # Test Markdown loading as text
    try:
        md_loader = DirectoryLoader(
            DATA_PATH, 
            glob="**/*.md", 
            loader_cls=TextLoader
        )
        md_docs = md_loader.load()
        raw_documents.extend(md_docs)
        print(f"SUCCESS: Loaded {len(md_docs)} Markdown documents")
    except Exception as e:
        print(f"WARNING: Could not load Markdown documents: {e}")
    
    print(f"\nTotal documents loaded: {len(raw_documents)}")
    
    if raw_documents:
        print("\nDocument previews:")
        for i, doc in enumerate(raw_documents[:3]):  # Show first 3 documents
            content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            print(f"  {i+1}. {doc.metadata.get('source', 'Unknown source')}")
            print(f"     Content: {content_preview}")
            print()
    
    return len(raw_documents) > 0

def test_environment():
    """Test environment variables"""
    print("Testing environment variables...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    langchain_key = os.getenv("LANGCHAIN_API_KEY")
    
    print(f"OpenAI API Key: {'Set' if openai_key else 'Not set'}")
    print(f"LangChain API Key: {'Set' if langchain_key else 'Not set'}")
    
    return bool(openai_key)

if __name__ == "__main__":
    print("Diego Chatbot Document Test")
    print("=" * 50)
    
    # Test environment
    env_ok = test_environment()
    print()
    
    # Test document loading
    docs_ok = test_document_loading()
    print()
    
    # Summary
    print("Test Summary:")
    print(f"  Environment: {'OK' if env_ok else 'Issues'}")
    print(f"  Documents: {'OK' if docs_ok else 'Issues'}")
    
    if env_ok and docs_ok:
        print("\nAll tests passed! The chatbot should work correctly.")
    else:
        print("\nSome issues found. Please check the configuration.")
