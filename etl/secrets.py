"""
Centralised secret resolution.

Priority:
  1. AWS Secrets Manager  — when AWS_SECRETS_MANAGER_SECRET_NAME is set (production / AWS)
  2. .env file / process environment  — for local development

Never falls back to hardcoded credentials.
"""

import json
import os

from dotenv import load_dotenv

# Load .env for local development; no-op if the file doesn't exist.
load_dotenv()


def _fetch_from_aws_secrets_manager(secret_name: str) -> dict:
    """Retrieve a JSON secret from AWS Secrets Manager."""
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError as exc:
        raise ImportError(
            "boto3 is required when AWS_SECRETS_MANAGER_SECRET_NAME is set. "
            "Install it with: pip install boto3"
        ) from exc

    region = os.getenv("AWS_REGION", "us-east-1")
    client = boto3.client("secretsmanager", region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as exc:
        raise RuntimeError(
            f"Failed to retrieve secret '{secret_name}' from AWS Secrets Manager: {exc}"
        ) from exc

    secret_string = response.get("SecretString")
    if not secret_string:
        raise RuntimeError(
            f"Secret '{secret_name}' in AWS Secrets Manager has no SecretString value."
        )

    try:
        return json.loads(secret_string)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Secret '{secret_name}' is not valid JSON."
        ) from exc


def _require(value: str | None, name: str) -> str:
    """Return the value or raise a clear error — never silently return None."""
    if not value:
        raise EnvironmentError(
            f"Required configuration '{name}' is missing. "
            "Set it in your .env file (local) or in AWS Secrets Manager (production)."
        )
    return value


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

_cached_secrets: dict | None = None


def get_db_config() -> dict:
    """Return database connection parameters from the appropriate secrets source."""
    global _cached_secrets

    secret_name = os.getenv("AWS_SECRETS_MANAGER_SECRET_NAME")

    if secret_name:
        # Running on AWS — fetch from Secrets Manager (result is cached per process).
        if _cached_secrets is None:
            _cached_secrets = _fetch_from_aws_secrets_manager(secret_name)
        raw = _cached_secrets
    else:
        # Local development — read from process environment (populated from .env).
        raw = {}

    return {
        "host":     _require(raw.get("DB_HOST")     or os.getenv("DB_HOST"),     "DB_HOST"),
        "port":     _require(raw.get("DB_PORT")     or os.getenv("DB_PORT"),     "DB_PORT"),
        "dbname":   _require(raw.get("DB_NAME")     or os.getenv("DB_NAME"),     "DB_NAME"),
        "user":     _require(raw.get("DB_USER")     or os.getenv("DB_USER"),     "DB_USER"),
        "password": _require(raw.get("DB_PASSWORD") or os.getenv("DB_PASSWORD"), "DB_PASSWORD"),
    }
