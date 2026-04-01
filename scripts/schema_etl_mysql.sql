/* =========================================================
   BDD HealthAI Coach - Schéma compatible ETL Python
   - etl_utils.py + etl_food.py + etl_gym.py + etl_sleep.py
   - etl_exercicedb.py (table exercice)
   ========================================================= */

CREATE DATABASE IF NOT EXISTS healthai_coach
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE healthai_coach;

SET FOREIGN_KEY_CHECKS = 0;

/* -------------------------
   Tables "référentiel / pilotage ETL"
   ------------------------- */

CREATE TABLE IF NOT EXISTS organisation (
  organisation_id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(150) NOT NULL UNIQUE,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS utilisateur (
  utilisateur_id INT AUTO_INCREMENT PRIMARY KEY,
  organisation_id INT NOT NULL,
  nom_utilisateur VARCHAR(120) NOT NULL UNIQUE,
  role ENUM('ADMIN','UTILISATEUR') NOT NULL DEFAULT 'UTILISATEUR',
  statut ENUM('ACTIF','INACTIF') NOT NULL DEFAULT 'ACTIF',
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_utilisateur_org
    FOREIGN KEY (organisation_id) REFERENCES organisation(organisation_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS source_donnees (
  source_id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(200) NOT NULL UNIQUE,
  description VARCHAR(500) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS execution_etl (
  execution_id INT AUTO_INCREMENT PRIMARY KEY,
  source_id INT NOT NULL,
  statut ENUM('EN_COURS','SUCCES','ECHEC') NOT NULL DEFAULT 'EN_COURS',
  demarre_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  termine_le DATETIME NULL,
  lignes_lues INT NOT NULL DEFAULT 0,
  lignes_valides INT NOT NULL DEFAULT 0,
  lignes_invalides INT NOT NULL DEFAULT 0,
  message VARCHAR(250) NULL,
  CONSTRAINT fk_execution_source
    FOREIGN KEY (source_id) REFERENCES source_donnees(source_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  INDEX idx_execution_source (source_id),
  INDEX idx_execution_statut (statut)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lot_donnees (
  lot_id INT AUTO_INCREMENT PRIMARY KEY,
  source_id INT NOT NULL,
  nom_lot VARCHAR(200) NOT NULL,
  statut ENUM('TELEVERSE','VALIDE','NETTOYE','REJETE') NOT NULL DEFAULT 'TELEVERSE',
  cree_par INT NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_lot_source
    FOREIGN KEY (source_id) REFERENCES source_donnees(source_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_lot_cree_par
    FOREIGN KEY (cree_par) REFERENCES utilisateur(utilisateur_id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX idx_lot_source (source_id),
  INDEX idx_lot_statut (statut),
  UNIQUE KEY uq_lot_nom_source (source_id, nom_lot)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS anomalie_donnee (
  anomalie_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  execution_id INT NOT NULL,
  severite ENUM('AVERT','ERREUR') NOT NULL,
  entite VARCHAR(80) NOT NULL,
  ref_ligne VARCHAR(60) NULL,
  nom_champ VARCHAR(120) NULL,
  code_anomalie VARCHAR(80) NOT NULL,
  description VARCHAR(250) NOT NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_anomalie_execution
    FOREIGN KEY (execution_id) REFERENCES execution_etl(execution_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_anom_exec (execution_id),
  INDEX idx_anom_sev (severite)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS enregistrement_brut (
  enregistrement_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  lot_id INT NOT NULL,
  entite VARCHAR(80) NOT NULL,
  ref_externe VARCHAR(120) NULL,
  payload JSON NOT NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_raw_lot
    FOREIGN KEY (lot_id) REFERENCES lot_donnees(lot_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_raw_lot (lot_id),
  INDEX idx_raw_entite (entite)
) ENGINE=InnoDB;


/* -------------------------
   STAGING (utilisé par pandas.to_sql)
   ------------------------- */

CREATE TABLE IF NOT EXISTS stg_alimentation (
  stg_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  lot_id INT NOT NULL,
  food_item VARCHAR(255) NULL,
  category VARCHAR(120) NULL,
  calories_kcal DECIMAL(10,2) NULL,
  protein_g DECIMAL(10,2) NULL,
  carbohydrates_g DECIMAL(10,2) NULL,
  fat_g DECIMAL(10,2) NULL,
  fiber_g DECIMAL(10,2) NULL,
  sugars_g DECIMAL(10,2) NULL,
  sodium_mg DECIMAL(10,2) NULL,
  cholesterol_mg DECIMAL(10,2) NULL,
  meal_type VARCHAR(60) NULL,
  water_intake_ml DECIMAL(10,2) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_stg_food_lot
    FOREIGN KEY (lot_id) REFERENCES lot_donnees(lot_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_stg_food_lot (lot_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS stg_salle_sport (
  stg_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  lot_id INT NOT NULL,
  age INT NULL,
  gender VARCHAR(20) NULL,
  weight_kg DECIMAL(10,2) NULL,
  height_m DECIMAL(10,2) NULL,
  max_bpm INT NULL,
  avg_bpm INT NULL,
  resting_bpm INT NULL,
  session_duration_hours DECIMAL(10,2) NULL,
  calories_burned DECIMAL(10,2) NULL,
  workout_type VARCHAR(80) NULL,
  fat_percentage DECIMAL(10,2) NULL,
  water_intake_l DECIMAL(10,2) NULL,
  workout_frequency_days_week DECIMAL(10,2) NULL,
  experience_level VARCHAR(50) NULL,
  bmi DECIMAL(10,2) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_stg_gym_lot
    FOREIGN KEY (lot_id) REFERENCES lot_donnees(lot_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_stg_gym_lot (lot_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS stg_sommeil_sante (
  stg_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  lot_id INT NOT NULL,
  person_id VARCHAR(60) NOT NULL,
  gender VARCHAR(20) NULL,
  age INT NULL,
  occupation VARCHAR(120) NULL,
  sleep_duration DECIMAL(10,2) NULL,
  quality_of_sleep DECIMAL(10,2) NULL,
  physical_activity_level DECIMAL(10,2) NULL,
  stress_level DECIMAL(10,2) NULL,
  bmi_category VARCHAR(60) NULL,
  blood_pressure VARCHAR(40) NULL,
  heart_rate INT NULL,
  daily_steps INT NULL,
  sleep_disorder VARCHAR(60) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_stg_sleep_lot
    FOREIGN KEY (lot_id) REFERENCES lot_donnees(lot_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_stg_sleep_lot (lot_id),
  INDEX idx_stg_sleep_person (person_id)
) ENGINE=InnoDB;


/* -------------------------
   Tables métier (sorties "clean")
   ------------------------- */

CREATE TABLE IF NOT EXISTS aliment (
  aliment_id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(255) NOT NULL,
  categorie VARCHAR(120) NULL,
  calories_kcal DECIMAL(10,2) NULL,
  proteines_g DECIMAL(10,2) NULL,
  glucides_g DECIMAL(10,2) NULL,
  lipides_g DECIMAL(10,2) NULL,
  fibres_g DECIMAL(10,2) NULL,
  sucres_g DECIMAL(10,2) NULL,
  sodium_mg DECIMAL(10,2) NULL,
  cholesterol_mg DECIMAL(10,2) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_aliment_nom (nom)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS journal_alimentaire (
  journal_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  utilisateur_id INT NOT NULL,
  consomme_le DATETIME NOT NULL,
  type_repas VARCHAR(30) NULL,
  aliment_id INT NULL,
  aliment_nom_libre VARCHAR(255) NULL,
  quantite DECIMAL(10,2) NULL,
  unite_quantite VARCHAR(30) NULL,
  calories_kcal DECIMAL(10,2) NULL,
  eau_ml DECIMAL(10,2) NULL,
  source_tag VARCHAR(60) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_journal_user
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_journal_aliment
    FOREIGN KEY (aliment_id) REFERENCES aliment(aliment_id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX idx_journal_user_date (utilisateur_id, consomme_le)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS profil_utilisateur (
  utilisateur_id INT PRIMARY KEY,
  genre VARCHAR(20) NULL,
  age INT NULL,
  taille_m DECIMAL(10,2) NULL,
  poids_kg DECIMAL(10,2) NULL,
  imc DECIMAL(10,2) NULL,
  categorie_imc VARCHAR(60) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_profil_user
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS objectif_utilisateur (
  objectif_id INT AUTO_INCREMENT PRIMARY KEY,
  utilisateur_id INT NOT NULL,
  date_debut DATE NOT NULL,
  actif_unique BOOLEAN NOT NULL DEFAULT TRUE,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_objectif_user
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_objectif_user_date (utilisateur_id, date_debut),
  INDEX idx_objectif_user_active (utilisateur_id, actif_unique)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mesure_biometrique (
  mesure_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  utilisateur_id INT NOT NULL,
  mesure_le DATETIME NOT NULL,
  poids_kg DECIMAL(10,2) NULL,
  taille_m DECIMAL(10,2) NULL,
  imc DECIMAL(10,2) NULL,
  taux_masse_grasse DECIMAL(10,2) NULL,
  bpm_repos INT NULL,
  bpm_moyen INT NULL,
  bpm_max INT NULL,
  eau_l DECIMAL(10,2) NULL,
  source_tag VARCHAR(60) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_mesure_user
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_mesure_user_date (utilisateur_id, mesure_le)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ref_type_entrainement (
  type_entrainement VARCHAR(80) PRIMARY KEY
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS seance_entrainement (
  seance_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  utilisateur_id INT NOT NULL,
  date_seance DATE NOT NULL,
  type_entrainement VARCHAR(80) NOT NULL,
  duree_seance_h DECIMAL(10,2) NULL,
  calories_brulees DECIMAL(10,2) NULL,
  frequence_entrainement_j_sem DECIMAL(10,2) NULL,
  niveau_experience VARCHAR(50) NULL,
  eau_l DECIMAL(10,2) NULL,
  source_tag VARCHAR(60) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_seance_user
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_seance_type
    FOREIGN KEY (type_entrainement) REFERENCES ref_type_entrainement(type_entrainement)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  INDEX idx_seance_user_date (utilisateur_id, date_seance)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS instantane_sommeil_sante (
  instantane_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  utilisateur_id INT NOT NULL,
  date_instantane DATE NOT NULL,
  identifiant_personne_externe VARCHAR(60) NULL,
  genre VARCHAR(20) NULL,
  age INT NULL,
  profession VARCHAR(120) NULL,
  duree_sommeil_h DECIMAL(10,2) NULL,
  qualite_sommeil_score DECIMAL(10,2) NULL,
  activite_physique_min_jour DECIMAL(10,2) NULL,
  stress_score DECIMAL(10,2) NULL,
  categorie_imc VARCHAR(60) NULL,
  tension_arterielle_brut VARCHAR(40) NULL,
  frequence_cardiaque_bpm INT NULL,
  pas_jour INT NULL,
  trouble_sommeil VARCHAR(30) NULL,
  source_tag VARCHAR(60) NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_sleep_user
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_sleep_user_date (utilisateur_id, date_instantane)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS progression_photo (
  photo_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  utilisateur_id INT NOT NULL,
  objectif_id INT NOT NULL,
  prise_le DATETIME NOT NULL,
  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_photo_user
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_photo_objectif
    FOREIGN KEY (objectif_id) REFERENCES objectif_utilisateur(objectif_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_photo_objectif_date (objectif_id, prise_le),
  INDEX idx_photo_user_date (utilisateur_id, prise_le)
) ENGINE=InnoDB;


/* -------------------------
   Table import Exercices (etl_exercicedb.py)
   - mapping flexible: ton script teste les colonnes existantes
   ------------------------- */

CREATE TABLE IF NOT EXISTS exercice (
  exercice_id BIGINT AUTO_INCREMENT PRIMARY KEY,

  -- champs "métier"
  external_id VARCHAR(80) NULL,
  nom VARCHAR(255) NULL,
  partie_corps VARCHAR(80) NULL,
  muscle_cible VARCHAR(80) NULL,
  equipement VARCHAR(120) NULL,

  -- versions JSON (tes ETL mettent du JSON string)
  parties_corps_json JSON NULL,
  muscles_secondaires_json JSON NULL,
  equipements_json JSON NULL,
  instructions_json JSON NULL,

  -- chemins relatifs vers gifs (si présents)
  gif_180_path VARCHAR(255) NULL,
  gif_360_path VARCHAR(255) NULL,
  gif_720_path VARCHAR(255) NULL,
  gif_1080_path VARCHAR(255) NULL,

  cree_le DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_exercice_external (external_id),
  INDEX idx_exo_nom (nom)
) ENGINE=InnoDB;


/* -------------------------
   Données minimales (très utile pour éviter erreurs ETL)
   ------------------------- */

INSERT IGNORE INTO organisation (nom) VALUES ('HealthAI Public');

-- admin par défaut (etl_food.py l'utilise : UTILISATEUR_ADMIN=admin)
INSERT IGNORE INTO utilisateur (organisation_id, nom_utilisateur, role, statut)
SELECT organisation_id, 'admin', 'ADMIN', 'ACTIF'
FROM organisation
WHERE nom='HealthAI Public';

-- sources (get_source_id utilise LIKE : "Daily Food%", "Gym Members%", "Sleep Health%")
INSERT IGNORE INTO source_donnees (nom, description) VALUES
('Daily Food Nutrition Dataset', 'Source CSV alimentation'),
('Gym Members Exercise Tracking', 'Source CSV sport/biométrie'),
('Sleep Health and Lifestyle Dataset', 'Source CSV sommeil/santé'),
('ExerciseDB (JSON + GIFs)', 'Source JSON exercices + assets');

-- ref types au moins "Other" (etl_gym.py insert aussi, mais ça évite FK dès le début)
INSERT IGNORE INTO ref_type_entrainement (type_entrainement) VALUES ('Other');

SET FOREIGN_KEY_CHECKS = 1;
