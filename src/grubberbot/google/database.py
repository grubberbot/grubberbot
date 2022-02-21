import os
from pprint import pprint

from google.oauth2 import service_account
from googleapiclient.discovery import build as gs_build

import sys
import yaml
import pymysql
import sqlalchemy
from google.cloud.sql.connector import connector
from google.cloud.sql.connector.connector import Connector

import grubberbot as gb

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/sqlservice.admin",
]


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

def init_connection_engine(credentials, url, **kwargs) -> sqlalchemy.engine.Engine:
    print(credentials)
    print(url)
    pprint(kwargs)
    def getconn() -> pymysql.connections.Connection:
        base_conn = Connector(credentials=credentials)
        #conn: pymysql.connections.Connection = connector.connect(
        conn: pymysql.connections.Connection = base_conn.connect(
            **kwargs,
        )
        return conn

    engine = sqlalchemy.create_engine(
        url,
        creator=getconn,
    )
    return engine


def local_init():
    pass


def init_postgres():
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
    gs_json_path = os.path.join(credential_directory, 'google_service_account.json')
    gs_yaml_path = os.path.join(credential_directory, 'grubberbot.yml')
    yml_creds = load_credentials(gs_yaml_path)

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gs_json_path

    credentials = service_account.Credentials.from_service_account_file(
        gs_json_path,
        scopes=SCOPES,
    )

    USE_MYSQL = 0
    if USE_MYSQL:
        user='root'
        password = yml_creds['MYSQL_PASSWORD']
        driver='pymysql'
        url = 'mysql+pymysql://'
        instance_connection_string = 'grubberbot:us-central1:grubberbot-mysql',
    else:
        user='postgres'
        password = yml_creds['POSTGRESQL_PASSWORD']
        driver='pg8000'
        url = 'postgresql+pg8000://'
        instance_connection_string = 'grubberbot:us-central1:grubberbot-postgresql'

    '''
    # Root access
    engine = init_connection_engine(
        credentials=None,
        url=url,

        instance_connection_string = instance_connection_string,
        driver=driver,
        user=user,
        password=password,
        db='grubber',
        #enable_iam_auth=True,
    )
    print(engine)
    '''

    engine = init_connection_engine(
        credentials=credentials,
        url=url,

        instance_connection_string = instance_connection_string,
        driver=driver,
        user='grubberbot@grubberbot.iam',
        db='grubber',
        enable_iam_auth=True,
    )
    print(engine)

    metadata = sqlalchemy.MetaData()
    metadata.reflect(engine)

    #with init_connection_engine() as engine:
    print(metadata.tables.keys())

    '''
    calendar = Calendar(gs_json_path)
    sql = SQL(gs_json_path)
    '''


if __name__ == "__main__":
    main()
