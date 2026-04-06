"""Scan routes."""
from fastapi import APIRouter
from typing import Optional

router = APIRouter()


@router.post("/start")
async def start_scan(repo_id: str, branch: Optional[str] = None):
    """Start a new scan of a repository."""
    return {
        "message": "Start scan endpoint (not yet implemented)",
        "repo_id": repo_id,
        "branch": branch,
    }


@router.get("/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get status of a scan."""
    return {"message": "Get scan status endpoint (not yet implemented)", "scan_id": scan_id}


@router.get("/")
async def list_scans():
    """List all scans."""
    return {"scans": []}
