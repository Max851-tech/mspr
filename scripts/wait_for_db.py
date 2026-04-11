"""Attendre que MySQL accepte des connexions (utilisé au démarrage Docker)."""
import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def main() -> None:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        sys.exit(1)

    for attempt in range(1, 61):
        try:
            engine = create_async_engine(url, echo=False)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            print("Database is reachable.")
            return
        except Exception as e:  # noqa: BLE001
            print(f"Waiting for database... ({attempt}/60) {e!r}")
            await asyncio.sleep(2)

    print("Database did not become ready in time.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
