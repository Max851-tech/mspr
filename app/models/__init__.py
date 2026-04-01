"""SQLAlchemy models for HealthAI Coach MySQL database."""
from app.models.base import Base

# ETL Pilotage models
from app.models.organisation import Organisation
from app.models.utilisateur import Utilisateur
from app.models.source_donnees import SourceDonnees
from app.models.execution_etl import ExecutionEtl
from app.models.lot_donnees import LotDonnees
from app.models.anomalie_donnee import AnomalieDonnee
from app.models.enregistrement_brut import EnregistrementBrut

# Staging models
from app.models.staging import StgAlimentation, StgSalleSport, StgSommeilSante

# Métier models
from app.models.aliment import Aliment
from app.models.exercice import Exercice
from app.models.ref_type_entrainement import RefTypeEntrainement
from app.models.profil_utilisateur import ProfilUtilisateur
from app.models.objectif_utilisateur import ObjectifUtilisateur
from app.models.progression_photo import ProgressionPhoto
from app.models.journal_alimentaire import JournalAlimentaire
from app.models.mesure_biometrique import MesureBiometrique
from app.models.seance_entrainement import SeanceEntrainement
from app.models.instantane_sommeil_sante import InstantaneSommeilSante

# Infrastructure models
from app.models.audit_log import AuditLog

__all__ = [
    # Base
    "Base",
    # ETL Pilotage
    "Organisation",
    "Utilisateur",
    "SourceDonnees",
    "ExecutionEtl",
    "LotDonnees",
    "AnomalieDonnee",
    "EnregistrementBrut",
    # Staging
    "StgAlimentation",
    "StgSalleSport",
    "StgSommeilSante",
    # Métier
    "Aliment",
    "Exercice",
    "RefTypeEntrainement",
    "ProfilUtilisateur",
    "ObjectifUtilisateur",
    "ProgressionPhoto",
    "JournalAlimentaire",
    "MesureBiometrique",
    "SeanceEntrainement",
    "InstantaneSommeilSante",
    # Infrastructure
    "AuditLog",
]
