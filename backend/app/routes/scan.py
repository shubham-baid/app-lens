"""Scan routes."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.db.models import Repository, Scan, ScanStatus, ScanTarget
from app.routes.auth import get_current_user

router = APIRouter()


class ScanStartRequest(BaseModel):
    """Request body for starting a scan."""

    repo_ids: list[str]
    branch: str | None = None


@router.post("/start")
async def start_scan(
    payload: ScanStartRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create a queued scan for registered repositories."""
    user = get_current_user(request)
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user ID in token")

    if not payload.repo_ids:
        raise HTTPException(status_code=400, detail="At least one repository must be selected")

    repo_uuid_map: dict[str, UUID] = {}
    for repo_id in payload.repo_ids:
        try:
            repo_uuid_map[repo_id] = UUID(repo_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid repository ID: {repo_id}") from exc

    repositories_result = await db.execute(
        select(Repository).where(Repository.id.in_(list(repo_uuid_map.values())))
    )
    repositories = repositories_result.scalars().all()

    if len(repositories) != len(repo_uuid_map):
        found_ids = {str(repo.id) for repo in repositories}
        missing = [repo_id for repo_id in payload.repo_ids if repo_id not in found_ids]
        raise HTTPException(
            status_code=404,
            detail={"message": "One or more repositories were not found", "missing_repo_ids": missing},
        )

    scan = Scan(
        user_id=str(user_id),
        status=ScanStatus.QUEUED,
        created_at=datetime.utcnow(),
    )
    db.add(scan)
    await db.flush()

    targets: list[ScanTarget] = []
    for repo in repositories:
        target = ScanTarget(
            scan_id=scan.id,
            repo_id=repo.id,
            branch=payload.branch or repo.default_branch,
        )
        db.add(target)
        targets.append(target)

    await db.commit()

    return {
        "scan": {
            "id": str(scan.id),
            "status": scan.status.value,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
            "target_count": len(targets),
            "targets": [
                {
                    "repo_id": str(repo.id),
                    "full_name": repo.full_name,
                    "branch": payload.branch or repo.default_branch,
                }
                for repo in repositories
            ],
        }
    }


@router.get("/{scan_id}")
async def get_scan_status(
    scan_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get the status and target metadata for a scan."""
    user = get_current_user(request)
    user_id = user.get("sub")

    result = await db.execute(
        select(Scan)
        .options(selectinload(Scan.targets).selectinload(ScanTarget.repo))
        .where(Scan.id == scan_id, Scan.user_id == str(user_id))
    )
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "scan": {
            "id": str(scan.id),
            "status": scan.status.value,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
            "error": scan.error,
            "targets": [
                {
                    "id": str(target.id),
                    "repo_id": str(target.repo_id),
                    "full_name": target.repo.full_name if target.repo else None,
                    "branch": target.branch,
                    "commit_sha": target.commit_sha,
                    "subpath": target.subpath,
                }
                for target in scan.targets
            ],
        }
    }


@router.get("/")
async def list_scans(request: Request, db: AsyncSession = Depends(get_db)):
    """List scans created by the current user."""
    user = get_current_user(request)
    user_id = user.get("sub")

    result = await db.execute(
        select(Scan)
        .options(selectinload(Scan.targets).selectinload(ScanTarget.repo))
        .where(Scan.user_id == str(user_id))
        .order_by(Scan.created_at.desc())
    )
    scans = result.scalars().all()

    return {
        "scans": [
            {
                "id": str(scan.id),
                "status": scan.status.value,
                "created_at": scan.created_at.isoformat() if scan.created_at else None,
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
                "error": scan.error,
                "target_count": len(scan.targets),
                "targets": [
                    {
                        "repo_id": str(target.repo_id),
                        "full_name": target.repo.full_name if target.repo else None,
                        "branch": target.branch,
                    }
                    for target in scan.targets
                ],
            }
            for scan in scans
        ]
    }
