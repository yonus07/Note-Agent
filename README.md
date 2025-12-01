# 📝 Note Agent

An intelligent AI-powered note-taking assistant built with FastAPI, LangChain, and Google Gemini. Manage your notes naturally using conversational prompts.

## Features

- **AI-Powered Note Management**: Use natural language to create, read, update, and delete notes
- **Secure File Operations**: All file operations are sandboxed to a dedicated `notes/` directory
- **Intelligent Agent**: Multi-tool agent that understands context and only uses tools when necessary
- **Real-time Chat Interface**: Modern, responsive web UI with streaming responses
- **Tool Calling**: Agent has access to 4 specialized tools:
  - `read_note`: Read note contents
  - `write_note`: Create or update notes
  - `list_notes`: View all available notes
  - `delete_note`: Remove notes

## Project Structure

```
DEPLOYAIAGENT/
├── agent.py              # AI agent logic with LangChain integration
├── main.py               # FastAPI server and routes
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
├── README.md             # This file
├── notes/                # User notes directory (created at runtime)
├── public/               # Static assets
├── scripts/              # Utility scripts
└── templates/
    └── index.html        # Web UI
```

## Prerequisites

- Python 3.10+
- Google API Key (for Gemini LLM)
- pip or conda for package management

## Installation

### 1. Clone/Navigate to the Project

```bash
cd DEPLOYAIAGENT
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

To get a Google API Key:
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key and paste it in the `.env` file

## Usage

### Run the Application

```bash
python main.py
```

The server will start at **http://localhost:8000**

### Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

### Example Commands

```
"Create a note called shopping.txt with milk, eggs, bread"
"List all my notes"
"Read shopping.txt"
"Update shopping.txt to add butter"
"Delete shopping.txt"
```

## API Endpoints

### GET `/`
Serves the web UI interface.

**Response**: HTML page with the chat interface

---

### POST `/agent`
Invokes the AI agent with a user prompt.

**Request Body**:
```json
{
  "prompt": "Create a note called tasks.txt with my to-do list"
}
```

**Response**:
```json
{
  "response": "Successfully wrote 45 characters to 'tasks.txt'."
}
```

**Error Response** (400):
```json
{
  "detail": "Prompt cannot be empty"
}
```

**Error Response** (500):
```json
{
  "detail": "Error invoking agent: [error details]"
}
```

## Configuration

### Model Settings
Edit `agent.py` to change the LLM model:

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",  # Change model here
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)
```

Available models:
- `gemini-2.0-flash-lite` (fast, lightweight)
- `gemini-2.0-flash` (faster, more capable)
- `gemini-1.5-pro` (most capable)

### Server Settings
Edit `main.py` to change host/port:

```python
uvicorn.run(app, host="127.0.0.1", port=8000)
```

## Security

- **Path Validation**: All filenames are validated to prevent directory traversal attacks
- **Sandboxed Directory**: All notes are stored in `notes/` directory only
- **Input Validation**: Prompts limited to 10,000 characters
- **Response Limits**: Responses capped at 100,000 characters
- **Safe Filename Rules**: Only alphanumeric characters, dots, dashes, and underscores allowed

## Architecture

### Agent Components

1. **LLM**: Google Gemini 2.0 Flash Lite (fastest inference)
2. **Tools**: Four specialized functions for note operations
3. **System Prompt**: Guides the agent to be efficient and helpful
4. **Graph**: LangGraph-based ReAct agent for reasoning

### Web Stack

- **Frontend**: HTML/CSS/JavaScript with gradient UI
- **Backend**: FastAPI with async/await support
- **Server**: Uvicorn ASGI server
- **Templates**: Jinja2 template engine

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'langchain_google_genai'`

Install the missing package:
```bash
pip install langchain-google-genai
```

### Error: `GOOGLE_API_KEY not set`

Ensure your `.env` file exists and contains:
```env
GOOGLE_API_KEY=your_key_here
```

### Server Won't Start

Check if port 8000 is already in use:
```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

Change the port in `main.py`:
```python
uvicorn.run(app, host="127.0.0.1", port=8001)  # Use 8001 instead
```

### Agent Not Responding

1. Verify your Google API key is valid
2. Check your internet connection
3. Ensure the model name is correct
4. Look for error details in the browser console

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.121.0 | Web framework |
| uvicorn | >=0.34.0 | ASGI server |
| langchain | >=1.1.0 | LLM framework |
| langgraph | >=1.0.0 | Agent graph library |
| langchain-google-genai | >=3.0.0 | Google Gemini integration |
| python-dotenv | Latest | Environment variable management |
| jinja2 | Latest | Template engine |
| pydantic | >=2.0.0 | Data validation |

## Performance Tips

1. **First Run**: The first request may be slower as dependencies are loaded
2. **Concurrency**: Up to 4 concurrent requests are supported
3. **Model Selection**: Use `gemini-2.0-flash-lite` for best speed
4. **Temperature**: Set to 0 for deterministic, faster responses

## Development

### Run Tests

```bash
pytest
```

### Code Structure

- `agent.py`: Core AI logic with tool definitions
- `main.py`: FastAPI routes and server setup
- `templates/index.html`: Web interface with real-time chat

### Extending with New Tools

Add a new tool in `agent.py`:

```python
@tool
def new_tool(param: str) -> str:
    """Tool description."""
    # Your implementation
    return result

# Add to TOOLS list
TOOLS = [read_note, write_note, list_notes, delete_note, new_tool]
```

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all environment variables are set
3. Ensure Python 3.10+ is installed
4. Check that all dependencies are installed with `pip list`

---
