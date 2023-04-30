import typing

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import Session

from grubberbot.utils import Database, chesscom
from grubberbot.utils.funcs import ParseArgs

# TODO: set_user chesscom_id is different
# TODO: make str outputs


def set_user(
    db: Database,
    discord_id: int,
    chesscom_name: str,
):
    # TODO: update to sqlalchemy ORM instead of core

    chesscom_id = chesscom.get_player_id(chesscom_name)
    if chesscom_id is None:
        msg = f"{discord_id}: {chesscom_name} is not a chesscom name"
        return msg

    table = db.metadata.tables["discord.user"]
    stmt = (
        sa.dialects.postgresql.insert(table)
        .values(
            discord_id=discord_id,
            chesscom_id=chesscom_id,
            chesscom_name=chesscom_name,
        )
        .on_conflict_do_update(
            index_elements=[table.c.discord_id],
            set_={
                "chesscom_id": chesscom_id,
                "chesscom_name": chesscom_name,
            },
        )
    )

    with db.engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

    msg = f"{discord_id} is linked to {chesscom_name}"
    return msg


def get_user(
    db: Database,
    discord_id: int,
):
    table = db.metadata.tables["discord.user"]
    stmt = sa.select(table).where(table.c.discord_id == discord_id)
    df = db.run_select(stmt)
    return df


def del_user(
    db: Database,
    discord_id: int,
):
    table = db.metadata.tables["discord.user"]
    stmt = sa.delete(table).where(table.c.discord_id == discord_id)
    df = db.run_delete(stmt)
    return df


def init_database(db: Database):
    pass


def main(verbose: bool = False):
    pass


if __name__ == "__main__":
    main(verbose=True)
