from google.oauth2 import service_account
import googleapiclient.discovery

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/drive",
    'https://www.googleapis.com/auth/sqlservice.admin',
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
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials,)

class SQL:
    def __init__(
        self,
        gs_credentials: str,
    ):
        credentials = service_account.Credentials.from_service_account_file(
            gs_credentials,
            scopes=SCOPES,
        )
        self.service = googleapiclient.discovery.build('sqladmin', 'v1beta4', credentials=credentials, http='34.70.253.226')
        print(self.service)


def main():
    gs_credentials = 'C:/Users/pault/Documents/keys/google_service_account.json'
    calendar = Calendar(gs_credentials)
    sql = SQL(gs_credentials)


if __name__ == '__main__':
    main()
