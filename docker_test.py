import grubberbot as gb
import sqlalchemy as sa


def main():

    credentials = None
    db = gb.google.database.Database(credentials, verbose=True)
    engine = db.engine

    print(engine)
    metadata = sa.MetaData()
    metadata.reflect(engine)
    print(metadata)
    print(metadata.tables.keys())
    print('done')


if __name__ == "__main__":
    main()
