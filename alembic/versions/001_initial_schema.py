"""Initial schema - all 18 tables for HealthAI Coach

Revision ID: 001
Revises:
Create Date: 2025-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================
    # ETL PILOTAGE TABLES
    # ==========================================

    # organisation
    op.create_table('organisation',
        sa.Column('organisation_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nom', sa.String(length=150), nullable=False),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('organisation_id', name='pk_organisation'),
        sa.UniqueConstraint('nom', name='uq_organisation_nom'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # utilisateur
    op.create_table('utilisateur',
        sa.Column('utilisateur_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organisation_id', sa.Integer(), nullable=False),
        sa.Column('nom_utilisateur', sa.String(length=120), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'UTILISATEUR', name='role_enum'), server_default='UTILISATEUR', nullable=False),
        sa.Column('statut', sa.Enum('ACTIF', 'INACTIF', name='statut_enum'), server_default='ACTIF', nullable=False),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['organisation_id'], ['organisation.organisation_id'], name='fk_utilisateur_org', ondelete='RESTRICT', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('utilisateur_id', name='pk_utilisateur'),
        sa.UniqueConstraint('nom_utilisateur', name='uq_utilisateur_nom_utilisateur'),
        mysql_engine='InnoDB'
    )

    # source_donnees
    op.create_table('source_donnees',
        sa.Column('source_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('source_id', name='pk_source_donnees'),
        sa.UniqueConstraint('nom', name='uq_source_donnees_nom'),
        mysql_engine='InnoDB'
    )

    # execution_etl
    op.create_table('execution_etl',
        sa.Column('execution_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('statut', sa.Enum('EN_COURS', 'SUCCES', 'ECHEC', name='statut_etl_enum'), server_default='EN_COURS', nullable=False),
        sa.Column('demarre_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('termine_le', sa.DateTime(), nullable=True),
        sa.Column('lignes_lues', sa.Integer(), server_default='0', nullable=False),
        sa.Column('lignes_valides', sa.Integer(), server_default='0', nullable=False),
        sa.Column('lignes_invalides', sa.Integer(), server_default='0', nullable=False),
        sa.Column('message', sa.String(length=250), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['source_donnees.source_id'], name='fk_execution_source', ondelete='RESTRICT', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('execution_id', name='pk_execution_etl'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_execution_source', 'execution_etl', ['source_id'])
    op.create_index('idx_execution_statut', 'execution_etl', ['statut'])

    # lot_donnees
    op.create_table('lot_donnees',
        sa.Column('lot_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('nom_lot', sa.String(length=200), nullable=False),
        sa.Column('statut', sa.Enum('TELEVERSE', 'VALIDE', 'NETTOYE', 'REJETE', name='statut_lot_enum'), server_default='TELEVERSE', nullable=False),
        sa.Column('cree_par', sa.Integer(), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['source_donnees.source_id'], name='fk_lot_source', ondelete='RESTRICT', onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['cree_par'], ['utilisateur.utilisateur_id'], name='fk_lot_cree_par', ondelete='SET NULL', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('lot_id', name='pk_lot_donnees'),
        sa.UniqueConstraint('source_id', 'nom_lot', name='uq_lot_nom_source'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_lot_source', 'lot_donnees', ['source_id'])
    op.create_index('idx_lot_statut', 'lot_donnees', ['statut'])

    # anomalie_donnee
    op.create_table('anomalie_donnee',
        sa.Column('anomalie_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('execution_id', sa.Integer(), nullable=False),
        sa.Column('severite', sa.Enum('AVERT', 'ERREUR', name='severite_enum'), nullable=False),
        sa.Column('entite', sa.String(length=80), nullable=False),
        sa.Column('ref_ligne', sa.String(length=60), nullable=True),
        sa.Column('nom_champ', sa.String(length=120), nullable=True),
        sa.Column('code_anomalie', sa.String(length=80), nullable=False),
        sa.Column('description', sa.String(length=250), nullable=False),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['execution_id'], ['execution_etl.execution_id'], name='fk_anomalie_execution', ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('anomalie_id', name='pk_anomalie_donnee'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_anom_exec', 'anomalie_donnee', ['execution_id'])
    op.create_index('idx_anom_sev', 'anomalie_donnee', ['severite'])

    # enregistrement_brut
    op.create_table('enregistrement_brut',
        sa.Column('enregistrement_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('lot_id', sa.Integer(), nullable=False),
        sa.Column('entite', sa.String(length=80), nullable=False),
        sa.Column('ref_externe', sa.String(length=120), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['lot_id'], ['lot_donnees.lot_id'], name='fk_raw_lot', ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('enregistrement_id', name='pk_enregistrement_brut'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_raw_lot', 'enregistrement_brut', ['lot_id'])
    op.create_index('idx_raw_entite', 'enregistrement_brut', ['entite'])

    # ==========================================
    # STAGING TABLES
    # ==========================================

    # stg_alimentation
    op.create_table('stg_alimentation',
        sa.Column('stg_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('lot_id', sa.Integer(), nullable=False),
        sa.Column('food_item', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=120), nullable=True),
        sa.Column('calories_kcal', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('protein_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('carbohydrates_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('fat_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('fiber_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('sugars_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('sodium_mg', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cholesterol_mg', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('meal_type', sa.String(length=60), nullable=True),
        sa.Column('water_intake_ml', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['lot_id'], ['lot_donnees.lot_id'], name='fk_stg_food_lot', ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('stg_id', name='pk_stg_alimentation'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_stg_food_lot', 'stg_alimentation', ['lot_id'])

    # stg_salle_sport
    op.create_table('stg_salle_sport',
        sa.Column('stg_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('lot_id', sa.Integer(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('weight_kg', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('height_m', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('max_bpm', sa.Integer(), nullable=True),
        sa.Column('avg_bpm', sa.Integer(), nullable=True),
        sa.Column('resting_bpm', sa.Integer(), nullable=True),
        sa.Column('session_duration_hours', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('calories_burned', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('workout_type', sa.String(length=80), nullable=True),
        sa.Column('fat_percentage', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('water_intake_l', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('workout_frequency_days_week', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('experience_level', sa.String(length=50), nullable=True),
        sa.Column('bmi', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['lot_id'], ['lot_donnees.lot_id'], name='fk_stg_gym_lot', ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('stg_id', name='pk_stg_salle_sport'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_stg_gym_lot', 'stg_salle_sport', ['lot_id'])

    # stg_sommeil_sante
    op.create_table('stg_sommeil_sante',
        sa.Column('stg_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('lot_id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.String(length=60), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('occupation', sa.String(length=120), nullable=True),
        sa.Column('sleep_duration', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('quality_of_sleep', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('physical_activity_level', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('stress_level', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('bmi_category', sa.String(length=60), nullable=True),
        sa.Column('blood_pressure', sa.String(length=40), nullable=True),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.Column('daily_steps', sa.Integer(), nullable=True),
        sa.Column('sleep_disorder', sa.String(length=60), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['lot_id'], ['lot_donnees.lot_id'], name='fk_stg_sleep_lot', ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('stg_id', name='pk_stg_sommeil_sante'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_stg_sleep_lot', 'stg_sommeil_sante', ['lot_id'])
    op.create_index('idx_stg_sleep_person', 'stg_sommeil_sante', ['person_id'])

    # ==========================================
    # MÉTIER TABLES
    # ==========================================

    # aliment
    op.create_table('aliment',
        sa.Column('aliment_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nom', sa.String(length=255), nullable=False),
        sa.Column('categorie', sa.String(length=120), nullable=True),
        sa.Column('calories_kcal', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('proteines_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('glucides_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('lipides_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('fibres_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('sucres_g', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('sodium_mg', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cholesterol_mg', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('aliment_id', name='pk_aliment'),
        sa.UniqueConstraint('nom', name='uq_aliment_nom'),
        mysql_engine='InnoDB'
    )

    # exercice
    op.create_table('exercice',
        sa.Column('exercice_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('external_id', sa.String(length=80), nullable=True),
        sa.Column('nom', sa.String(length=255), nullable=True),
        sa.Column('partie_corps', sa.String(length=80), nullable=True),
        sa.Column('muscle_cible', sa.String(length=80), nullable=True),
        sa.Column('equipement', sa.String(length=120), nullable=True),
        sa.Column('parties_corps_json', sa.JSON(), nullable=True),
        sa.Column('muscles_secondaires_json', sa.JSON(), nullable=True),
        sa.Column('equipements_json', sa.JSON(), nullable=True),
        sa.Column('instructions_json', sa.JSON(), nullable=True),
        sa.Column('gif_180_path', sa.String(length=255), nullable=True),
        sa.Column('gif_360_path', sa.String(length=255), nullable=True),
        sa.Column('gif_720_path', sa.String(length=255), nullable=True),
        sa.Column('gif_1080_path', sa.String(length=255), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('exercice_id', name='pk_exercice'),
        sa.UniqueConstraint('external_id', name='uq_exercice_external'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_exo_nom', 'exercice', ['nom'])

    # ref_type_entrainement
    op.create_table('ref_type_entrainement',
        sa.Column('type_entrainement', sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint('type_entrainement', name='pk_ref_type_entrainement'),
        mysql_engine='InnoDB'
    )

    # profil_utilisateur
    op.create_table('profil_utilisateur',
        sa.Column('utilisateur_id', sa.Integer(), nullable=False),
        sa.Column('genre', sa.String(length=20), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('taille_m', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('poids_kg', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('imc', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('categorie_imc', sa.String(length=60), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateur.utilisateur_id'], name='fk_profil_user', ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('utilisateur_id', name='pk_profil_utilisateur'),
        mysql_engine='InnoDB'
    )

    # journal_alimentaire
    op.create_table('journal_alimentaire',
        sa.Column('journal_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=False),
        sa.Column('consomme_le', sa.DateTime(), nullable=False),
        sa.Column('type_repas', sa.String(length=30), nullable=True),
        sa.Column('aliment_id', sa.Integer(), nullable=True),
        sa.Column('aliment_nom_libre', sa.String(length=255), nullable=True),
        sa.Column('quantite', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('unite_quantite', sa.String(length=30), nullable=True),
        sa.Column('calories_kcal', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('eau_ml', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('source_tag', sa.String(length=60), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateur.utilisateur_id'], name='fk_journal_user', ondelete='CASCADE', onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['aliment_id'], ['aliment.aliment_id'], name='fk_journal_aliment', ondelete='SET NULL', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('journal_id', name='pk_journal_alimentaire'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_journal_user_date', 'journal_alimentaire', ['utilisateur_id', 'consomme_le'])

    # mesure_biometrique
    op.create_table('mesure_biometrique',
        sa.Column('mesure_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=False),
        sa.Column('mesure_le', sa.DateTime(), nullable=False),
        sa.Column('poids_kg', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('taille_m', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('imc', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('taux_masse_grasse', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('bpm_repos', sa.Integer(), nullable=True),
        sa.Column('bpm_moyen', sa.Integer(), nullable=True),
        sa.Column('bpm_max', sa.Integer(), nullable=True),
        sa.Column('eau_l', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('source_tag', sa.String(length=60), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateur.utilisateur_id'], name='fk_mesure_user', ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('mesure_id', name='pk_mesure_biometrique'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_mesure_user_date', 'mesure_biometrique', ['utilisateur_id', 'mesure_le'])

    # seance_entrainement
    op.create_table('seance_entrainement',
        sa.Column('seance_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=False),
        sa.Column('date_seance', sa.Date(), nullable=False),
        sa.Column('type_entrainement', sa.String(length=80), nullable=False),
        sa.Column('duree_seance_h', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('calories_brulees', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('frequence_entrainement_j_sem', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('niveau_experience', sa.String(length=50), nullable=True),
        sa.Column('eau_l', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('source_tag', sa.String(length=60), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateur.utilisateur_id'], name='fk_seance_user', ondelete='CASCADE', onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['type_entrainement'], ['ref_type_entrainement.type_entrainement'], name='fk_seance_type', ondelete='RESTRICT', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('seance_id', name='pk_seance_entrainement'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_seance_user_date', 'seance_entrainement', ['utilisateur_id', 'date_seance'])

    # instantane_sommeil_sante
    op.create_table('instantane_sommeil_sante',
        sa.Column('instantane_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=False),
        sa.Column('date_instantane', sa.Date(), nullable=False),
        sa.Column('identifiant_personne_externe', sa.String(length=60), nullable=True),
        sa.Column('genre', sa.String(length=20), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('profession', sa.String(length=120), nullable=True),
        sa.Column('duree_sommeil_h', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('qualite_sommeil_score', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('activite_physique_min_jour', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('stress_score', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('categorie_imc', sa.String(length=60), nullable=True),
        sa.Column('tension_arterielle_brut', sa.String(length=40), nullable=True),
        sa.Column('frequence_cardiaque_bpm', sa.Integer(), nullable=True),
        sa.Column('pas_jour', sa.Integer(), nullable=True),
        sa.Column('trouble_sommeil', sa.String(length=30), nullable=True),
        sa.Column('source_tag', sa.String(length=60), nullable=True),
        sa.Column('cree_le', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateur.utilisateur_id'], name='fk_sleep_user', ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('instantane_id', name='pk_instantane_sommeil_sante'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_sleep_user_date', 'instantane_sommeil_sante', ['utilisateur_id', 'date_instantane'])


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table('instantane_sommeil_sante')
    op.drop_table('seance_entrainement')
    op.drop_table('mesure_biometrique')
    op.drop_table('journal_alimentaire')
    op.drop_table('profil_utilisateur')
    op.drop_table('ref_type_entrainement')
    op.drop_table('exercice')
    op.drop_table('aliment')
    op.drop_table('stg_sommeil_sante')
    op.drop_table('stg_salle_sport')
    op.drop_table('stg_alimentation')
    op.drop_table('enregistrement_brut')
    op.drop_table('anomalie_donnee')
    op.drop_table('lot_donnees')
    op.drop_table('execution_etl')
    op.drop_table('source_donnees')
    op.drop_table('utilisateur')
    op.drop_table('organisation')
