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
