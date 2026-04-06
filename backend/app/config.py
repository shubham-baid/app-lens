"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    postgres_url: str = "postgresql+asyncpg://applens:applens@localhost:5432/applens"

    # GitHub OAuth
    github_client_id: str
    github_client_secret: str
    github_oauth_redirect_uri: Optional[str] = None

    @property
    def github_oauth_redirect_uri_computed(self) -> str:
        """OAuth callback URL — explicit override takes priority, then derived from environment."""
        if self.github_oauth_redirect_uri:
            return self.github_oauth_redirect_uri
        if self.environment == "production":
            base = self.frontend_url.rstrip("/")
            return f"{base}/api/auth/github/callback"
        return "http://localhost:8000/auth/github/callback"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # OpenAI
    openai_api_key: str

    # MCP GitHub server
    mcp_github_host: str = "localhost"
    mcp_github_port: int = 8000

    # Runtime
    environment: str = "development"
    debug: bool = False
    frontend_url: str = "http://localhost:3000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()
