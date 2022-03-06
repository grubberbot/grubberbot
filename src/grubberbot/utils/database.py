import os
import sys
import typing

import pandas as pd
import pymysql
import sqlalchemy as sa
import sqlalchemy.orm
import yaml
from google.cloud.sql.connector import connector
from google.cloud.sql.connector.connector import Connector
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build as gs_build

import alembic.config
from grubberbot.utils.funcs import ParseArgs


def sa_to_df(result: sa.engine.CursorResult) -> pd.DataFrame:
    df = pd.DataFrame(result.all(), columns=result.keys())
    return df


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

        self.metadata = sa.MetaData()

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
        engine = sa.create_engine(url, **kwargs, **self.engine_kwargs)
        return engine

    def alembic_upgrade_head(self):
        # 'create database grubber;'
        # '\connect grubber;'
        # 'grant all privileges on database grubber to "grubberbot@grubberbot.iam";'

        argv = [
            # '--raiseerr',
            "upgrade",
            "head",
        ]
        alembic.config.main(argv=argv)

    def load_schemas(self):
        insp = sa.inspect(self.engine)
        schemas = insp.get_schema_names()
        for schema in schemas:
            self.metadata.reflect(self.engine, schema=schema)
        return self.metadata

    def run_select(
        self,
        stmt,
        filename: typing.Optional[str] = None,
        load_cache: bool = False,
    ) -> pd.DataFrame:
        if load_cache and filename is not None:
            if os.path.exists(filename):
                return pd.read_parquet(filename)
        with sa.orm.Session(self.engine) as session:
            result = session.execute(stmt)
        df = sa_to_df(result)
        if filename is not None:
            df.to_parquet(filename)
        return df

    def run_delete(
        self,
        stmt,
    ):
        with sa.orm.Session(self.engine) as session:
            session.execute(stmt)

    def print_table(self, schema: str, table: str):
        schema_table = f"{schema}.{table}"
        for column in self.metadata.tables[schema_table].columns:
            # column = str(column).split(".")[-1]
            # column = getattr(self.metadata.tables[schema_table].c, column)
            print(repr(column))


def main():
    pass


if __name__ == "__main__":
    main()
