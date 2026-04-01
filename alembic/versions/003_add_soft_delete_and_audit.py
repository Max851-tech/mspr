"""Add soft delete and audit log infrastructure

Revision ID: 003
Revises: 002
Create Date: 2026-02-05 08:50:17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add deleted_at to aliment table and create audit_log table."""
    # Add deleted_at column to aliment table with index
    op.add_column(
        'aliment',
        sa.Column('deleted_at', mysql.DATETIME(fsp=6), nullable=True)
    )
    op.create_index(
        'idx_aliment_deleted_at',
        'aliment',
        ['deleted_at']
    )

    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('audit_id', mysql.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('table_name', mysql.VARCHAR(80), nullable=False),
        sa.Column('record_id', mysql.BIGINT(), nullable=False),
        sa.Column('action', mysql.VARCHAR(20), nullable=False),
        sa.Column('changed_by', mysql.BIGINT(), nullable=True),
        sa.Column('changed_at', mysql.DATETIME(fsp=6), nullable=False),
        sa.Column('old_values', mysql.JSON(), nullable=True),
        sa.Column('new_values', mysql.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('audit_id', name='pk_audit_log'),
        sa.ForeignKeyConstraint(
            ['changed_by'],
            ['utilisateur.utilisateur_id'],
            name='fk_audit_log_changed_by_utilisateur',
            ondelete='SET NULL'
        ),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create indexes for audit_log
    op.create_index('idx_audit_log_table_name', 'audit_log', ['table_name'])
    op.create_index('idx_audit_log_record_id', 'audit_log', ['record_id'])
    op.create_index('idx_audit_log_changed_at', 'audit_log', ['changed_at'])


def downgrade() -> None:
    """Remove deleted_at from aliment and drop audit_log table."""
    # Drop audit_log table
    op.drop_index('idx_audit_log_changed_at', 'audit_log')
    op.drop_index('idx_audit_log_record_id', 'audit_log')
    op.drop_index('idx_audit_log_table_name', 'audit_log')
    op.drop_table('audit_log')

    # Remove deleted_at column from aliment
    op.drop_index('idx_aliment_deleted_at', 'aliment')
    op.drop_column('aliment', 'deleted_at')
