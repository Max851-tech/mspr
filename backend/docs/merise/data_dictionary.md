# HealthAI Coach - Dictionnaire de Données

**Projet:** HealthAI Coach Backend API
**Base de données:** MySQL 8.0+ (InnoDB, utf8mb4)
**Méthodologie:** Merise (MCD/MLD/MPD)
**Date de génération:** 2026-03-01
**Version:** 1.1

---

## Vue d'ensemble

Ce dictionnaire de données documente le schéma complet de la base de données dérivé du MPD. Il inclut toutes les tables, colonnes, types de données, contraintes et descriptions métier.

Le schéma est organisé en trois couches :
1. **Pilotage ETL** — Tables de gestion des imports et de la qualité des données
2. **Staging** — Tables temporaires pour le chargement des datasets Kaggle
3. **Métier** — Tables "clean" exposées via l'API REST

---

## Résumé des Tables

### Couche Pilotage ETL

| Table | Objectif | Dépendances |
|-------|----------|-------------|
| organisation | Organisations/tenants du système | Aucune (racine) |
| utilisateur | Comptes utilisateurs avec rôles | organisation |
| source_donnees | Catalogue des sources de données ETL | Aucune (référentiel) |
| execution_etl | Historique des exécutions ETL | source_donnees |
| lot_donnees | Lots de données importés | source_donnees, utilisateur |
| anomalie_donnee | Erreurs et avertissements ETL | execution_etl |
| enregistrement_brut | Données brutes JSON avant transformation | lot_donnees |

### Couche Staging

| Table | Objectif | Dataset Source |
|-------|----------|----------------|
| stg_alimentation | Staging alimentation | Daily Food Nutrition Dataset |
| stg_salle_sport | Staging gym/biométrie | Gym Members Exercise Tracking |
| stg_sommeil_sante | Staging sommeil/santé | Sleep Health and Lifestyle |

### Couche Métier

| Table | Objectif | Dépendances |
|-------|----------|-------------|
| aliment | Référentiel aliments avec valeurs nutritionnelles | Aucune (référentiel) |
| exercice | Catalogue d'exercices avec instructions | Aucune (référentiel) |
| ref_type_entrainement | Types d'entraînement (lookup) | Aucune (référentiel) |
| profil_utilisateur | Profil biométrique utilisateur | utilisateur |
| objectif_utilisateur | Objectifs utilisateur historisés | utilisateur |
| progression_photo | Photos de progression associées aux objectifs | utilisateur, objectif_utilisateur |
| journal_alimentaire | Journal des repas | utilisateur, aliment |
| mesure_biometrique | Mesures corporelles historiques | utilisateur |
| seance_entrainement | Sessions d'entraînement | utilisateur, ref_type_entrainement |
| instantane_sommeil_sante | Données sommeil et santé quotidiennes | utilisateur |

---

## Détail des Tables

---

### organisation

**Objectif:** Table racine multi-tenant pour isoler les données par organisation

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| organisation_id | INT | PK, AUTO_INCREMENT | Identifiant unique de l'organisation |
| nom | VARCHAR(150) | NOT NULL, UNIQUE | Nom de l'organisation |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: organisation_id
- UNIQUE: nom

---

### utilisateur

**Objectif:** Comptes utilisateurs avec authentification et gestion des rôles

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| utilisateur_id | INT | PK, AUTO_INCREMENT | Identifiant unique utilisateur |
| organisation_id | INT | NOT NULL, FK | Organisation de rattachement |
| nom_utilisateur | VARCHAR(120) | NOT NULL, UNIQUE | Nom d'utilisateur (login) |
| email | VARCHAR(255) | NULL, UNIQUE | Adresse email de connexion/contact |
| mot_de_passe_hash | VARCHAR(255) | NULL | Hash du mot de passe stocké par l'API |
| role | ENUM('ADMIN','UTILISATEUR') | NOT NULL, DEFAULT 'UTILISATEUR' | Rôle système |
| statut | ENUM('ACTIF','INACTIF') | NOT NULL, DEFAULT 'ACTIF' | Statut du compte |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: utilisateur_id
- UNIQUE: nom_utilisateur
- UNIQUE: email

