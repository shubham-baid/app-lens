"""Authentication routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/github/login")
async def github_login():
    """Initiate GitHub OAuth login flow."""
    return {"message": "GitHub login endpoint (not yet implemented)"}


@router.get("/github/callback")
async def github_callback(code: str):
    """Handle GitHub OAuth callback."""
    return {"message": "GitHub callback endpoint (not yet implemented)", "code": code}


@router.get("/me")
async def get_current_user():
    """Get current authenticated user info."""
    return {"message": "Get current user endpoint (not yet implemented)"}


@router.post("/logout")
async def logout():
    """Log out current user."""
    return {"message": "Logout endpoint (not yet implemented)"}
