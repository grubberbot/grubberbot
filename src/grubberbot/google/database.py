import os
import sys
from pprint import pprint

import pymysql
import sqlalchemy as sa
import yaml
from google.cloud.sql.connector import connector
from google.cloud.sql.connector.connector import Connector
from google.oauth2 import service_account
from googleapiclient.discovery import build as gs_build

import grubberbot as gb

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/sqlservice.admin",
]

# TODO: typing for credentials

class Database:

    def __init__(
        self,
        credentials,
        verbose: bool=False,
    ):
        self.engine_kwargs = {'future': True}
        if verbose:
            self.engine_kwargs.update(**{ "echo": True, "echo_pool": True})

        if credentials is None:
            self.engine = self._create_engine_local()
        else:
            self.engine = self._create_engine_cloud(credentials)


    def _create_engine_cloud(self, credentials, use_root=False, **kwargs,) -> sa.engine.Engine:

        if use_root:
            kwargs.update({
                'user': "postgres",
                'password': yml_creds["POSTGRESQL_PASSWORD"],
            })
        else:
            kwargs.update({
                'user': "grubberbot@grubberbot.iam",
                'enable_iam_auth': True,
            })

        def getconn() -> pymysql.connections.Connection:
            base_conn = Connector(credentials=credentials)
            conn: pymysql.connections.Connection = base_conn.connect(
                instance_connection_string='grubberbot:us-central1:grubberbot-postgresql',
                driver='pg8000',
                db='grubber',
                **kwargs,
            )
            return conn

        engine = sa.create_engine(
            'postgresql+pg8000://',
            creator=getconn,
            **self.engine_kwargs,
        )

        return engine

    def _create_engine_local(self, **kwargs,) -> sa.engine.Engine:
        url = sa.engine.URL.create(
            drivername='postgresql+pg8000',
            username='grubberbot@grubberbot.iam',
            password='password',
            host="db",
            database='grubber',
            port='5432',
        )
        engine = sa.create_engine(url, **self.engine_kwargs)
        return engine

def create_engine(credentials, local: bool, verbose: bool, **kwargs,) -> sa.engine.Engine:
    if local:
        engine = create_engine_local(credentials=credentials, verbose=verbose, **kwargs)
    else:
        engine = create_engine_cloud(credentials=credentials, verbose=verbose, **kwargs)
    return engine

class Calendar:
    def __init__(
        self,
        gs_credentials: str,
    ):
        credentials = service_account.Credentials.from_service_account_file(
            gs_credentials,
            scopes=SCOPES,
        )
        self.service = gs_build(
            "calendar",
            "v3",
            credentials=credentials,
        )


class SQL:
    def __init__(
        self,
        gs_credentials: str,
    ):
        credentials = service_account.Credentials.from_service_account_file(
            gs_credentials,
            scopes=SCOPES,
        )

        with gs_build("sqladmin", "v1beta4", credentials=credentials) as service:
            req = service.instances().get(
                project="grubberbot",
                instance="grubberbot-mysql",
            )

        resp = req.execute()
        import json

        print(json.dumps(resp, indent=2))


def load_credentials(credentials_directory):
    with open(credentials_directory, "r") as f:
        credentials = yaml.safe_load(f)
    return credentials


def local_init(verbose: bool):
    pass


def init_database():
    # Create database grubber
    # 'create database grubber;'
    # Connect to grubber
    # '\connect grubber;'
    # Grant all privileges in database grubber to user grubberbot@grubberbot.iam
    # 'grant all privileges on database grubber to "grubberbot@grubberbot.iam";'
    pass


def main():

    args = gb.utils.funcs.parse_args()
    credential_directory = os.path.normpath(args.credential_directory)
    gs_json_path = os.path.join(credential_directory, "google_service_account.json")
    gs_yaml_path = os.path.join(credential_directory, "grubberbot.yml")
    yml_creds = load_credentials(gs_yaml_path)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gs_json_path

    credentials = service_account.Credentials.from_service_account_file(
        gs_json_path,
        scopes=SCOPES,
    )

    engine = create_engine(credentials, local=True, verbose=True)
    print(engine)

    metadata = sa.MetaData()
    metadata.reflect(engine)

    # with init_connection_engine() as engine:
    print(metadata.tables.keys())

    """
    calendar = Calendar(gs_json_path)
    sql = SQL(gs_json_path)
    """


if __name__ == "__main__":
    main()
