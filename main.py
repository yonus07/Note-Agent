from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent import run_agent
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Create a thread pool executor for running synchronous agent code
executor = ThreadPoolExecutor(max_workers=4)

# Request model
class AgentRequest(BaseModel):
    """Request model for agent invocation."""
    prompt: str


# Response model
class AgentResponse(BaseModel):
    """Response model for agent invocation."""
    response: str


@app.get("/")
async def home(request: Request):
    """Serve the main HTML interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/agent", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    """
    Invoke the AI agent with a prompt.
    
    The agent can read and write text files based on natural language instructions.
    This endpoint handles long-running operations without blocking the event loop.
    """
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Validate prompt length
        if len(request.prompt) > 10000:
            raise HTTPException(status_code=400, detail="Prompt is too long. Maximum length is 10000 characters.")
        
        # Run the agent in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, run_agent, request.prompt)
        
        # Validate response length (safety check)
        if len(result) > 100000:
            result = result[:100000] + "\n\n[Response truncated due to length]"
        
        return AgentResponse(response=result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invoking agent: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
