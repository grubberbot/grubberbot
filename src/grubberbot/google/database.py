import os
import sys
import typing
from pprint import pprint

import pymysql
import sqlalchemy as sa
import sqlalchemy.orm
import yaml
from google.cloud.sql.connector import connector
from google.cloud.sql.connector.connector import Connector
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build as gs_build

import grubberbot as gb
from grubberbot.utils.funcs import ParseArgs


class Database:
    def __init__(
        self,
        args: ParseArgs,
        verbose: bool = False,
    ):
        self.engine_kwargs = {"future": True}
        if verbose:
            self.engine_kwargs.update(**{"echo": True, "echo_pool": True})

        self.args = args
        if self.args.gsa is None:
            self.engine = self._create_engine_local()
        else:
            self.engine = self._create_engine_cloud(self.args.gsa)

    def _create_engine_cloud(
        self,
        credentials: Credentials,
        use_root=False,
        **kwargs,
    ) -> sa.engine.Engine:

        if use_root and self.args.yml is not None:
            kwargs.update(
                {
                    "user": "postgres",
                    "password": self.args.yml["POSTGRESQL_PASSWORD"],
                }
            )
        else:
            kwargs.update(
                {
                    "user": "grubberbot@grubberbot.iam",
                    "enable_iam_auth": True,
                }
            )

        def getconn() -> pymysql.connections.Connection:
            base_conn = Connector(credentials=credentials)
            instance_connection_string = "grubberbot:us-central1:grubberbot-postgresql"
            conn: pymysql.connections.Connection = base_conn.connect(
                instance_connection_string=instance_connection_string,
                driver="pg8000",
                db="grubber",
                **kwargs,
            )
            return conn

        engine = sa.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            **self.engine_kwargs,
        )

        return engine

    def _create_engine_local(
        self,
        **kwargs,
    ) -> sa.engine.Engine:
        url = sa.engine.URL.create(  # type: ignore[attr-defined]
            drivername="postgresql+pg8000",
            username="grubberbot@grubberbot.iam",
            password="password",
            host="db",
            database="grubber",
            port="5432",
        )
        engine = sa.create_engine(url, **self.engine_kwargs)
        return engine

    def init_database(self):
        # 'create database grubber;'
        # '\connect grubber;'
        # 'grant all privileges on database grubber to "grubberbot@grubberbot.iam";'
        pass


def main():
    args = gb.utils.funcs.ParseArgs()
    db = Database(args, verbose=True)

    print(db.engine)
    metadata = sa.MetaData()
    metadata.reflect(db.engine)
    print(metadata.tables.keys())


if __name__ == "__main__":
    main()
