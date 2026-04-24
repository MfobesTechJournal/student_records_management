
"""Centralised secret resolution for local and AWS database access."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

_cached_secrets: dict[str, Any] | None = None


def _fetch_from_aws_secrets_manager(secret_name: str) -> dict[str, Any]:
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
        payload = json.loads(secret_string)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Secret '{secret_name}' is not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(
            f"Secret '{secret_name}' must be a JSON object with database keys."
        )

    return payload


def _require(value: str | None, name: str) -> str:
    if not value:
        raise EnvironmentError(
            f"Required configuration '{name}' is missing. "
            "Set it in your .env file (local) or in AWS Secrets Manager (production)."
        )
    return value


def _get_raw_config() -> dict[str, Any]:
    global _cached_secrets

    secret_name = os.getenv("AWS_SECRETS_MANAGER_SECRET_NAME")
    if not secret_name:
        return {}

    if _cached_secrets is None:
        _cached_secrets = _fetch_from_aws_secrets_manager(secret_name)

    return _cached_secrets


def _read(raw: dict[str, Any], key: str) -> str | None:
    value = raw.get(key)
    if value is None:
        value = os.getenv(key)
    if value is None:
        return None
    return str(value)


def get_db_config() -> dict[str, str]:
    """
    Return database connection parameters from the active secret source.

    Supported optional keys:
      - DATABASE_URL
      - DB_SSLMODE
      - DB_SSLROOTCERT
    """
    raw = _get_raw_config()

    database_url = _read(raw, "DATABASE_URL")
    config: dict[str, str] = {}

    if database_url:
        config["database_url"] = database_url
    else:
        config.update(
            {
                "host": _require(_read(raw, "DB_HOST"), "DB_HOST"),
                "port": _require(_read(raw, "DB_PORT"), "DB_PORT"),
                "dbname": _require(_read(raw, "DB_NAME"), "DB_NAME"),
                "user": _require(_read(raw, "DB_USER"), "DB_USER"),
                "password": _require(_read(raw, "DB_PASSWORD"), "DB_PASSWORD"),
            }
        )

    sslmode = _read(raw, "DB_SSLMODE")
    if sslmode:
        config["sslmode"] = sslmode

    sslrootcert = _read(raw, "DB_SSLROOTCERT")
    if sslrootcert:
        config["sslrootcert"] = sslrootcert

    return config
