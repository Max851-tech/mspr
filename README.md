# HealthAI Coach API

Backend API pour une plateforme de suivi de sante et fitness. Projet MSPR TPRE501 (CDA-DIADS 2025-2026).

## Stack technique

| Technologie | Version | Role |
|-------------|---------|------|
| Python | 3.11+ | Langage |
| FastAPI | 0.104+ | Framework REST |
| Uvicorn | 0.24+ | Serveur ASGI |
| SQLAlchemy | 2.0+ | ORM (async) |
| aiomysql | 0.2+ | Driver MySQL async |
| Alembic | 1.12+ | Migrations BDD |
| Pydantic | 2.4+ | Validation de donnees |
| RapidFuzz | 3.14+ | Recherche floue |

## Quick start

### Pre-requis

- Python 3.11+
- MySQL 8.0+
- pip

### Installation

```bash
# Cloner le repo
git clone https://github.com/hichembenamara/mspr.git
cd mspr

# Creer un environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dependances
pip install -r requirements.txt
```

### Configuration de la base de donnees

```bash
# Creer la base MySQL
mysql -u root -p < scripts/schema.sql

# Appliquer les migrations
alembic upgrade head
```

> La connexion par defaut est `mysql+aiomysql://root:password@localhost/healthai_coach`.
> Modifier `app/database.py` pour adapter les identifiants.

### Lancement

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est accessible sur `http://localhost:8000`.

- Documentation Swagger : `http://localhost:8000/docs`
- Documentation ReDoc : `http://localhost:8000/redoc`

### Tests

```bash
pytest
```

---

## Architecture du projet

```
.
├── app/
│   ├── main.py                  # Point d'entree FastAPI
│   ├── database.py              # Connexion async MySQL
│   ├── models/                  # Modeles SQLAlchemy (18 tables)
│   │   ├── utilisateur.py       # Comptes utilisateurs
│   │   ├── organisation.py      # Multi-tenant
│   │   ├── profil_utilisateur.py
│   │   ├── objectif_utilisateur.py
│   │   ├── progression_photo.py
│   │   ├── aliment.py           # Referentiel alimentaire
│   │   ├── exercice.py          # Catalogue d'exercices
│   │   ├── seance_entrainement.py
│   │   ├── journal_alimentaire.py
│   │   ├── mesure_biometrique.py
│   │   ├── instantane_sommeil_sante.py
│   │   ├── audit_log.py         # Piste d'audit
│   │   ├── source_donnees.py    # Pipeline ETL
│   │   ├── execution_etl.py
│   │   ├── lot_donnees.py
│   │   ├── enregistrement_brut.py
│   │   ├── anomalie_donnee.py
│   │   └── staging.py           # Tables de staging ETL
│   ├── routers/                 # Endpoints API
│   │   ├── users.py             # CRUD utilisateurs
│   │   ├── foods.py             # Recherche aliments
│   │   ├── exercises.py         # Recherche exercices
│   │   └── admin/               # Endpoints admin
│   │       ├── users.py
│   │       ├── foods.py
│   │       └── exercises.py
│   ├── schemas/                 # Schemas Pydantic
│   │   ├── user.py
│   │   ├── food.py
│   │   ├── exercise.py
│   │   ├── tracking.py
│   │   ├── bulk.py
│   │   ├── common.py
│   │   ├── error.py
│   │   └── pagination.py
│   ├── services/                # Logique metier
│   │   ├── audit.py             # Journalisation des changements
│   │   ├── search.py            # Recherche floue 2 etapes
│   │   ├── tracking.py          # Objectifs et photos
│   │   └── validation.py        # Validation souple avec warnings
│   ├── dependencies/            # Injection de dependances
│   │   ├── database.py          # Session BDD
│   │   └── pagination.py        # Parametres de pagination
│   └── exceptions/              # Exceptions HTTP metier
│       ├── user.py
│       ├── food.py
│       ├── exercise.py
│       └── tracking.py
├── alembic/                     # Migrations BDD (5 versions)
├── scripts/                     # Scripts SQL
│   ├── schema.sql               # Schema complet
│   └── schema_etl_mysql.sql     # Schema ETL
├── tests/                       # Tests
├── datasets                     # URLs des datasets Kaggle
└── requirements.txt
```

---

## Endpoints API

### Endpoints publics

#### Utilisateurs (`/api/v1/users`)

| Methode | Route | Description |
|---------|-------|-------------|
| `POST` | `/` | Creer un utilisateur |
| `GET` | `/` | Lister les utilisateurs (pagine) |
| `GET` | `/{user_id}` | Obtenir un utilisateur |
| `PUT` | `/{user_id}` | Modifier un utilisateur |
| `DELETE` | `/{user_id}` | Supprimer un utilisateur |

