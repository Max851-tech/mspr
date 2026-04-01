"""Add soft delete and difficulte to exercice

Revision ID: 004
Revises: 003
Create Date: 2026-02-05 09:03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add deleted_at and difficulte columns to exercice table."""
    # Add deleted_at column with index
    op.add_column(
        'exercice',
        sa.Column('deleted_at', mysql.DATETIME(fsp=6), nullable=True)
    )
    op.create_index(
        'idx_exercice_deleted_at',
        'exercice',
        ['deleted_at']
    )

    # Add difficulte column with index
    op.add_column(
        'exercice',
        sa.Column('difficulte', mysql.VARCHAR(20), nullable=True)
    )
    op.create_index(
        'idx_exercice_difficulte',
        'exercice',
        ['difficulte']
    )


def downgrade() -> None:
    """Remove deleted_at and difficulte columns from exercice table."""
    # Remove difficulte column and index
    op.drop_index('idx_exercice_difficulte', 'exercice')
    op.drop_column('exercice', 'difficulte')

    # Remove deleted_at column and index
    op.drop_index('idx_exercice_deleted_at', 'exercice')
    op.drop_column('exercice', 'deleted_at')
