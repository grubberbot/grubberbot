import sqlalchemy as sa

import grubberbot as gb


def main():
    print('testing dev')

    args = gb.utils.funcs.ParseArgs()
    db = gb.utils.Database(args)
    db.alembic_upgrade_head()
    print('upgraded head')
    db.load_schemas()
    print('loaded schemas')

    rl = gb.discord.rapid_league.RapidLeague(db)

    user0 = {
        'discord_id': 8,
        'chesscom_id': 9,
        'chesscom_name': 'pg',
    }
    user1 = {
        'discord_id': 20,
        'chesscom_id': 19,
        'chesscom_name': 'll',
    }

    rl.set_user(**user0)
    rl.set_user(**user1)
    df = rl.get_user(user0['discord_id'])
    print(df)
    df = rl.get_user(user1['discord_id'])
    print(df)
    df = rl.del_user(user0['discord_id'])
    print(df)
    

if __name__ == "__main__":
    main()
