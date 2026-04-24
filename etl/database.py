from pathlib import Path

import psycopg2

from .secrets import get_db_config


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "sql-queries" / "schema.sql"


def get_connection():
    cfg = get_db_config()
    connect_kwargs = {}

    if cfg.get("sslmode"):
        connect_kwargs["sslmode"] = cfg["sslmode"]

    if cfg.get("sslrootcert"):
        connect_kwargs["sslrootcert"] = cfg["sslrootcert"]

    if cfg.get("database_url"):
        return psycopg2.connect(cfg["database_url"], **connect_kwargs)

    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        **connect_kwargs,
    )


def run_sql_file(sql_path: Path) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_path.read_text(encoding="utf-8"))


def setup_database() -> None:
    run_sql_file(SCHEMA_PATH)
    print(f"PostgreSQL schema applied successfully from {SCHEMA_PATH.name}.")


if __name__ == "__main__":
    setup_database()