**Clés étrangères:**
- fk_utilisateur_org: organisation_id → organisation(organisation_id) ON DELETE RESTRICT

---

### source_donnees

**Objectif:** Catalogue des sources de données pour le pilotage ETL

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| source_id | INT | PK, AUTO_INCREMENT | Identifiant unique de la source |
| nom | VARCHAR(200) | NOT NULL, UNIQUE | Nom de la source (ex: "Daily Food Nutrition Dataset") |
| description | VARCHAR(500) | NULL | Description détaillée |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: source_id
- UNIQUE: nom

**Valeurs initiales:**
- "Daily Food Nutrition Dataset" — Source CSV alimentation
- "Gym Members Exercise Tracking" — Source CSV sport/biométrie
- "Sleep Health and Lifestyle Dataset" — Source CSV sommeil/santé
- "ExerciseDB (JSON + GIFs)" — Source JSON exercices + assets

---

### execution_etl

**Objectif:** Historique des exécutions ETL avec métriques de qualité

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| execution_id | INT | PK, AUTO_INCREMENT | Identifiant unique de l'exécution |
| source_id | INT | NOT NULL, FK | Source de données traitée |
| statut | ENUM('EN_COURS','SUCCES','ECHEC') | NOT NULL, DEFAULT 'EN_COURS' | Statut de l'exécution |
| demarre_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Début de l'exécution |
| termine_le | DATETIME | NULL | Fin de l'exécution |
| lignes_lues | INT | NOT NULL, DEFAULT 0 | Nombre de lignes lues |
| lignes_valides | INT | NOT NULL, DEFAULT 0 | Nombre de lignes valides |
| lignes_invalides | INT | NOT NULL, DEFAULT 0 | Nombre de lignes rejetées |
| message | VARCHAR(250) | NULL | Message de fin (succès ou erreur) |

**Index:**
- PRIMARY KEY: execution_id
- INDEX: idx_execution_source (source_id)
- INDEX: idx_execution_statut (statut)

**Clés étrangères:**
- fk_execution_source: source_id → source_donnees(source_id) ON DELETE RESTRICT

---

### lot_donnees

**Objectif:** Lots de données importés avec traçabilité

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| lot_id | INT | PK, AUTO_INCREMENT | Identifiant unique du lot |
| source_id | INT | NOT NULL, FK | Source de données |
| nom_lot | VARCHAR(200) | NOT NULL | Nom du lot (ex: fichier CSV) |
| statut | ENUM('TELEVERSE','VALIDE','NETTOYE','REJETE') | NOT NULL, DEFAULT 'TELEVERSE' | État du lot dans le pipeline |
| cree_par | INT | NULL, FK | Utilisateur ayant créé le lot |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: lot_id
- INDEX: idx_lot_source (source_id)
- INDEX: idx_lot_statut (statut)
- UNIQUE: uq_lot_nom_source (source_id, nom_lot)

**Clés étrangères:**
- fk_lot_source: source_id → source_donnees(source_id) ON DELETE RESTRICT
- fk_lot_cree_par: cree_par → utilisateur(utilisateur_id) ON DELETE SET NULL

---

### anomalie_donnee

**Objectif:** Journal des erreurs et avertissements détectés pendant l'ETL

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| anomalie_id | BIGINT | PK, AUTO_INCREMENT | Identifiant unique de l'anomalie |
| execution_id | INT | NOT NULL, FK | Exécution ETL concernée |
| severite | ENUM('AVERT','ERREUR') | NOT NULL | Niveau de sévérité |
| entite | VARCHAR(80) | NOT NULL | Table/entité concernée |
| ref_ligne | VARCHAR(60) | NULL | Référence de la ligne source |
| nom_champ | VARCHAR(120) | NULL | Champ concerné |
| code_anomalie | VARCHAR(80) | NOT NULL | Code d'erreur (ex: "VALEUR_MANQUANTE") |
| description | VARCHAR(250) | NOT NULL | Description lisible de l'anomalie |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de détection |

