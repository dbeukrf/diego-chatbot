from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
from contextlib import asynccontextmanager
import json
import os
import asyncio


# Import the existing chatbot functionality
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFDirectoryLoader, 
    DirectoryLoader,
    TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from uuid import uuid4

# Load environment variables
load_dotenv()

# Configuration
DATA_PATH = "data"
CHROMA_PATH = "backend/chroma_db"

# RAG Configuration
RAG_CONFIG = {
    # Chunking
    "chunk_size": 1000,  # Increased from 400 for better context
    "chunk_overlap": 200,  # Increased from 100 for continuity
    
    # Embeddings
    "embedding_model": "text-embedding-3-small",  # Cost-effective choice
    
    # Retrieval
    "retrieval_k": 4,  # Reduced from 5 for more focused results
    "mmr_enabled": True,  # Enable Maximal Marginal Relevance
    "mmr_lambda": 0.5,  # Balance relevance vs diversity
    
    # Temperature settings by query type
    "temperature": {
        "factual": 0.0,  # Work, education, skills
        "conversational": 0.3,  # General chat
        "creative": 0.5,  # Hobbies, personality
    },
}

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_chatbot()
    yield
    # Shutdown (if needed)
    pass

# Initialize FastAPI app
app = FastAPI(title="Diego Chatbot API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for the chatbot
llm = None
vector_store = None
retriever = None

# Pydantic models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class IngestResponse(BaseModel):
    message: str
    documents_processed: int

class StatusResponse(BaseModel):
    status: str
    backend: bool
    database: bool
    documents: int



# Query classification helper
def classify_query_type(message: str) -> str:
    """
    Classify query into factual, conversational, or creative
    """
    message_lower = message.lower()
    
    # Factual keywords
    factual_keywords = [
        'what', 'where', 'when', 'which', 'how many', 'list',
        'experience', 'education', 'skills', 'technologies', 'projects',
        'work', 'role', 'position', 'degree', 'gpa', 'company'
    ]
    
    # Creative keywords
    creative_keywords = [
        'hobbies', 'interests', 'music', 'film', 'personality',
        'creative', 'artistic', 'passion', 'enjoy', 'like'
    ]
    
    # Check for factual
    if any(keyword in message_lower for keyword in factual_keywords):
        return 'factual'
    
    # Check for creative
    if any(keyword in message_lower for keyword in creative_keywords):
        return 'creative'
    
    # Default to conversational
    return 'conversational'

# Initialize the chatbot components
def initialize_chatbot():
    global llm, vector_store, retriever
    
    try:
        # Set up environment variables
        os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        
        # Initialize the LLM with default temperature (will be adjusted per query)
        llm = ChatOpenAI(
            temperature=RAG_CONFIG["temperature"]["conversational"],
            model='gpt-4o-mini',
            max_tokens=500,  # Concise responses
            top_p=0.9,
            frequency_penalty=0.3,  # Reduce repetition
        )
        
        # Initialize embeddings - using text-embedding-3-small for cost-effectiveness
        embeddings_model = OpenAIEmbeddings(
            model=RAG_CONFIG["embedding_model"]
        )
        
        # Initialize vector store with optimized settings
        vector_store = Chroma(
            collection_name="diego_portfolio",
            embedding_function=embeddings_model,
            persist_directory=CHROMA_PATH,
            collection_metadata={
                "hnsw:space": "cosine",  # Cosine similarity
            }
        )
        
        # Set up retriever with MMR for diversity
        if RAG_CONFIG["mmr_enabled"]:
            retriever = vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    'k': RAG_CONFIG["retrieval_k"],
                    'lambda_mult': RAG_CONFIG["mmr_lambda"],
                }
            )
        else:
            retriever = vector_store.as_retriever(
                search_kwargs={'k': RAG_CONFIG["retrieval_k"]}
            )
        
        # Check if documents are already ingested
        try:
            collection = vector_store._collection
            if collection and collection.count() > 0:
                print(f"Vectorstore already contains {collection.count()} documents. Skipping ingestion.")
            else:
                print("Vectorstore is empty. Ingesting documents...")
                # Automatically ingest documents during startup
                ingest_documents_sync()
        except Exception as e:
            print(f"Could not check vectorstore status: {e}")
            print("Attempting to ingest documents...")
            ingest_documents_sync()
        
        return True
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        return False


