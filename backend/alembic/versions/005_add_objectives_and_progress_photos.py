"""Add objectif_utilisateur and progression_photo tables

Revision ID: 005
Revises: 004
Create Date: 2026-03-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the new goal-tracking tables from the updated MCD."""
    op.create_table(
        "objectif_utilisateur",
        sa.Column("objectif_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("utilisateur_id", sa.Integer(), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=False),
        sa.Column("actif_unique", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("cree_le", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(
            ["utilisateur_id"],
            ["utilisateur.utilisateur_id"],
            name="fk_objectif_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("objectif_id", name="pk_objectif_utilisateur"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index(
        "idx_objectif_user_date",
        "objectif_utilisateur",
        ["utilisateur_id", "date_debut"],
    )
    op.create_index(
        "idx_objectif_user_active",
        "objectif_utilisateur",
        ["utilisateur_id", "actif_unique"],
    )

    op.create_table(
        "progression_photo",
        sa.Column("photo_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("utilisateur_id", sa.Integer(), nullable=False),
        sa.Column("objectif_id", sa.Integer(), nullable=False),
        sa.Column("prise_le", sa.DateTime(), nullable=False),
        sa.Column("cree_le", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(
            ["utilisateur_id"],
            ["utilisateur.utilisateur_id"],
            name="fk_photo_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["objectif_id"],
            ["objectif_utilisateur.objectif_id"],
            name="fk_photo_objectif",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("photo_id", name="pk_progression_photo"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index(
        "idx_photo_objectif_date",
        "progression_photo",
        ["objectif_id", "prise_le"],
    )
    op.create_index(
        "idx_photo_user_date",
        "progression_photo",
        ["utilisateur_id", "prise_le"],
    )


def downgrade() -> None:
    """Drop the goal-tracking tables."""
    op.drop_index("idx_photo_user_date", table_name="progression_photo")
    op.drop_index("idx_photo_objectif_date", table_name="progression_photo")
    op.drop_table("progression_photo")

    op.drop_index("idx_objectif_user_active", table_name="objectif_utilisateur")
    op.drop_index("idx_objectif_user_date", table_name="objectif_utilisateur")
    op.drop_table("objectif_utilisateur")
