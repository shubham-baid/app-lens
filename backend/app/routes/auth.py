"""Authentication routes."""
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from jose import jwt
from app.config import settings
from app.auth.github_oauth import get_github_access_token, get_github_user

router = APIRouter()


@router.get("/github/login")
async def github_login():
    """Initiate GitHub OAuth login flow."""
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)

    # Build GitHub OAuth authorization URL
    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_oauth_redirect_uri_computed,
        "scope": "read:user repo",
        "state": state,
    }
    params_str = "&".join([f"{k}={v}" for k, v in params.items()])
    github_oauth_url = f"https://github.com/login/oauth/authorize?{params_str}"

    return RedirectResponse(url=github_oauth_url)


@router.get("/github/callback")
async def github_callback(code: str, response: Response):
    """Handle GitHub OAuth callback and issue JWT token."""
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    # Exchange code for GitHub access token
    access_token = await get_github_access_token(code)
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain GitHub access token")

    # Fetch user info from GitHub
    user = await get_github_user(access_token)
    if not user:
        raise HTTPException(status_code=400, detail="Failed to fetch GitHub user info")

    # Create JWT payload with user info and GitHub token
    jwt_payload = {
        "sub": str(user["id"]),
        "login": user["login"],
        "access_token": access_token,
        "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours),
    }
    token = jwt.encode(jwt_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    # Set authentication cookie and redirect to dashboard
    response = RedirectResponse(url=f"{settings.frontend_url}/dashboard")
    response.set_cookie(
        key="applens_token",
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.jwt_expiration_hours * 3600,
    )
    return response


def get_current_user(request: Request) -> dict:
    """Extract and validate JWT token from request cookies."""
    token = request.cookies.get("applens_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/me")
async def get_current_user_info(request: Request):
    """Get authenticated user profile from JWT token."""
    user = get_current_user(request)
    return {
        "id": user.get("sub"),
        "login": user.get("login"),
        "authenticated": True,
    }


@router.post("/logout")
async def logout(response: Response):
    """Clear authentication cookie to log out user."""
    response = Response()
    response.delete_cookie(
        key="applens_token",
        path="/",
        secure=settings.environment == "production",
        httponly=True,
        samesite="lax",
    )
    # Defensive clear for clients that may have stored a narrower path cookie.
    response.delete_cookie(
        key="applens_token",
        path="/auth",
        secure=settings.environment == "production",
        httponly=True,
        samesite="lax",
    )
    return response
