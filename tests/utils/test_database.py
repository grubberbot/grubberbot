import pandas as pd
import pytest
import sqlalchemy as sa

import alembic.config
import grubberbot as gb


@pytest.fixture
def db():
    args = gb.utils.funcs.ParseArgs()
    pytest_db = gb.utils.Database(args, verbose=False)
    pytest_db.alembic_upgrade_head()
    pytest_db.load_schemas()
    return pytest_db


def test_exists_twitch_tts(db):
    assert "twitch.tts" in db.metadata.tables.keys()


def test_exists_twitch_tts_permissions(db):
    assert "twitch.tts_permissions" in db.metadata.tables.keys()


def test_exists_discord_user(db):
    assert "discord.user" in db.metadata.tables.keys()


def test_set_user(db):
    users = [
        {"discord_id": 1, "chesscom_name": "pawngrubber"},
        {"discord_id": 3, "chesscom_name": "lalizig"},
    ]

    for user in users:
        gb.discord.rapid_league.set_user(db, **user)

    df = gb.discord.rapid_league.get_user(db, users[0]["discord_id"])
    val = df["chesscom_name"][0]
    assert val == users[0]["chesscom_name"]


if __name__ == "__main__":
    pass