import asyncio
import os
import sys
from urllib.parse import urlparse

import aiomysql


def _parse_mysql_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in {"mysql+aiomysql", "mysql"}:
        raise ValueError(f"Unsupported DATABASE_URL scheme: {parsed.scheme}")
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 3306,
        "user": parsed.username or "root",
        "password": parsed.password or "",
        "db": (parsed.path or "/").lstrip("/") or None,
    }


async def _wait() -> int:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 2

    cfg = _parse_mysql_url(url)
    retries = int(os.getenv("DB_WAIT_RETRIES", "60"))
    delay = float(os.getenv("DB_WAIT_DELAY_SECONDS", "1"))

    for i in range(1, retries + 1):
        try:
            conn = await aiomysql.connect(
                host=cfg["host"],
                port=cfg["port"],
                user=cfg["user"],
                password=cfg["password"],
                db=cfg["db"],
            )
            conn.close()
            return 0
        except Exception as e:
            print(f"[wait_for_db] attempt {i}/{retries} failed: {e}", file=sys.stderr)
            await asyncio.sleep(delay)

    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_wait()))
