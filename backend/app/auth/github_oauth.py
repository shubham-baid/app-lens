"""GitHub OAuth implementation."""
import httpx
from typing import Optional
from app.config import settings


async def get_github_access_token(code: str) -> Optional[str]:
    """Exchange GitHub OAuth authorization code for an access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
    return None


async def get_github_user(access_token: str) -> Optional[dict]:
    """Fetch GitHub user information using an access token."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        if response.status_code == 200:
            return response.json()
    return None
