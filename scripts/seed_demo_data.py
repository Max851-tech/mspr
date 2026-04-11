"""Insère quelques aliments / exercices de démo si les tables sont vides."""
import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.models.aliment import Aliment  # noqa: E402
from app.models.exercice import Exercice  # noqa: E402


async def main() -> None:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    engine = create_async_engine(db_url, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        foods_count = (await session.execute(select(func.count()).select_from(Aliment))).scalar_one()
        if foods_count == 0:
            session.add_all(
                [
                    Aliment(nom="Pomme", categorie="Fruit", calories_kcal=52, proteines_g=0.3, glucides_g=14, lipides_g=0.2),
                    Aliment(nom="Riz (cuit)", categorie="Féculent", calories_kcal=130, proteines_g=2.4, glucides_g=28, lipides_g=0.3),
                    Aliment(nom="Poulet (blanc)", categorie="Protéine", calories_kcal=165, proteines_g=31, glucides_g=0, lipides_g=3.6),
                ]
            )

        ex_count = (await session.execute(select(func.count()).select_from(Exercice))).scalar_one()
        if ex_count == 0:
            session.add_all(
                [
                    Exercice(nom="Pompes", muscle_cible="Pectoraux", equipement="Poids du corps", difficulte="DEBUTANT"),
                    Exercice(nom="Squat", muscle_cible="Quadriceps", equipement="Poids du corps", difficulte="DEBUTANT"),
                    Exercice(nom="Planche", muscle_cible="Abdominaux", equipement="Tapis", difficulte="DEBUTANT"),
                ]
            )

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
