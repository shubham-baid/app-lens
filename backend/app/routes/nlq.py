"""Natural language query routes."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/ask")
async def ask_nlq(repo_id: str, question: str):
    """Ask a natural language question about a repository."""
    return {
        "message": "NLQ endpoint (not yet implemented)",
        "repo_id": repo_id,
        "question": question,
    }
