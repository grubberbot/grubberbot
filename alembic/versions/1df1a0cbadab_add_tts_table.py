"""add tts table.

Revision ID: 1df1a0cbadab
Revises: ae978d48aa08
Create Date: 2022-02-23 15:09:33.072182
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "1df1a0cbadab"
down_revision = "ae978d48aa08"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column(
            "tts_permissions_id", sa.Integer, sa.ForeignKey("twitch.tts_permissions.id")
        ),
        schema="twitch",
    )


def downgrade():
    op.drop_table("twitch.tts")