# Enhanced document splitter for markdown
def split_markdown_documents(documents):
    """
    Split markdown documents using header-based splitting first,
    then recursive splitting for large sections
    """

    if not documents:
        return []

    # Define headers to split on
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )
    
    all_splits = []
    for doc in documents:
        # First split by headers
        try:
            header_splits = markdown_splitter.split_text(doc.page_content)
            
            # Add metadata from original document
            for split in header_splits:
                split.metadata.update(doc.metadata)
            
            # Further split large sections with recursive splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=RAG_CONFIG["chunk_size"],
                chunk_overlap=RAG_CONFIG["chunk_overlap"],
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            
            final_splits = text_splitter.split_documents(header_splits)
            all_splits.extend(final_splits)
            
        except Exception as e:
            print(f"Markdown split fallback for {doc.metadata.get('source', 'unknown')}: {e}")
            # Fallback to recursive splitting
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=RAG_CONFIG["chunk_size"],
                chunk_overlap=RAG_CONFIG["chunk_overlap"]
            )
            all_splits.extend(text_splitter.split_documents([doc]))
    
    return all_splits


# Enhanced metadata extraction
def add_metadata(chunks, source_file):
    """
    Add rich metadata to chunks for better filtering and retrieval
    """
    # Extract category from filename
    category_map = {
        'professional_summary': 'summary',
        'work_experience': 'work',
        'projects': 'projects',
        'education_awards': 'education',
        'goals_vision': 'goals',
        'challenges': 'challenges',
        'hobbies': 'hobbies',
    }
    
    # Determine category from filename
    category = 'general'
    for key, value in category_map.items():
        if key in source_file.lower():
            category = value
            break
    
    # Add metadata to each chunk
    for chunk in chunks:
        chunk.metadata['source_file'] = source_file
        chunk.metadata['category'] = category
        
        # Add topic tags based on content
        content_lower = chunk.page_content.lower()
        topics = []
        
        # Technical topics
        if any(word in content_lower for word in ['python', 'javascript', 'java', 'react', 'fastapi']):
            topics.append('technical_skills')
        if any(word in content_lower for word in ['ai', 'agent', 'llm', 'langchain', 'rag']):
            topics.append('ai_ml')
        if any(word in content_lower for word in ['project', 'built', 'developed', 'created']):
            topics.append('projects')
        if any(word in content_lower for word in ['music', 'film', 'creative', 'artistic']):
            topics.append('creative')
        
        chunk.metadata['topics'] = ','.join(topics) if topics else 'general'
    
    return chunks


