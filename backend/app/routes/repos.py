"""Repository routes."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.github_oauth import get_github_user_repos
from app.db.base import get_db
from app.db.models import Repository
from app.routes.auth import get_current_user

router = APIRouter()


class RegisterRepoRequest(BaseModel):
    """Request body for registering a repository."""

    full_name: str
    html_url: str
    default_branch: str = "main"
    visibility: str = "public"
    provider: str = "github"


@router.get("/search")
async def search_repos(request: Request, q: Optional[str] = None):
    """Search GitHub repositories available to the authenticated user."""
    user = get_current_user(request)
    access_token = user.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="No GitHub access token")

    repos = await get_github_user_repos(access_token)

    if q:
        q_lower = q.lower()
        repos = [
            repo
            for repo in repos
            if q_lower in (repo.get("full_name") or "").lower()
            or q_lower in (repo.get("description") or "").lower()
        ]

    return {
        "repos": [
            {
                "full_name": repo.get("full_name"),
                "html_url": repo.get("html_url"),
                "default_branch": repo.get("default_branch") or "main",
                "visibility": "private" if repo.get("private") else "public",
            }
            for repo in repos
        ]
    }


@router.get("/")
async def list_repos(request: Request, db: AsyncSession = Depends(get_db)):
    """List all registered repositories from the database."""
    _ = get_current_user(request)

    result = await db.execute(select(Repository).order_by(Repository.created_at.desc()))
    repositories = result.scalars().all()

    return {
        "repositories": [
            {
                "id": str(repo.id),
                "full_name": repo.full_name,
                "html_url": repo.html_url,
                "default_branch": repo.default_branch,
                "visibility": repo.visibility,
                "provider": repo.provider,
                "owner": repo.owner,
                "last_scanned_at": repo.last_scanned_at.isoformat() if repo.last_scanned_at else None,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
            }
            for repo in repositories
        ]
    }


@router.post("/register")
async def register_repo(
    payload: RegisterRepoRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a repository in the database for future scans."""
    _ = get_current_user(request)

    full_name = payload.full_name.strip()
    if "/" not in full_name:
        raise HTTPException(status_code=400, detail="full_name must be in 'owner/repo' format")

    owner = full_name.split("/", 1)[0]

    existing_result = await db.execute(select(Repository).where(Repository.full_name == full_name))
    existing_repo = existing_result.scalar_one_or_none()
    if existing_repo:
        return {
            "repository": {
                "id": str(existing_repo.id),
                "full_name": existing_repo.full_name,
                "html_url": existing_repo.html_url,
                "default_branch": existing_repo.default_branch,
                "visibility": existing_repo.visibility,
                "provider": existing_repo.provider,
                "owner": existing_repo.owner,
            },
            "created": False,
        }

    repo = Repository(
        full_name=full_name,
        html_url=payload.html_url,
        default_branch=payload.default_branch,
        visibility=payload.visibility,
        provider=payload.provider,
        owner=owner,
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)

    return {
        "repository": {
            "id": str(repo.id),
            "full_name": repo.full_name,
            "html_url": repo.html_url,
            "default_branch": repo.default_branch,
            "visibility": repo.visibility,
            "provider": repo.provider,
            "owner": repo.owner,
        },
        "created": True,
    }