#### Profil (`/api/v1/users/{user_id}`)

| Methode | Route | Description |
|---------|-------|-------------|
| `GET` | `/profile` | Obtenir le profil biometrique |
| `PUT` | `/profile` | Creer/modifier le profil (upsert) |

#### Objectifs (`/api/v1/users/{user_id}/objectives`)

| Methode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Lister les objectifs |
| `POST` | `/` | Creer un objectif (desactive les autres actifs) |
| `GET` | `/{objective_id}` | Obtenir un objectif |
| `PUT` | `/{objective_id}` | Modifier un objectif |

#### Photos de progression (`/api/v1/users/{user_id}/progress-photos`)

| Methode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Lister les photos (filtre par objectif possible) |
| `POST` | `/` | Ajouter une photo |
| `GET` | `/{photo_id}` | Obtenir une photo |

#### Aliments (`/api/v1/foods`)

| Methode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Rechercher/parcourir les aliments |
| `GET` | `/{food_id}` | Obtenir un aliment |

**Parametres de recherche :**
- `q` : terme de recherche (recherche floue si >= 3 caracteres)
- `category` : filtrer par categorie
- `page`, `per_page` : pagination

**Reponse :** items, total, pagination, facettes par categorie.

#### Exercices (`/api/v1/exercises`)

| Methode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Rechercher/parcourir les exercices |
| `GET` | `/{exercise_id}` | Obtenir un exercice |

**Parametres de recherche :**
- `q` : terme de recherche (recherche floue)
- `muscle_group` : filtrer par groupe musculaire
- `difficulty` : DEBUTANT, INTERMEDIAIRE, AVANCE
- `equipment` : filtrer par equipement
- `page`, `per_page` : pagination

**Reponse :** items, total, pagination, 3 facettes (groupes musculaires, difficultes, equipements).

### Endpoints admin

#### Admin utilisateurs (`/api/v1/admin/users`)

| Methode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Lister avec filtres (role, date, objectif) |
| `GET` | `/export` | Exporter en CSV |
| `GET` | `/{user_id}` | Obtenir un utilisateur (vue admin) |

#### Admin aliments (`/api/v1/admin/foods`)

| Methode | Route | Description |
|---------|-------|-------------|
| `POST` | `/` | Creer un aliment (retourne des warnings) |
| `GET` | `/{food_id}` | Obtenir (inclut les supprimes) |
| `PUT` | `/{food_id}` | Modifier (retourne des warnings) |
| `DELETE` | `/{food_id}` | Suppression logique (soft delete) |
| `POST` | `/{food_id}/restore` | Restaurer un aliment supprime |
| `POST` | `/bulk` | Operations en masse (CREATE/UPDATE/DELETE) |

#### Admin exercices (`/api/v1/admin/exercises`)

| Methode | Route | Description |
|---------|-------|-------------|
| `POST` | `/` | Creer un exercice (retourne des warnings) |
| `GET` | `/{exercise_id}` | Obtenir (inclut les supprimes) |
| `PUT` | `/{exercise_id}` | Modifier (retourne des warnings) |
| `DELETE` | `/{exercise_id}` | Suppression logique (soft delete) |
| `POST` | `/{exercise_id}/restore` | Restaurer un exercice supprime |
| `POST` | `/bulk` | Operations en masse (CREATE/UPDATE/DELETE) |

#### Utilitaires

| Methode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Informations API |
| `GET` | `/health` | Health check |

---

## Modele de donnees

### Schema relationnel

Le projet utilise **18 tables** organisees en 5 domaines :

#### Gestion des utilisateurs

```
organisation (1) ──< utilisateur (1) ──── profil_utilisateur (1)
                           │
                           ├──< objectif_utilisateur
                           │          │
                           │          └──< progression_photo
                           │
                           ├──< seance_entrainement ──> ref_type_entrainement
                           ├──< journal_alimentaire ──> aliment
                           ├──< mesure_biometrique
                           └──< instantane_sommeil_sante
```

#### Referentiels (avec soft delete et audit)

| Table | Description | Champs cles |
|-------|-------------|-------------|
| `aliment` | Catalogue alimentaire | nom, categorie, calories, proteines, glucides, lipides, fibres, sucres, sodium, cholesterol |
| `exercice` | Catalogue d'exercices | nom, partie_corps, muscle_cible, equipement, difficulte, GIFs multi-resolution |
| `ref_type_entrainement` | Types d'entrainement | type_entrainement (PK) |

#### Suivi utilisateur

| Table | Description |
|-------|-------------|
| `seance_entrainement` | Sessions d'entrainement (duree, calories, frequence) |
| `journal_alimentaire` | Journal de consommation (repas, quantites) |
| `mesure_biometrique` | Mesures (poids, IMC, frequence cardiaque) |
| `instantane_sommeil_sante` | Snapshot quotidien (sommeil, stress, pas) |