**Index:**
- PRIMARY KEY: anomalie_id
- INDEX: idx_anom_exec (execution_id)
- INDEX: idx_anom_sev (severite)

**Clés étrangères:**
- fk_anomalie_execution: execution_id → execution_etl(execution_id) ON DELETE CASCADE

---

### enregistrement_brut

**Objectif:** Stockage des données brutes JSON avant transformation

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| enregistrement_id | BIGINT | PK, AUTO_INCREMENT | Identifiant unique |
| lot_id | INT | NOT NULL, FK | Lot de données source |
| entite | VARCHAR(80) | NOT NULL | Type d'entité (aliment, exercice, etc.) |
| ref_externe | VARCHAR(120) | NULL | Identifiant externe (ID source) |
| payload | JSON | NOT NULL | Données brutes en JSON |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date d'import |

**Index:**
- PRIMARY KEY: enregistrement_id
- INDEX: idx_raw_lot (lot_id)
- INDEX: idx_raw_entite (entite)

**Clés étrangères:**
- fk_raw_lot: lot_id → lot_donnees(lot_id) ON DELETE CASCADE

---

### stg_alimentation

**Objectif:** Table de staging pour le dataset alimentation (pandas.to_sql)

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| stg_id | BIGINT | PK, AUTO_INCREMENT | Identifiant staging |
| lot_id | INT | NOT NULL, FK | Lot de données source |
| food_item | VARCHAR(255) | NULL | Nom de l'aliment |
| category | VARCHAR(120) | NULL | Catégorie alimentaire |
| calories_kcal | DECIMAL(10,2) | NULL | Calories (kcal) |
| protein_g | DECIMAL(10,2) | NULL | Protéines (g) |
| carbohydrates_g | DECIMAL(10,2) | NULL | Glucides (g) |
| fat_g | DECIMAL(10,2) | NULL | Lipides (g) |
| fiber_g | DECIMAL(10,2) | NULL | Fibres (g) |
| sugars_g | DECIMAL(10,2) | NULL | Sucres (g) |
| sodium_mg | DECIMAL(10,2) | NULL | Sodium (mg) |
| cholesterol_mg | DECIMAL(10,2) | NULL | Cholestérol (mg) |
| meal_type | VARCHAR(60) | NULL | Type de repas |
| water_intake_ml | DECIMAL(10,2) | NULL | Apport en eau (ml) |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date d'import |

**Index:**
- PRIMARY KEY: stg_id
- INDEX: idx_stg_food_lot (lot_id)

**Clés étrangères:**
- fk_stg_food_lot: lot_id → lot_donnees(lot_id) ON DELETE CASCADE

---

### stg_salle_sport

**Objectif:** Table de staging pour le dataset gym/biométrie

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| stg_id | BIGINT | PK, AUTO_INCREMENT | Identifiant staging |
| lot_id | INT | NOT NULL, FK | Lot de données source |
| age | INT | NULL | Âge |
| gender | VARCHAR(20) | NULL | Genre |
| weight_kg | DECIMAL(10,2) | NULL | Poids (kg) |
| height_m | DECIMAL(10,2) | NULL | Taille (m) |
| max_bpm | INT | NULL | Fréquence cardiaque max |
| avg_bpm | INT | NULL | Fréquence cardiaque moyenne |
| resting_bpm | INT | NULL | Fréquence cardiaque au repos |
| session_duration_hours | DECIMAL(10,2) | NULL | Durée de session (h) |
| calories_burned | DECIMAL(10,2) | NULL | Calories brûlées |
| workout_type | VARCHAR(80) | NULL | Type d'entraînement |
| fat_percentage | DECIMAL(10,2) | NULL | Taux de masse grasse (%) |
| water_intake_l | DECIMAL(10,2) | NULL | Apport en eau (L) |
| workout_frequency_days_week | DECIMAL(10,2) | NULL | Fréquence d'entraînement (j/sem) |
| experience_level | VARCHAR(50) | NULL | Niveau d'expérience |
| bmi | DECIMAL(10,2) | NULL | IMC calculé |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date d'import |

