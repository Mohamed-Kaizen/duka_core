"""Settings for Duka Core Project."""
from typing import List, Set

from pydantic import BaseSettings
from redis import Redis


class EnvSettings(BaseSettings):
    """Base settings for Duka Core."""

    PROJECT_NAME: str = "Duka Core"

    PROJECT_DESCRIPTION: str = "A microservice that has the main logic for Duka project"

    DOCS_URL: str = "/docs"

    REDOC_URL: str = "/redoc"

    OPENAPI_URL: str = "/openapi.json"

    ALLOWED_HOSTS: List[str] = ["*"]

    CORS_ORIGINS: List[str] = ["*"]

    CORS_ALLOW_CREDENTIALS: bool = True

    CORS_ALLOW_METHODS: List[str] = ["*"]

    CORS_ALLOW_HEADERS: List[str] = ["*"]

    LOG_LEVEL: str = "DEBUG"

    HASURA_GRAPHQL_ADMIN_SECRET: str

    HASURA_ENDPOINT_URL: str

    authjwt_secret_key: str

    authjwt_denylist_enabled: bool = True

    authjwt_denylist_token_checks: Set[str] = {"access", "refresh"}

    REDIS_HOST: str

    REDIS_PORT: int

    REDIS_PASSWORD: str


SETTINGS = EnvSettings()

REDIS = Redis(host=SETTINGS.REDIS_HOST, port=SETTINGS.REDIS_PORT, password=SETTINGS.REDIS_PASSWORD, decode_responses=True)
