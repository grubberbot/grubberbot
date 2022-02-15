import sqlalchemy as sa  # type: ignore[import]
from sqlalchemy.orm import Session  # type: ignore[import]
import pandas as pd  # type: ignore[import]
import os
from pprint import pprint

GSA_PATH = 'C:/Users/pault/Documents/keys/google_service_account.json'

class SAEngine:

    def __enter__(self):

        url = sa.engine.URL.create(
            drivername='mysql+mysqlconnector',
            host='34.70.253.226',
            username='root',
            password='6cst4P5kmI06Mbua',
            #host=os.environ["MYSQL_CONNECTION_NAME"],
            #username=os.environ["MYSQL_USER"],
            #password=os.environ["MYSQL_PASS"],
        )
        pprint(url)

        engine = sa.create_engine(
            url,
            future=True,
            connect_args={'use_pure': True},
            echo=True,
            echo_pool=True,
        )
        return engine

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def print_table(metadata, schema: str, table: str) -> None:
    schema_table = f"{schema}.{table}"
    for column in metadata.tables[schema_table].columns:
        column = str(column).split(".")[-1]
        column = getattr(metadata.tables[schema_table].c, column)
        print(repr(column))


# Convert sqlalchemy result to pandas dataframe
def sa_to_df(result: sa.engine.CursorResult) -> pd.DataFrame:
    df = pd.DataFrame(result.all(), columns=result.keys())
    return df


def main():

    # Metadata object holds database metadata
    metadata = sa.MetaData()

    # Load up metadata from the chess.abuse_report table
    with SAEngine() as engine:
        metadata.reflect(bind=engine)

    for table in metadata.sorted_tables:
        print_table(table)

    return

    # Generate a sql query
    stmt = (
        sa.select(
            table.c.status_id,
            table.c.abuser_user_id,
            table.c.reporter_user_id,
            table.c.date,
        )
        .order_by(sa.desc(table.c.date))
        .filter(table.c.date < present)
        .filter(table.c.date > past)
        .limit(10)
    )

    # Print the sql query
    print(repr(stmt))

    # Execute the sql query
    with SAEngine() as engine:
        with Session(engine) as session:
            result = session.execute(stmt)

    # Convert result to pandas dataframe and print
    df = sa_to_df(result)
    print(df)

if __name__ == '__main__':
    main()