**Index:**
- PRIMARY KEY: stg_id
- INDEX: idx_stg_gym_lot (lot_id)

**Clés étrangères:**
- fk_stg_gym_lot: lot_id → lot_donnees(lot_id) ON DELETE CASCADE

---

### stg_sommeil_sante

**Objectif:** Table de staging pour le dataset sommeil/santé

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| stg_id | BIGINT | PK, AUTO_INCREMENT | Identifiant staging |
| lot_id | INT | NOT NULL, FK | Lot de données source |
| person_id | VARCHAR(60) | NOT NULL | Identifiant personne source |
| gender | VARCHAR(20) | NULL | Genre |
| age | INT | NULL | Âge |
| occupation | VARCHAR(120) | NULL | Profession |
| sleep_duration | DECIMAL(10,2) | NULL | Durée de sommeil (h) |
| quality_of_sleep | DECIMAL(10,2) | NULL | Score qualité sommeil |
| physical_activity_level | DECIMAL(10,2) | NULL | Niveau activité physique |
| stress_level | DECIMAL(10,2) | NULL | Niveau de stress |
| bmi_category | VARCHAR(60) | NULL | Catégorie IMC |
| blood_pressure | VARCHAR(40) | NULL | Tension artérielle (brut) |
| heart_rate | INT | NULL | Fréquence cardiaque |
| daily_steps | INT | NULL | Pas quotidiens |
| sleep_disorder | VARCHAR(60) | NULL | Trouble du sommeil |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date d'import |

**Index:**
- PRIMARY KEY: stg_id
- INDEX: idx_stg_sleep_lot (lot_id)
- INDEX: idx_stg_sleep_person (person_id)

**Clés étrangères:**
- fk_stg_sleep_lot: lot_id → lot_donnees(lot_id) ON DELETE CASCADE

---

### aliment

**Objectif:** Référentiel des aliments avec valeurs nutritionnelles (données nettoyées)

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| aliment_id | INT | PK, AUTO_INCREMENT | Identifiant unique aliment |
| nom | VARCHAR(255) | NOT NULL, UNIQUE | Nom de l'aliment |
| categorie | VARCHAR(120) | NULL | Catégorie alimentaire |
| calories_kcal | DECIMAL(10,2) | NULL | Calories pour 100g |
| proteines_g | DECIMAL(10,2) | NULL | Protéines (g/100g) |
| glucides_g | DECIMAL(10,2) | NULL | Glucides (g/100g) |
| lipides_g | DECIMAL(10,2) | NULL | Lipides (g/100g) |
| fibres_g | DECIMAL(10,2) | NULL | Fibres (g/100g) |
| sucres_g | DECIMAL(10,2) | NULL | Sucres (g/100g) |
| sodium_mg | DECIMAL(10,2) | NULL | Sodium (mg/100g) |
| cholesterol_mg | DECIMAL(10,2) | NULL | Cholestérol (mg/100g) |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: aliment_id
- UNIQUE: uq_aliment_nom (nom)

---

### exercice

**Objectif:** Catalogue d'exercices avec instructions et médias

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| exercice_id | BIGINT | PK, AUTO_INCREMENT | Identifiant unique exercice |
| external_id | VARCHAR(80) | NULL, UNIQUE | ID externe (ExerciseDB) |
| nom | VARCHAR(255) | NULL | Nom de l'exercice |
| partie_corps | VARCHAR(80) | NULL | Partie du corps ciblée |
| muscle_cible | VARCHAR(80) | NULL | Muscle principal |
| equipement | VARCHAR(120) | NULL | Équipement requis |
| parties_corps_json | JSON | NULL | Parties du corps (JSON array) |
| muscles_secondaires_json | JSON | NULL | Muscles secondaires (JSON array) |
| equipements_json | JSON | NULL | Équipements alternatifs (JSON array) |
| instructions_json | JSON | NULL | Instructions étape par étape (JSON array) |
| gif_180_path | VARCHAR(255) | NULL | Chemin GIF 180px |
| gif_360_path | VARCHAR(255) | NULL | Chemin GIF 360px |
| gif_720_path | VARCHAR(255) | NULL | Chemin GIF 720px |
| gif_1080_path | VARCHAR(255) | NULL | Chemin GIF 1080px |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: exercice_id
- UNIQUE: uq_exercice_external (external_id)
- INDEX: idx_exo_nom (nom)

