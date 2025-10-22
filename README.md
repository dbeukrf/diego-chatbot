# Diego Chatbot Terminal

A terminal-style web interface for the Diego Chatbot, featuring document ingestion and AI-powered chat capabilities.

## Features

- 🖥️ **Terminal-style Interface**: Authentic terminal experience with command history, autocomplete, and keyboard shortcuts
- 📄 **Multi-format Document Support**: Process PDF, Word (.docx), Markdown (.md), and text (.txt) documents
- 🤖 **AI Chat**: Chat with Diego about your documents using RAG (Retrieval Augmented Generation)
- ⚡ **Real-time**: Fast, responsive interface with real-time chat capabilities
- 🎨 **Modern UI**: Clean, terminal-inspired design with syntax highlighting
- 🔍 **Smart Retrieval**: Intelligent document chunking and vector search for accurate responses

## Commands

- `help` - Show available commands
- `ingest` - Ingest documents into the database
- `chat <message>` - Chat with Diego about your documents
- `clear` - Clear the terminal
- `status` - Show system status
- `exit` - Exit the application

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key
- LangChain API key (optional, for tracing)

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
2. **Ingest documents**: Type `ingest` to process documents in the `data/` folder
3. **Chat with Diego**: Type `chat <your question>` to ask questions about your documents
4. **Check status**: Type `status` to see system information

## Project Structure

```
diego-chatbot/
├── src/                    # React frontend
│   ├── App.tsx            # Main terminal component
│   ├── App.css            # Terminal styling
│   └── index.css          # Global styles
├── data/                   # Document storage
├── docs/                   # Documentation
├── api_server.py          # FastAPI backend
├── chatbot.py             # Original Streamlit chatbot
├── ingest_database.py     # Document ingestion script
├── start_backend.py       # Backend startup script
├── requirements.txt       # Python dependencies
└── package.json          # Node.js dependencies
```

## API Endpoints

- `GET /api/status` - Health check
- `GET /api/db-status` - Database status
- `GET /api/doc-count` - Document count
- `POST /api/ingest` - Ingest documents
- `POST /api/chat` - Chat with Diego
- `GET /api/system-status` - Full system status

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
3. **Documents not ingesting**: Check that the `data/` folder exists and contains PDF files
4. **API key errors**: Verify your OpenAI API key is correctly set in the `.env` file

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