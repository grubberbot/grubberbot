"""empty message

Revision ID: 20bed5e1df6b
Revises:
Create Date: 2022-02-15 12:50:29.632756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20bed5e1df6b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.execute('create schema twitch')

    # Discord user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('twitch_id', sa.Integer, nullable=False, unique=True),
        sa.Column('twitch_name', sa.String(128), nullable=False),
        schema='twitch',
    )


def downgrade():
    op.execute('drop schema twitch')
    op.drop_table('user', schema='twitch')