# Synchronous document ingestion for startup
def ingest_documents_sync():
    """Synchronously ingest documents during startup with optimised chunking"""
    try:
        if not os.path.exists(DATA_PATH):
            print(f"Data directory not found at {DATA_PATH}")
            return False
        
        # Load documents from multiple sources
        raw_documents = []
        
        # Load PDF documents
        try:
            pdf_loader = PyPDFDirectoryLoader(DATA_PATH)
            pdf_docs = pdf_loader.load()
            raw_documents.extend(pdf_docs)
            print(f"Loaded {len(pdf_docs)} PDF documents")
        except Exception as e:
            print(f"Could not load PDF documents: {e}")
        
        # Load text documents
        try:
            txt_loader = DirectoryLoader(
                DATA_PATH, 
                glob="**/*.txt", 
                loader_cls=TextLoader
            )
            txt_docs = txt_loader.load()
            raw_documents.extend(txt_docs)
            print(f"Loaded {len(txt_docs)} text documents")
        except Exception as e:
            print(f"Could not load text documents: {e}")
        
        # Load markdown documents as text
        markdown_docs = []
        try:
            
            md_loader = DirectoryLoader(
                DATA_PATH, 
                glob="**/*.md", 
                loader_cls=lambda path: TextLoader(path, encoding="utf-8")
            )
            markdown_docs = md_loader.load()
            raw_documents.extend(markdown_docs)
            print(f"Loaded {len(markdown_docs)} markdown documents")
        except Exception as e:
            print(f"Could not load markdown documents: {e}")
        
        if not raw_documents:
            print("No documents found in data directory. Supported formats: PDF, MD, TXT")
            return False
        
        
        # Split markdown documents with header-aware splitting
        all_chunks = []
        
        if markdown_docs:
            print("Splitting markdown documents with header awareness...")
            md_chunks = split_markdown_documents(markdown_docs)
            
            # Add metadata to markdown chunks
            for chunk in md_chunks:
                source = chunk.metadata.get('source', 'unknown')
                chunk_with_meta = add_metadata([chunk], source)
                all_chunks.extend(chunk_with_meta)
        
        # Split other documents with recursive splitter
        if raw_documents:
            print("Splitting PDF/text documents...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=RAG_CONFIG["chunk_size"],
                chunk_overlap=RAG_CONFIG["chunk_overlap"],
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            
            other_chunks = text_splitter.split_documents(raw_documents)
            
            # Add metadata
            for chunk in other_chunks:
                source = chunk.metadata.get('source', 'unknown')
                chunk_with_meta = add_metadata([chunk], source)
                all_chunks.extend(chunk_with_meta)
        
        # Create unique IDs
        uuids = [str(uuid4()) for _ in range(len(all_chunks))]
        
        # Add to vector store
        vector_store.add_documents(documents=all_chunks, ids=uuids)
        
        print(f"Successfully ingested {len(all_chunks)} document chunks")
        
        # Print category distribution
        categories = {}
        for chunk in all_chunks:
            cat = chunk.metadata.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nCategory distribution:")
        for cat, count in categories.items():
            print(f"  - {cat}: {count} chunks")
        
        return True
        
    except Exception as e:
        print(f"Error ingesting documents: {e}")
        return False

# Health check endpoint
@app.get("/api/status")
async def health_check():
    return {"status": "ok", "backend": True}

# Database status endpoint
@app.get("/api/db-status")
async def database_status():
    try:
        if vector_store is None:
            return {"status": "error", "database": False}
        
        # Try to get collection info
        collection = vector_store._collection
        if collection:
            return {"status": "ok", "database": True}
        else:
            return {"status": "error", "database": False}
    except Exception as e:
        return {"status": "error", "database": False, "error": str(e)}

# Document count endpoint
@app.get("/api/doc-count")
async def document_count():
    try:
        if vector_store is None:
            return {"count": 0}
        
        collection = vector_store._collection
        if collection:
            count = collection.count()
            return {"count": count}
        else:
            return {"count": 0}
    except Exception as e:
        return {"count": 0, "error": str(e)}

# Ingest documents endpoint (same logic as sync version)
@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_documents():
    try:
        success = ingest_documents_sync()
        
        if success:
            collection = vector_store._collection
            count = collection.count() if collection else 0
            
            return IngestResponse(
                message=f"Successfully ingested documents",
                documents_processed=count
            )
        else:
            return IngestResponse(
                message="Failed to ingest documents",
                documents_processed=0
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting documents: {str(e)}")

# Chat endpoint with dynamic temperature based on query type
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if llm is None or retriever is None:
            raise HTTPException(status_code=500, detail="Chatbot not initialized")
        
        # Classify query type if not provided
        query_type = request.query_type
        if not query_type or query_type not in ['factual', 'conversational', 'creative']:
            query_type = classify_query_type(request.message)
        
        # Retrieve relevant documents
        docs = retriever.invoke(request.message)
        
        # Combine knowledge with source tracking
        knowledge = ""
        sources = []
        for doc in docs:
            knowledge += doc.page_content + "\n\n"
            source = doc.metadata.get('source_file', 'Unknown')
            if source not in sources:
                sources.append(source)
        
        # Get temperature based on query type
        temperature = RAG_CONFIG["temperature"].get(query_type, 0.3)
        
        # Create LLM with appropriate temperature
        dynamic_llm = ChatOpenAI(
            temperature=temperature,
            model='gpt-4o-mini',
            max_tokens=500,
            top_p=0.9,
            frequency_penalty=0.3,
        )
        
        # Create RAG prompt with AI DJ persona
        rag_prompt =f"""You are Diego Beuk's Career Scout & Talent Curator.
        Your role is to represent Diego with authenticity and strategic storytelling, showcasing his career, achievements, and skills in a way that inspires confidence, curiosity, and opportunity.

        Your style is: Innovative, engaging, dynamic, informative, playful, personable, approachable, data-informed, and persuasive. You blend career marketing and technical insight.

        Guidelines:
        - Always represent Diego positively but objectively - no exaggerations, only confident truths
        - Use vivid, natural, and straight-to-the-point language
        - Highlight achievements and growth that align with employer needs
        - Answer based SOLELY on the knowledge provided below about Diego Beuk
        - Don't mention that you're using provided knowledge
        - If information isn't in the knowledge base, say so honestly
        - Keep responses focused and relevant to the question

        Query type: {query_type}

        The question: {request.message}

        Knowledge about Diego Beuk:
        {knowledge}

        Your response:"""
        
        # Get response from LLM
        response = dynamic_llm.invoke(rag_prompt)
        
        return ChatResponse(
            response=response.content,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


# System status endpoint
@app.get("/api/system-status", response_model=StatusResponse)
async def system_status():
    try:
        backend_status = True
        database_status = False
        doc_count = 0
        
        # Check database status
        if vector_store is not None:
            try:
                collection = vector_store._collection
                if collection:
                    database_status = True
                    doc_count = collection.count()
            except:
                pass
        
        return StatusResponse(
            status="ok",
            backend=backend_status,
            database=database_status,
            documents=doc_count
        )
        
    except Exception as e:
        return StatusResponse(
            status="error",
            backend=False,
            database=False,
            documents=0
        )


# Configuration endpoint (for debugging)
@app.get("/api/config")
async def get_config():
    """Return current RAG configuration"""
    return {
        "rag_config": RAG_CONFIG,
        "llm_model": "gpt-4o-mini",
        "embedding_model": RAG_CONFIG["embedding_model"],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
