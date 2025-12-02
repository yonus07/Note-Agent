from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
import re
from pathlib import Path
from typing import Optional, Tuple

load_dotenv()

# Define the safe notes directory
NOTES_DIR = Path("notes")
NOTES_DIR.mkdir(exist_ok=True)  # Create the directory if it doesn't exist


def validate_filename(filename: str) -> Tuple[bool, str]:
    """
    Validate that a filename is safe.
    Only allows simple filenames like 'mynote.txt', not paths like '../../etc/passwd'.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty."
    
    # Check for path separators or navigation attempts
    if '/' in filename or '\\' in filename or '..' in filename:
        return False, "Filename cannot contain path separators (/, \\) or directory navigation (..). Use only simple filenames like 'mynote.txt'."
    
    # Check for invalid characters (basic validation)
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        return False, "Filename contains invalid characters. Only letters, numbers, dots, dashes, and underscores are allowed."
    
    # Check length
    if len(filename) > 255:
        return False, "Filename is too long. Maximum length is 255 characters."
    
    return True, ""


def get_safe_path(filename: str) -> Tuple[Optional[Path], str]:
    """
    Get a safe file path within the notes directory.
    
    Returns:
        tuple: (safe_path, error_message)
    """
    is_valid, error_msg = validate_filename(filename)
    if not is_valid:
        return None, error_msg
    
    return NOTES_DIR / filename, ""


@tool
def read_note(filename: str) -> str:
    """
    Read the contents of a note file.
    
    Args:
        filename: The name of the note file (e.g., 'mynote.txt'). 
                 Must be a simple filename without paths.
    
    Returns:
        The contents of the file or an error message.
    """
    safe_path, error_msg = get_safe_path(filename)
    if not safe_path:
        return f"Error: {error_msg}"
    
    try:
        if not safe_path.exists():
            available_notes = [f.name for f in NOTES_DIR.iterdir() if f.is_file()]
            if available_notes:
                return f"Error: Note '{filename}' not found. Available notes: {', '.join(available_notes)}"
            else:
                return f"Error: Note '{filename}' not found. The notes folder is empty."
        
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return f"Note '{filename}' exists but is empty."
        
        return f"Contents of '{filename}':\n\n{content}"
    
    except PermissionError:
        return f"Error: Permission denied. Cannot read '{filename}'."
    except UnicodeDecodeError:
        return f"Error: Cannot read '{filename}'. The file contains invalid characters."
    except Exception as e:
        return f"Error reading '{filename}': {str(e)}"


@tool
def write_note(filename: str, content: str) -> str:
    """
    Write content to a note file. This will overwrite the file if it exists.
    
    Args:
        filename: The name of the note file (e.g., 'mynote.txt'). 
                 Must be a simple filename without paths.
        content: The content to write to the file.
    
    Returns:
        A success message or an error message.
    """
    safe_path, error_msg = get_safe_path(filename)
    if not safe_path:
        return f"Error: {error_msg}"
    
    try:
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to '{filename}'."
    
    except PermissionError:
        return f"Error: Permission denied. Cannot write to '{filename}'."
    except OSError as e:
        return f"Error: Cannot write to '{filename}'. {str(e)}"
    except Exception as e:
        return f"Error writing '{filename}': {str(e)}"


@tool
def list_notes() -> str:
    """
    List all existing notes in the notes folder.
    
    Returns:
        A list of all note filenames, or a message if the folder is empty.
    """
    try:
        notes = [f.name for f in NOTES_DIR.iterdir() if f.is_file()]
        
        if not notes:
            return "No notes found. The notes folder is empty."
        
        notes.sort()  # Sort alphabetically for easier reading
        if len(notes) == 1:
            return f"Found 1 note: {notes[0]}"
        else:
            return f"Found {len(notes)} notes:\n" + "\n".join(f"  - {note}" for note in notes)
    
    except PermissionError:
        return "Error: Permission denied. Cannot access the notes folder."
    except Exception as e:
        return f"Error listing notes: {str(e)}"


@tool
def delete_note(filename: str) -> str:
    """
    Delete a note file. The file must exist in the notes folder.
    
    Args:
        filename: The name of the note file to delete (e.g., 'mynote.txt'). 
                 Must be a simple filename without paths.
    
    Returns:
        A success message or an error message.
    """
    safe_path, error_msg = get_safe_path(filename)
    if not safe_path:
        return f"Error: {error_msg}"
    
    try:
        if not safe_path.exists():
            return f"Error: Note '{filename}' does not exist. Cannot delete a file that doesn't exist."
        
        safe_path.unlink()
        return f"Successfully deleted '{filename}'."
    
    except PermissionError:
        return f"Error: Permission denied. Cannot delete '{filename}'."
    except Exception as e:
        return f"Error deleting '{filename}': {str(e)}"


TOOLS = [read_note, write_note, list_notes, delete_note]

SYSTEM_MESSAGE = (
    "You are a note-taking assistant with access to a secure notes folder. "
    "Your role is to help users manage their notes efficiently.\n\n"
    "Available tools:\n"
    "- read_note: Read the contents of a note file\n"
    "- write_note: Write or overwrite a note file\n"
    "- list_notes: List all existing notes\n"
    "- delete_note: Delete a note file\n\n"
    "Guidelines:\n"
    "1. Always think before using tools. Only use tools when necessary.\n"
    "2. If a user asks about notes, use list_notes first to see what's available.\n"
    "3. Provide clear, direct responses. Avoid unnecessary tool calls.\n"
    "4. When reading files, summarize or quote relevant parts rather than just saying 'file read'.\n"
    "5. If a user asks a simple question that doesn't require file operations, answer directly without tools.\n"
    "6. All filenames must be simple names like 'mynote.txt' - never use paths.\n"
    "7. Be concise but helpful. Users want clear information, not verbose explanations."
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)
agent = create_react_agent(llm, TOOLS, prompt=SYSTEM_MESSAGE)


def run_agent(user_input: str) -> str:
    """
    Run the agent with a user query and return the response.
    
    Args:
        user_input: The user's query or prompt.
    
    Returns:
        The agent's response as a string.
    """
    try:
        # Lower recursion limit to encourage more direct responses
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"recursion_limit": 30}  # Reduced from 50 to encourage efficiency
        )
        
        # Extract the final response
        messages = result["messages"]
        
        # Find the last AI message (should be the final response)
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content:
                return msg.content
        
        return "Error: No response generated."
    
    except Exception as e:
        return f"Error: Failed to process your request. {str(e)}"
