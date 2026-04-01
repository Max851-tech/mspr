"""Add auth columns to utilisateur and objectives to profil_utilisateur

Revision ID: 002
Revises: 001
Create Date: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table (idempotent migrations)."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # ==========================================
    # UTILISATEUR TABLE - Add auth columns
    # ==========================================

    # Add email column (nullable for existing seed users)
    if not column_exists('utilisateur', 'email'):
        op.add_column('utilisateur',
            sa.Column('email', sa.String(length=255), nullable=True)
        )
        # Create unique constraint on email
        op.create_unique_constraint('uq_utilisateur_email', 'utilisateur', ['email'])

    # Add mot_de_passe_hash column (Maxime's auth service fills this)
    if not column_exists('utilisateur', 'mot_de_passe_hash'):
        op.add_column('utilisateur',
            sa.Column('mot_de_passe_hash', sa.String(length=255), nullable=True)
        )

    # ==========================================
    # PROFIL_UTILISATEUR TABLE - Add objectives columns
    # ==========================================

    # Add objectif_principal (enum: PERTE_POIDS, MUSCLE, SOMMEIL, FORME)
    if not column_exists('profil_utilisateur', 'objectif_principal'):
        op.add_column('profil_utilisateur',
            sa.Column('objectif_principal', sa.String(length=50), nullable=True)
        )

    # Add objectifs_secondaires (JSON array)
    if not column_exists('profil_utilisateur', 'objectifs_secondaires'):
        op.add_column('profil_utilisateur',
            sa.Column('objectifs_secondaires', sa.JSON(), nullable=True)
        )


def downgrade() -> None:
    # Remove columns in reverse order

    # Profil utilisateur
    if column_exists('profil_utilisateur', 'objectifs_secondaires'):
        op.drop_column('profil_utilisateur', 'objectifs_secondaires')

    if column_exists('profil_utilisateur', 'objectif_principal'):
        op.drop_column('profil_utilisateur', 'objectif_principal')

    # Utilisateur
    if column_exists('utilisateur', 'mot_de_passe_hash'):
        op.drop_column('utilisateur', 'mot_de_passe_hash')

    if column_exists('utilisateur', 'email'):
        op.drop_constraint('uq_utilisateur_email', 'utilisateur', type_='unique')
        op.drop_column('utilisateur', 'email')
