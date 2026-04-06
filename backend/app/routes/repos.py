"""Repository routes."""
from fastapi import APIRouter
from typing import Optional

router = APIRouter()


@router.get("/search")
async def search_repos(q: Optional[str] = None):
    """Search repositories by name or owner."""
    return {"message": "Search repos endpoint (not yet implemented)", "query": q}


@router.get("/")
async def list_repos():
    """List all registered repositories."""
    return {"repositories": []}


@router.post("/register")
async def register_repo(repo_name: str):
    """Register a new repository for scanning."""
    return {"message": "Register repo endpoint (not yet implemented)", "repo": repo_name}
