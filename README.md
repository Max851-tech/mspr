# HealthAI Coach — Dev rapide (XAMPP + Docker + Vite)

Objectif: **un workflow simple, rapide et sans confusion**.

## Quick start (dev)

### 1) Démarrer MySQL XAMPP

- Lance **MySQL** dans XAMPP
- phpMyAdmin: `http://127.0.0.1/phpmyadmin`

Assure-toi que la base s’appelle **`healthai_coach`**.

> Si tu as importé un dump qui crée `healthai_coaching`, soit tu **renommes** la base dans phpMyAdmin,
> soit tu mets `DATABASE_URL=.../healthai_coaching` dans `.env` et dans `docker-compose.yml`.

### 2) Configurer l’API

Copie `.env.example` → `.env` (le `.env` est **ignoré par Git**), puis configure au minimum :

```env
DATABASE_URL=mysql+aiomysql://root@localhost:3306/healthai_coach
VITE_PUBLIC_API_PORT=8001
```

### 3) Lancer l’API (Docker)

```bash
docker compose up --build
```

- **API**: `http://localhost:8001`
- **Docs**: `http://localhost:8001/docs`

### 4) Lancer le frontend (Vite)

```bash
cd frontend
npm install
npm run dev
```

Ouvre l’URL affichée (souvent `http://localhost:5173`, sinon `5174` si 5173 est déjà pris).

## Où sont stockées les données ?

- **Uniquement dans XAMPP MySQL** (port `3306`)
- Le `docker-compose.yml` **ne lance aucun MySQL**
- L’API Docker se connecte à XAMPP via **`host.docker.internal:3306`**

## Ports

- **MySQL (XAMPP)**: `3306`
- **API**: `8001` (hôte) → `8000` (conteneur)
- **Frontend (Vite)**: `5173` (fallback auto `5174`)

## Structure du projet

```
app/
  api/
    routes/              # Routers FastAPI (auth/users/foods/exercises/admin)
    dependencies/        # Dépendances FastAPI (db/auth/pagination/admin key)
  core/                  # Settings
  models/                # SQLAlchemy models
  schemas/               # Pydantic schemas
  security/              # JWT + hash passwords (bcrypt + legacy pbkdf2)
  services/              # Logique métier
alembic/                 # Migrations
frontend/                # Vite + React
docker/                  # Dockerfile
scripts/                 # Utilitaires (wait_for_db)
```

