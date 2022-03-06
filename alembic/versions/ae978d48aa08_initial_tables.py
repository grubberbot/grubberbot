"""initial_tables.

Revision ID: ae978d48aa08
Revises:
Create Date: 2022-02-23 14:02:47.564002
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "ae978d48aa08"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('create schema twitch')
    op.create_table(
        'tts_permissions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(64), nullable=False),
        schema='twitch',
    )


def downgrade():
    op.drop_table('twitch.tts_permissions')
    op.execute('drop schema twitch')
