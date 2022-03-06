
def main(verbose: bool=False):

    # Parse command line arguments
    args = gb.utils.funcs.ParseArgs()

    # Initialize database
    db = gb.google.database.Database(args, verbose=verbose)
    db.alembic_upgrade_head()
    db.load_schemas()

if __name__ == '__main__':
    main(verbose=True)