---

### ref_type_entrainement

**Objectif:** Table de référence des types d'entraînement

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| type_entrainement | VARCHAR(80) | PK | Type d'entraînement (clé naturelle) |

**Index:**
- PRIMARY KEY: type_entrainement

**Valeurs initiales:**
- "Other" (valeur par défaut)
- Autres valeurs insérées par etl_gym.py

---

### profil_utilisateur

**Objectif:** Profil biométrique de l'utilisateur (1:1 avec utilisateur)

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| utilisateur_id | INT | PK, FK | Identifiant utilisateur (relation 1:1) |
| genre | VARCHAR(20) | NULL | Genre (male/female/other) |
| age | INT | NULL | Âge en années |
| taille_m | DECIMAL(10,2) | NULL | Taille en mètres |
| poids_kg | DECIMAL(10,2) | NULL | Poids en kilogrammes |
| imc | DECIMAL(10,2) | NULL | Indice de masse corporelle |
| categorie_imc | VARCHAR(60) | NULL | Catégorie IMC (Normal, Surpoids, etc.) |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: utilisateur_id

**Clés étrangères:**
- fk_profil_user: utilisateur_id → utilisateur(utilisateur_id) ON DELETE CASCADE

---

### objectif_utilisateur

**Objectif:** Historique des objectifs poursuivis par un utilisateur

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| objectif_id | INT | PK, AUTO_INCREMENT | Identifiant unique de l'objectif |
| utilisateur_id | INT | NOT NULL, FK | Utilisateur propriétaire de l'objectif |
| date_debut | DATE | NOT NULL | Date de début de l'objectif |
| actif_unique | BOOLEAN | NOT NULL, DEFAULT 1 | Marque l'objectif actif courant |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: objectif_id
- INDEX: idx_objectif_user_date (utilisateur_id, date_debut)
- INDEX: idx_objectif_user_active (utilisateur_id, actif_unique)

**Clés étrangères:**
- fk_objectif_user: utilisateur_id → utilisateur(utilisateur_id) ON DELETE CASCADE

---

### progression_photo

**Objectif:** Photos de progression illustrant l'évolution d'un objectif utilisateur

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| photo_id | BIGINT | PK, AUTO_INCREMENT | Identifiant unique de la photo |
| utilisateur_id | INT | NOT NULL, FK | Utilisateur propriétaire de la photo |
| objectif_id | INT | NOT NULL, FK | Objectif illustré par la photo |
| prise_le | DATETIME | NOT NULL | Date et heure de prise de la photo |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: photo_id
- INDEX: idx_photo_objectif_date (objectif_id, prise_le)
- INDEX: idx_photo_user_date (utilisateur_id, prise_le)

**Clés étrangères:**
- fk_photo_user: utilisateur_id → utilisateur(utilisateur_id) ON DELETE CASCADE
- fk_photo_objectif: objectif_id → objectif_utilisateur(objectif_id) ON DELETE CASCADE

---

### journal_alimentaire

**Objectif:** Journal des repas et consommations alimentaires

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| journal_id | BIGINT | PK, AUTO_INCREMENT | Identifiant unique entrée |
| utilisateur_id | INT | NOT NULL, FK | Utilisateur concerné |
| consomme_le | DATETIME | NOT NULL | Date et heure de consommation |
| type_repas | VARCHAR(30) | NULL | Type de repas (petit-déjeuner, déjeuner, etc.) |
| aliment_id | INT | NULL, FK | Aliment du référentiel (si lié) |
| aliment_nom_libre | VARCHAR(255) | NULL | Nom libre si aliment non référencé |
| quantite | DECIMAL(10,2) | NULL | Quantité consommée |
| unite_quantite | VARCHAR(30) | NULL | Unité (g, ml, portion, etc.) |
| calories_kcal | DECIMAL(10,2) | NULL | Calories calculées |
| eau_ml | DECIMAL(10,2) | NULL | Apport en eau (ml) |
| source_tag | VARCHAR(60) | NULL | Tag source (ETL, manuel, API) |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: journal_id
- INDEX: idx_journal_user_date (utilisateur_id, consomme_le)

