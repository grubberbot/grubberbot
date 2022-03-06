from grubberbot.utils import Database
import typing
import sqlalchemy as sa
from sqlalchemy.orm import Session
import pandas as pd


class RapidLeague:

    def __init__(self, db: Database):
        self.db = db

    def set_user(
        self,
        discord_id: int,
        chesscom_id: int,
        chesscom_name: str,
    ):

        # TODO: update to sqlalchemy ORM instead of core

        table = self.db.metadata.tables['discord.user']
        stmt = (
            sa.dialects.postgresql.insert(table)
            .values(
                discord_id=discord_id,
                chesscom_id=chesscom_id,
                chesscom_name=chesscom_name,
            )
            .on_conflict_do_update(
                index_elements=[table.c.discord_id],
                set_=dict(
                    chesscom_id=chesscom_id,
                    chesscom_name=chesscom_name,
                )
            )
        )

        with self.db.engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

    def get_user(
        self,
        discord_id: int,
    ):
        table = self.db.metadata.tables['discord.user']
        stmt = (
            sa.select(table)
            .where(table.c.discord_id == discord_id)
        )
        df = self.db.run_select(stmt)
        return df

    def del_user(
        self,
        discord_id: int,
    ):
        table = self.db.metadata.tables['discord.user']
        stmt = (
            sa.delete(table)
            .where(table.c.discord_id == discord_id)
        )
        df = self.db.run_delete(stmt)
        return df




def init_database(db: Database):
    pass


def main(verbose: bool=False):

    # Parse command line arguments
    args = gb.utils.funcs.ParseArgs()

    # Initialize database
    db = Database(args, verbose=verbose)
    db.alembic_upgrade_head()
    db.load_schemas()

if __name__ == '__main__':
    main(verbose=True)
