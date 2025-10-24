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
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4

# Load environment variables
load_dotenv()

# Configuration
DATA_PATH = "data"
CHROMA_PATH = "backend/chroma_db"

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

# Initialize the chatbot components
def initialize_chatbot():
    global llm, vector_store, retriever
    
    try:
        # Set up environment variables
        os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        
        # Initialize the LLM
        llm = ChatOpenAI(temperature=0.5, model='gpt-4o-mini')
        
        # Initialize embeddings
        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
        
        # Initialize vector store
        vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings_model,
            persist_directory=CHROMA_PATH,
        )
        
        # Set up retriever 
        # TODO: Look at modifying the k value, chunk size, and chunk overlap, and temperature value for the LLM.
        retriever = vector_store.as_retriever(search_kwargs={'k': 5})
        
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
            print(f"Warning: Could not check vectorstore status: {e}")
            print("Attempting to ingest documents...")
            ingest_documents_sync()
        
        return True
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        return False

# Synchronous document ingestion for startup
def ingest_documents_sync():
    """Synchronously ingest documents during startup"""
    try:
        if not os.path.exists(DATA_PATH):
            print(f"Warning: Data directory not found at {DATA_PATH}")
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
            print(f"Warning: Could not load PDF documents: {e}")
        
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
            print(f"Warning: Could not load text documents: {e}")
        
        # Load markdown documents as text
        try:
            md_loader = DirectoryLoader(
                DATA_PATH, 
                glob="**/*.md", 
                loader_cls=TextLoader
            )
            md_docs = md_loader.load()
            raw_documents.extend(md_docs)
            print(f"Loaded {len(md_docs)} markdown documents")
        except Exception as e:
            print(f"Warning: Could not load markdown documents: {e}")
        
        if not raw_documents:
            print("No documents found in data directory. Supported formats: PDF, MD, TXT")
            return False
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
        
        chunks = text_splitter.split_documents(raw_documents)
        
        # Create unique IDs
        uuids = [str(uuid4()) for _ in range(len(chunks))]
        
        # Add to vector store
        vector_store.add_documents(documents=chunks, ids=uuids)
        
        print(f"Successfully ingested {len(chunks)} document chunks")
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

# Ingest documents endpoint
@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_documents():
    try:
        if not os.path.exists(DATA_PATH):
            raise HTTPException(status_code=404, detail="Data directory not found")
        
        # Load documents from multiple sources
        raw_documents = []
        
        # Load PDF documents
        try:
            pdf_loader = PyPDFDirectoryLoader(DATA_PATH)
            pdf_docs = pdf_loader.load()
            raw_documents.extend(pdf_docs)
        except Exception as e:
            print(f"Warning: Could not load PDF documents: {e}")
        
        # Load text documents
        try:
            txt_loader = DirectoryLoader(
                DATA_PATH, 
                glob="**/*.txt", 
                loader_cls=TextLoader
            )
            txt_docs = txt_loader.load()
            raw_documents.extend(txt_docs)
        except Exception as e:
            print(f"Warning: Could not load text documents: {e}")
        
        # Load markdown documents as text
        try:
            md_loader = DirectoryLoader(
                DATA_PATH, 
                glob="**/*.md", 
                loader_cls=TextLoader
            )
            md_docs = md_loader.load()
            raw_documents.extend(md_docs)
        except Exception as e:
            print(f"Warning: Could not load markdown documents: {e}")
        
        if not raw_documents:
            return IngestResponse(
                message="No documents found in data directory. Supported formats: PDF, MD, TXT",
                documents_processed=0
            )
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=25,
            length_function=len,
            is_separator_regex=False,
        )
        
        chunks = text_splitter.split_documents(raw_documents)
        
        # Create unique IDs
        uuids = [str(uuid4()) for _ in range(len(chunks))]
        
        # Add to vector store
        vector_store.add_documents(documents=chunks, ids=uuids)
        
        return IngestResponse(
            message=f"Successfully ingested {len(chunks)} document chunks",
            documents_processed=len(chunks)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting documents: {str(e)}")

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if llm is None or retriever is None:
            raise HTTPException(status_code=500, detail="Chatbot not initialized")
        
        # Retrieve relevant documents
        docs = retriever.invoke(request.message)
        
        # Combine knowledge
        knowledge = ""
        for doc in docs:
            knowledge += doc.page_content + "\n\n"
        
        # Create RAG prompt with AI DJ persona
        rag_prompt = f"""
        You are Diego Beuk's Career Scout & Talent Curator. Your role is to represent Diego with authenticity and strategic storytelling, showcasing his career, achievements, and skills in a way that inspires confidence, curiosity, and opportunity.

        Your style is: Innovative, engaging, dynamic, informative, playful, personable, approachable, data-informed, and persuasive. You blend career marketing and technical insight.

        Always represent Diego positively but objectively - no exaggerations, only confident truths. Use vivid, natural, and straight to the point language to highlight achievements and growth. Promote employability by aligning Diego's experiences with employer needs and market trends.

        Answer based solely on the knowledge provided below. Don't mention that you're using provided knowledge.

        The question: {request.message}

        The knowledge about Diego Beuk: {knowledge}
        """
        
        # Get response from LLM
        response = llm.invoke(rag_prompt)
        
        return ChatResponse(response=response.content)
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