**Clés étrangères:**
- fk_journal_user: utilisateur_id → utilisateur(utilisateur_id) ON DELETE CASCADE
- fk_journal_aliment: aliment_id → aliment(aliment_id) ON DELETE SET NULL

---

### mesure_biometrique

**Objectif:** Historique des mesures corporelles

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| mesure_id | BIGINT | PK, AUTO_INCREMENT | Identifiant unique mesure |
| utilisateur_id | INT | NOT NULL, FK | Utilisateur concerné |
| mesure_le | DATETIME | NOT NULL | Date et heure de la mesure |
| poids_kg | DECIMAL(10,2) | NULL | Poids (kg) |
| taille_m | DECIMAL(10,2) | NULL | Taille (m) |
| imc | DECIMAL(10,2) | NULL | IMC calculé |
| taux_masse_grasse | DECIMAL(10,2) | NULL | Taux de masse grasse (%) |
| bpm_repos | INT | NULL | Fréquence cardiaque au repos |
| bpm_moyen | INT | NULL | Fréquence cardiaque moyenne |
| bpm_max | INT | NULL | Fréquence cardiaque max |
| eau_l | DECIMAL(10,2) | NULL | Apport en eau (L) |
| source_tag | VARCHAR(60) | NULL | Tag source (ETL, manuel, API) |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: mesure_id
- INDEX: idx_mesure_user_date (utilisateur_id, mesure_le)

**Clés étrangères:**
- fk_mesure_user: utilisateur_id → utilisateur(utilisateur_id) ON DELETE CASCADE

---

### seance_entrainement

**Objectif:** Sessions d'entraînement avec métriques

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| seance_id | BIGINT | PK, AUTO_INCREMENT | Identifiant unique séance |
| utilisateur_id | INT | NOT NULL, FK | Utilisateur concerné |
| date_seance | DATE | NOT NULL | Date de la séance |
| type_entrainement | VARCHAR(80) | NOT NULL, FK | Type d'entraînement |
| duree_seance_h | DECIMAL(10,2) | NULL | Durée en heures |
| calories_brulees | DECIMAL(10,2) | NULL | Calories dépensées |
| frequence_entrainement_j_sem | DECIMAL(10,2) | NULL | Fréquence hebdomadaire |
| niveau_experience | VARCHAR(50) | NULL | Niveau (débutant, intermédiaire, avancé) |
| eau_l | DECIMAL(10,2) | NULL | Hydratation (L) |
| source_tag | VARCHAR(60) | NULL | Tag source (ETL, manuel, API) |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: seance_id
- INDEX: idx_seance_user_date (utilisateur_id, date_seance)

**Clés étrangères:**
- fk_seance_user: utilisateur_id → utilisateur(utilisateur_id) ON DELETE CASCADE
- fk_seance_type: type_entrainement → ref_type_entrainement(type_entrainement) ON DELETE RESTRICT

---

### instantane_sommeil_sante

