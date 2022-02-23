import argparse
import os
import typing

import yaml
from google.oauth2.service_account import Credentials

GSA_NAME = "google_service_account.json"
YML_NAME = "grubberbot.yml"
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/sqlservice.admin",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        "--credential_directory",
        help="Directory where login credentials are data",
    )
    parser.add_argument(
        "-e",
        "--example",
        help="Unused, just an example",
    )

    args = parser.parse_args()
    return args


class ParseArgs:
    args: argparse.Namespace
    yml: typing.Union[dict[str, str], None]
    gsa: typing.Union[Credentials, None]

    def __init__(self):
        self.args = parse_args()
        self.yml = self._get_yml_creds()
        self.gsa = self._get_gsa_creds()

    def _get_yml_creds(self) -> typing.Union[dict[str, str], None]:

        if self.args.credential_directory is None:
            return None

        path = os.path.join(os.path.normpath(self.args.credential_directory), YML_NAME)
        with open(path, "r") as f:
            yml_creds = yaml.safe_load(f)

        return yml_creds

    def _get_gsa_creds(self) -> typing.Union[Credentials, None]:

        if self.args.credential_directory is None:
            return None

        path = os.path.join(os.path.normpath(self.args.credential_directory), GSA_NAME)
        credentials = Credentials.from_service_account_file(path, scopes=SCOPES)
        return credentials
