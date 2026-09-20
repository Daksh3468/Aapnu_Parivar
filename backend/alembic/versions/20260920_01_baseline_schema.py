"""Baseline schema for the existing demo registry.

Revision ID: 20260920_01
Revises:
Create Date: 2026-09-20
"""

from alembic import op

from app.core.db import Base
import app.models  # noqa: F401

revision = "20260920_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the complete baseline schema for a fresh deployment."""
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Remove the baseline schema. Intended only for disposable environments."""
    Base.metadata.drop_all(bind=op.get_bind())
