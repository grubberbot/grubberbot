"""rapid league users.

Revision ID: 350251f34a1d
Revises: 1df1a0cbadab
Create Date: 2022-03-04 20:14:14.623138
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '350251f34a1d'
down_revision = '1df1a0cbadab'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('create schema discord')
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('discord_id', sa.Integer, nullable=False, unique=True),
        sa.Column('chesscom_id', sa.Integer),
        sa.Column('chesscom_name', sa.String(64)),
        schema='discord',
    )



def downgrade():
    op.drop_table('discord.user')
    op.execute('drop schema discord')