**Objectif:** Données quotidiennes sommeil et santé globale

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| instantane_id | BIGINT | PK, AUTO_INCREMENT | Identifiant unique |
| utilisateur_id | INT | NOT NULL, FK | Utilisateur concerné |
| date_instantane | DATE | NOT NULL | Date de l'instantané |
| identifiant_personne_externe | VARCHAR(60) | NULL | ID personne source (dataset) |
| genre | VARCHAR(20) | NULL | Genre |
| age | INT | NULL | Âge |
| profession | VARCHAR(120) | NULL | Profession |
| duree_sommeil_h | DECIMAL(10,2) | NULL | Durée de sommeil (h) |
| qualite_sommeil_score | DECIMAL(10,2) | NULL | Score qualité (1-10) |
| activite_physique_min_jour | DECIMAL(10,2) | NULL | Activité physique (min/jour) |
| stress_score | DECIMAL(10,2) | NULL | Score de stress (1-10) |
| categorie_imc | VARCHAR(60) | NULL | Catégorie IMC |
| tension_arterielle_brut | VARCHAR(40) | NULL | Tension artérielle (ex: "120/80") |
| frequence_cardiaque_bpm | INT | NULL | Fréquence cardiaque |
| pas_jour | INT | NULL | Nombre de pas quotidiens |
| trouble_sommeil | VARCHAR(30) | NULL | Trouble du sommeil détecté |
| source_tag | VARCHAR(60) | NULL | Tag source (ETL, manuel, API) |
| cree_le | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date de création |

**Index:**
- PRIMARY KEY: instantane_id
- INDEX: idx_sleep_user_date (utilisateur_id, date_instantane)

**Clés étrangères:**
- fk_sleep_user: utilisateur_id → utilisateur(utilisateur_id) ON DELETE CASCADE

---

## Conventions de Nommage

Toutes les contraintes suivent une convention de nommage cohérente :

| Type | Format | Exemple |
|------|--------|---------|
| Clé primaire | pk_<table> | pk_utilisateur |
| Clé étrangère | fk_<table>_<référence> | fk_journal_user |
| Contrainte unique | uq_<table>_<colonne> | uq_aliment_nom |
| Index | idx_<table>_<colonnes> | idx_journal_user_date |

### Conventions de colonnes

- **IDs:** `<entite>_id` (INT ou BIGINT AUTO_INCREMENT)
- **Dates:** `<action>_le` (DATETIME) ou `date_<type>` (DATE)
- **Mesures:** `<mesure>_<unite>` (ex: poids_kg, taille_m, calories_kcal)
- **Timestamps:** `cree_le` pour la création

### Langue

- Noms de tables et colonnes en **français** (aliment, utilisateur, cree_le)
- Colonnes staging en **anglais** (mappées depuis datasets Kaggle)
- Types ENUM en **français majuscule** (ACTIF, INACTIF, EN_COURS)

---

## Mapping des Datasets Sources

| Table Métier | Dataset Kaggle | Colonnes Mappées |
|--------------|----------------|------------------|
| aliment | Daily Food Nutrition Dataset | nom, categorie, calories, proteines, glucides, lipides, fibres, sucres, sodium, cholesterol |
| exercice | ExerciseDB (JSON + GIFs) | nom, partie_corps, muscle_cible, equipement, instructions, gifs |
| profil_utilisateur | Sleep Health + Gym Members | genre, age, taille, poids, imc, categorie_imc |
| mesure_biometrique | Gym Members Exercise Tracking | poids, taille, imc, taux_masse_grasse, bpm_repos, bpm_moyen, bpm_max |
| seance_entrainement | Gym Members Exercise Tracking | type_entrainement, duree_seance, calories_brulees, frequence_entrainement, niveau_experience |
| instantane_sommeil_sante | Sleep Health and Lifestyle | duree_sommeil, qualite_sommeil, activite_physique, stress, tension_arterielle, frequence_cardiaque, pas_jour, trouble_sommeil |

---

## Flux ETL

```
┌─────────────────┐
│  Fichier CSV    │
│  ou JSON        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  lot_donnees    │  ← Enregistrement du lot
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  stg_*          │  ← pandas.to_sql (staging)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  execution_etl  │  ← Suivi de l'exécution
│  anomalie_donnee│  ← Erreurs détectées
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tables métier  │  ← Données nettoyées
│  (aliment, etc.)│
└─────────────────┘
```

---

## Historique des Révisions

| Date | Version | Modifications |
|------|---------|---------------|
| 2025-02-04 | 1.0 | Création initiale du dictionnaire de données adapté au schéma MySQL ETL |

---

*Document généré dans le cadre du projet MSPR HealthAI Coach*
