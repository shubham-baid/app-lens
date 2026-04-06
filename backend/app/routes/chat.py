"""Chat routes."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/sessions")
async def create_chat_session(repo_id: str):
    """Create a new chat session."""
    return {"message": "Create chat session endpoint (not yet implemented)", "repo_id": repo_id}


@router.post("/{session_id}/message")
async def send_message(session_id: str, message: str):
    """Send a message in a chat session."""
    return {
        "message": "Send message endpoint (not yet implemented)",
        "session_id": session_id,
        "user_message": message,
    }


@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get chat session history."""
    return {"message": "Get session endpoint (not yet implemented)", "session_id": session_id}
