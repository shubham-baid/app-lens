"""Service graph routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{repo_id}")
async def get_service_graph(repo_id: str):
    """Get the service dependency graph for a repository."""
    return {
        "message": "Get service graph endpoint (not yet implemented)",
        "repo_id": repo_id,
    }


@router.post("/{repo_id}/refresh")
async def refresh_graph(repo_id: str):
    """Recompute the service graph for a repository."""
    return {
        "message": "Refresh graph endpoint (not yet implemented)",
        "repo_id": repo_id,
    }


@router.get("/{repo_id}/stats")
async def get_graph_stats(repo_id: str):
    """Get graph statistics for a repository."""
    return {
        "message": "Get graph stats endpoint (not yet implemented)",
        "repo_id": repo_id,
    }
