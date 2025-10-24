# Diego Beuk's Standalone AI DJ Chatbot

A terminal-style web interface featuring an AI-powered career assistant, built with React, FastAPI, ChromaDB, and Retrieval Augmented Generation (RAG) to intelligently answer career-related questions about Diego Beuk.

## Features

- AI DJ Persona: A career-focused AI assistant with a unique DJ-inspired identity
- Terminal-Style Interface: Authentic terminal experience with command history, autocomplete, and keyboard shortcuts
- Multi-Format Document Support: Processes PDF, Markdown (.md), and text (.txt) files
- Advanced RAG Chat: Context-aware chat about Diego’s career, skills, and experience using intelligent document retrieval
- Real-Time Performance: Fast and responsive interface for natural, interactive conversation
- Animated ASCII Art: Dynamic terminal header with ASCII frame animation
- Smart Retrieval: Intelligent document chunking and vector search for accurate answers
- Career-Focused Commands: Commands tailored for career exploration, skill analysis, and profile generation

## Commands

- `help` - Show a numbered list of available commands
- `spin-profile` - Generate a recruiter-ready summary of Diego's professional journey
- `amplify <skill>` - Expand on a specific skill with examples and impact statements
- `career-analysis <job>` - Compare Diego's skills with a target job role
- `clear` - Clear the terminal
- `exit` - Exit the application

**Natural Conversation**: You can also chat naturally with Diego's AI DJ about his career, skills, projects, or any questions you have!

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key
- LangChain API key (optional, for tracing)
- pnpm (recommended package manager)

### 1. Environment Setup

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here  # Optional
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
# or using pnpm (recommended)
pnpm install
```

### 3. Run the Application

#### Option A: Run Everything Together
```bash
npm run start:all
```

#### Option B: Run Separately

Terminal 1 (Backend):
```bash
npm run start:backend
# or
python start_backend.py
```

Terminal 2 (Frontend):
```bash
npm run start:frontend
# or
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

1. **Start the application** using one of the methods above
2. **Documents are automatically ingested** on startup from the `data/` folder
3. **Chat with Diego's AI DJ**: Interact with the AI DJ via commands or natural language:
   - `spin-profile` - Get a recruiter-ready summary
   - `amplify Python` - Deep dive into specific skills
   - `career-analysis AI Developer` - Compare skills with job roles
   - Or just ask questions naturally about Diego's career and experience
4. **Explore the interface**: The terminal includes animated ASCII art and a modern terminal experience

## Project Structure

```
diego-chatbot/
├── src/                          
│   ├── components/               
│   │   ├── App.tsx              
│   │   └── AnimatedAscii.tsx    
│   ├── hooks/                    
│   │   └── useAsciiFrames.ts    
│   ├── styles/                  
│   │   ├── App.css              
│   │   └── index.css            
│   ├── assets/                  
│   └── main.tsx                 
├── backend/                      
│   ├── api_server.py            
│   ├── start_backend.py         
│   ├── chroma_db/               
│   └── utils/                   
│       └── test_documents.py    
├── data/                         
│   ├── diego_ai_profile.md      
│   └── DiegoBeukResume.pdf      
├── docs/                         
│   ├── diegobeuk-system.md      
│   ├── TODO                     
│   └── [other documentation files]
├── public/                       
│   ├── media/                   
│   │   ├── ascii_frames/        
│   │   └── [background images]  
│   └── vite.svg                 
├── scripts/                      
│   ├── start.bat                
│   └── start.sh                 
├── requirements.txt              
├── package.json                  
├── pnpm-lock.yaml                
└── start_backend.bat            
```

## API Endpoints

- `GET /api/status` - Health check endpoint
- `GET /api/db-status` - Vector database status check
- `GET /api/doc-count` - Get document count in vector store
- `POST /api/ingest` - Ingest documents from data folder
- `POST /api/chat` - Chat with Diego's AI DJ (RAG-powered responses)
- `GET /api/system-status` - Complete system status (backend, database, documents)

### Chat API Details
The `/api/chat` endpoint uses RAG (Retrieval Augmented Generation) to provide context-aware responses about Diego's career, skills, and experience. It automatically retrieves relevant document chunks and generates responses using OpenAI's GPT-4o-mini model.

## AI DJ Persona

Diego's AI DJ is designed as a **Career Scout & Talent Curator** with the following characteristics:

- **Role**: Insightful Career Navigator & Talent Curator
- **Mission**: Represent Diego with authenticity and strategic storytelling
- **Style**: Engaging, informative, approachable, and data-driven
- **Focus**: Showcase Diego's professional journey, communicate experiences clearly, and tailor content for employers and recruiters

This persona blends storytelling, technical understanding, and AI-driven insight to position Diego effectively in professional contexts.

## Technology Stack

### Frontend
- **React 19.1.1** - Modern React with latest features
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **CSS3** - Custom terminal styling with animations

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - RAG and LLM orchestration
- **ChromaDB** - Vector database for document storage
- **OpenAI GPT-4o-mini** - Language model for responses
- **OpenAI Embeddings** - Text embedding model

### Key Features
- **RAG (Retrieval Augmented Generation)** - Context-aware responses
- **Vector Search** - Intelligent document retrieval
- **Multi-format Support** - PDF, Markdown, and text documents
- **Real-time Chat** - Fast, responsive interface
- **Animated ASCII Art** - Dynamic terminal header

## Development

### Frontend Development
```bash
npm run dev
```

### Backend Development
```bash
python start_backend.py
```

### Building for Production
```bash
npm run build
```

## Troubleshooting

### Common Issues

1. **Backend not starting**: Check that all Python dependencies are installed and your `.env` file is configured
2. **Frontend can't connect to backend**: Ensure the backend is running on port 8000
3. **Documents not ingesting**: Check that the `data/` folder exists and contains supported files (PDF, MD, TXT)
4. **API key errors**: Verify your OpenAI API key is correctly set in the `.env` file
5. **ASCII animation not loading**: Check that the `public/media/ascii_frames/` directory contains the animation files
6. **Vector database issues**: The ChromaDB is automatically created in `backend/chroma_db/` - ensure write permissions

### Logs

- Backend logs: Check the terminal where you started the backend
- Frontend logs: Check the browser console (F12)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at http://localhost:8000/docs
3. Create an issue in the repository