#### Pipeline ETL

```
source_donnees (1) ──< execution_etl (1) ──< anomalie_donnee
       │
       └──< lot_donnees (1) ──< enregistrement_brut
```

| Table | Description |
|-------|-------------|
| `source_donnees` | Catalogue des sources de donnees |
| `execution_etl` | Historique des executions (statut, lignes traitees) |
| `lot_donnees` | Lots de donnees avec tracabilite |
| `enregistrement_brut` | Enregistrements JSON bruts |
| `anomalie_donnee` | Journal des erreurs ETL |

#### Tables de staging

- `stg_alimentation` : staging alimentation
- `stg_salle_sport` : staging fitness
- `stg_sommeil_sante` : staging sommeil/sante

#### Audit

| Table | Description |
|-------|-------------|
| `audit_log` | Traçabilite des modifications (INSERT, UPDATE, DELETE, RESTORE) avec valeurs avant/apres en JSON |

---

## Patterns architecturaux

### Recherche floue en 2 etapes

1. **Pre-filtre SQL** : `LIKE` pour reduire le volume (max 500 candidats)
2. **Scoring Python** : RapidFuzz avec seuil de 60/100 pour le classement final

### Soft delete

Les tables `aliment` et `exercice` utilisent un champ `deleted_at` au lieu d'une suppression physique. Les endpoints publics excluent automatiquement les enregistrements supprimes ; les endpoints admin y ont acces.

### Validation souple

Au lieu de rejeter les donnees invalides, le systeme retourne des **warnings** :
- Calories manquantes ou suspectes (> 1000 kcal, negatives)
- Champs manquants sur les exercices (muscle_cible, difficulte)

Les donnees sont nettoyees (normalisation des strings) et acceptees avec les avertissements.

### Piste d'audit

Chaque modification sur les referentiels (aliments, exercices) est tracee dans `audit_log` avec :
- Action (INSERT, UPDATE, DELETE, RESTORE)
- Valeurs avant/apres en JSON
- Identifiant de l'utilisateur responsable
- Horodatage

### Operations en masse (bulk)

Les endpoints `/bulk` supportent un mix d'actions (CREATE, UPDATE, DELETE) en une seule requete, avec gestion d'erreur par item et commit transactionnel.

### Multi-tenant

L'architecture supporte le multi-organisation via `organisation_id` sur la table `utilisateur`.

---

## Migrations

Les migrations Alembic sont dans `alembic/versions/` :

| Version | Description |
|---------|-------------|
| 001 | Schema initial (18 tables + staging) |
| 002 | Champs auth sur utilisateur + objectifs/photos |
| 003 | Soft delete sur aliment/exercice + table audit_log |
| 004 | Soft delete exercice + index difficulte |
| 005 | Tables objectif_utilisateur + progression_photo |

```bash
# Appliquer toutes les migrations
alembic upgrade head

# Voir l'etat actuel
alembic current

# Generer une nouvelle migration
alembic revision --autogenerate -m "description"

# Revenir en arriere
alembic downgrade -1
```

---

## Datasets sources

Les donnees proviennent de Kaggle :

| Dataset | Usage |
|---------|-------|
| [Sleep Health and Lifestyle](https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset/) | Sommeil et sante |
| [Gym Members Exercise](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset) | Sessions d'entrainement |
| [Daily Food and Nutrition](https://www.kaggle.com/datasets/adilshamim8/daily-food-and-nutrition-dataset) | Alimentation |
| [Fitness Exercises](https://www.kaggle.com/datasets/exercisedb/fitness-exercises-dataset) | Catalogue d'exercices |

---

## Format des erreurs

Toutes les erreurs suivent un format structure :

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "Utilisateur introuvable",
    "details": {
      "user_id": 42
    }
  }
}
```

| Code | HTTP | Description |
|------|------|-------------|
| `USER_NOT_FOUND` | 404 | Utilisateur introuvable |
| `EMAIL_ALREADY_EXISTS` | 409 | Email deja utilise |
| `PROFILE_NOT_FOUND` | 404 | Profil introuvable |
| `FOOD_NOT_FOUND` | 404 | Aliment introuvable |
| `FOOD_ALREADY_EXISTS` | 409 | Aliment deja existant |
| `EXERCISE_NOT_FOUND` | 404 | Exercice introuvable |
| `EXERCISE_ALREADY_EXISTS` | 409 | Exercice deja existant |
| `OBJECTIVE_NOT_FOUND` | 404 | Objectif introuvable |
| `PROGRESS_PHOTO_NOT_FOUND` | 404 | Photo introuvable |
