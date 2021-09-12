from discord.ext import commands
from typing import Optional
from pprint import pformat, pprint
from dotenv import load_dotenv
from tqdm import tqdm
import discord
import pandas as pd
import logging
import datetime
import os
import numpy as np
import re

import funcs_general as fgg
import funcs_chesscom as fcc
import funcs_league as flg

pd.options.mode.chained_assignment = None

DISCORD_USERS_PARQUET = 'data/discord_users.parquet'
DISCORD_HISTORY_PARQUET = 'data/discord_history.parquet'
LOG_FILE = 'data/grubberbot.log'
GRUBBER_MENTION = '<@490529572908171284>'
GUILD_NAME = "pawngrubber's server"
ANNOUNCE_SUB_CHANNEL = 'grubberbot-debug'
ELO_EXTRA = 100

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
)

GENERAL_ERROR_MESSAGE = '{mention} `!{name}` error, get help with `!help {name}`'
TIME_CONTROL = '900+10'
MODERATOR_ROLES = [
    'The Grubber',
    'Mods',
    'Cool People',
]
WHITE_RESULTS_CODES = {
    'win': 1,
    'checkmated': -1,
    'agreed': 0,
    'repetition': 0,
    'timeout': -1,
    'resigned': -1,
    'stalemate': 0,
    'lose': -1,
    'insufficient': 0,
    '50move': 0,
    'abandoned': -1,
    'kingofthehill': -1,
    'threecheck': -1,
    'timevsinsufficient': 0,
    'bughousepartnerlose': -1
}
DISPLAY_RESULT = {
    1: '1-0',
    0: '1/2-1/2',
    -1: '0-1',
}

LDB = flg.LeagueDatabase()

################ General commands
async def get_all_threads(guild):
    threads = list(guild.threads)
    threads = threads + [
        t
        for c in guild.channels if hasattr(c, 'archived_threads')
        async for t in c.archived_threads() if 'league' in c.name
    ]
    return threads

async def announce_pairing(bot, guild):
    season_name = fgg.get_month(0)
    week_num = 2

    df = LDB.get_games_by_week(season_name, week_num)
    channel = discord.utils.get(guild.channels, name='league-scheduling')

    rows = [row for row in df.itertuples()]
    for row in rows:
        title = fgg.gen_pairing_thread_name(
            row.game_id,
            season_name,
            week_num,
            row.white_discord_name,
            row.black_discord_name,
        )
        thread = await channel.create_thread(
            name=title,
            #message=f'{GRUBBER_MENTION} test123',
            type=discord.ChannelType.public_thread,
            reason='testing-purposes',
        )
        message = (
            'Hi! September Rapid League Week 2 has started, please use '
            'this thread so I can help you.  This thread is for:\n'
            '* Scheduling your rapid game.  Any conversation outside of this '
            'thread cannot be regulated by moderators.  You have until '
            'September 16th 11:59pm ET to schedule your game.\n'
            '* Posting your result.  When your game is done please use '
            '`!set_result <url>` (in this thread) where `<url>` is a link to the '
            'chess.com game.\n\n'
            'If you need a substitute please ask in the #league-moderation room.\n\n'
            f'<@{row.white_discord_id}> will play white\n'
            f'<@{row.black_discord_id}> will play black\n'
            'See the pairings online: https://docs.google.com/spreadsheets/d/1SFH7ntDpDW7blX_xBU_m_kSmvY2tLXkuwq-TOM9wyew/edit#gid=2039965781'
        )
        print(message)
        await thread.send(message)
        print(title)

async def announce_substitute(mention, team_mention, guild, seed_id, week_num):
    #guild = ctx.guild
    channel = discord.utils.get(guild.channels, name=ANNOUNCE_SUB_CHANNEL)
    title = fgg.gen_substitute_thread_name(seed_id)
    thread = await channel.create_thread(
        name=title,
        type=discord.ChannelType.public_thread,
        reason='testing-purposes',
    )

    message = (
        f'{mention} has requested a substitute on week {week_num}.  '
        f'Any eligible member of team {team_mention} may play '
        f'for {mention} by using `!claim_substitute {seed_id}` '
        f'in this thread.  '

    )

    print(title)
    print(message)
    await thread.send(message)
    return thread

def save_user_data(guild):
    members = list(guild.members)
    df_dict = {
        'discord_id': [member.id for member in tqdm(members)],
        'discord_name': [str(member) for member in tqdm(members)],
    }
    df = pd.DataFrame(df_dict)
    df.to_parquet(DISCORD_USERS_PARQUET)
    print(f'updated {DISCORD_USERS_PARQUET}')

async def save_discord_history(guild):
    data = {
        'date': [],
        'discord_id': [],
        'name': [],
        'text': [],
        'channel': [],
        'is_thread': [],
    }

    LIMIT = None
    channels = [(False, c) for c in guild.channels]
    threads = [(True, t) for t in guild.threads]
    threads = threads + [
        (True, t)
        for c in guild.channels
        if hasattr(c, 'archived_threads')
        async for t in c.archived_threads()
        if 'league' in c.name
    ]
    combined = channels + threads
    for is_thread, channel in tqdm(combined):
        print()
        print(is_thread, channel.name)
        if hasattr(channel, 'history'):
            msgs = await channel.history(limit=LIMIT).flatten()
            for msg in msgs:
                data['date'].append(msg.created_at)
                data['discord_id'].append(msg.author.id)
                data['name'].append(str(msg.author))
                data['text'].append(msg.content)
                data['channel'].append(channel.name)
                data['is_thread'].append(is_thread)

    df = pd.DataFrame(data)
    df.to_parquet(DISCORD_HISTORY_PARQUET)
    print(f'updated {DISCORD_HISTORY_PARQUET}')

def update_google_sheet():
    # Sign-up info
    season_name = fgg.get_month()
    df = LDB.update_signup_info(season_name)
    fgg.df_to_sheet(df, sheet=0, title=season_name)

    # Standings
    df = LDB.get_season_games(season_name)
    teams = list(df['white_team_name']) + list(df['black_team_name'])
    teams = set(teams)
    result_dict = {1: 3, 0: 1, -1: 0}
    white_dict = [
        {
            'score': result_dict[row.result],
            'team': row.white_team_name,
            'rapid_rating': row.white_rapid_rating,
            'discord_name': row.white_discord_name,
            'chesscom': row.white_chesscom,
        }
        for row in df.itertuples()
    ]
    black_dict = [
        {
            'score': result_dict[row.result * (-1)],
            'team': row.black_team_name,
            'rapid_rating': row.black_rapid_rating,
            'discord_name': row.black_discord_name,
            'chesscom': row.black_chesscom,
        }
        for row in df.itertuples()
    ]
    seeds = white_dict + black_dict
    members = {team: [] for team in teams}
    for seed in seeds:
        key = (seed['discord_name'], seed['chesscom'], seed['rapid_rating'])
        members[seed['team']].append(key)
    members = {k: {m: 0 for m in list(set(v))} for k, v in members.items()}
    for seed in seeds:
        key = (seed['discord_name'], seed['chesscom'], seed['rapid_rating'])
        members[seed['team']][key] += seed['score']

    members = {
        t: sorted([[u[0], u[1], u[2], s, ''] for u, s in m.items()], key=lambda x: x[2])
        for t, m in members.items()
    }
    for team in teams:
        points = sum(row[3] for row in members[team])
        val = [['', '', '', points, ''], ['', '', '', '', '']]
        members[team] = val + members[team]

    cols = [[
        e for team in teams for e in
        [team, 'Chesscom', 'Rapid Elo', 'Points', '']
    ]]
    max_length = max(len(v) for k, v in members.items())
    for k in members.keys():
        while len(members[k]) < max_length:
            members[k].append(['', '', '', ''])
    arr = []
    for i in range(max_length):
        arr.append([])
        for team in teams:
            row = members[team][i]
            arr[i] = arr[i] + members[team][i]
    arr = cols + arr
    fgg.arr_to_sheet(arr, sheet=1)

    # Pairings
    for week_num in [1, 2, 3, 4]:
        season_name = fgg.get_month(0)
        df = LDB.get_games_by_week(season_name, week_num)
        to_sheet = df[[
            'game_id',
            'white_discord_name',
            'white_chesscom',
            'white_rapid_rating',
            'black_rapid_rating',
            'black_chesscom',
            'black_discord_name',
            'schedule',
            'result',
            'url',
        ]]
        to_sheet['result'] = [
            DISPLAY_RESULT[r] if r in DISPLAY_RESULT else '-'
            for r in np.array(to_sheet['result'])
        ]
        fgg.df_to_sheet(to_sheet, sheet=week_num+1)

    # Next season sign-up info
    season_name = fgg.get_month(1)
    df = LDB.update_signup_info(season_name)
    fgg.df_to_sheet(df, sheet=6, title=season_name)

################ Exception handling
def gen_chesscom_username_error(mention, user_mention, mod=False):
    if mod:
        error_command = '!mod_set_chesscom'
    else:
        error_command = '!set_chesscom'
    message = (
        f'{mention} User {user_mention} has not yet linked to chesscom, '
        f' use {error_command}'
    )
    return message

def on_command_error(ctx, exception):
    user = ctx.message.author
    mention = user.mention

    # If user doesn't have permissions
    if isinstance(exception, commands.errors.CheckFailure):
        message = 'You do not have the correct role for this command'
        logging_message = f'{user} || {ctx.message.clean_content} || {message}'
        print(logging_message)
        logging.error(logging_message)
        return message

    # Parse out the command from the message
    command_name = ctx.message.content.split(' ')[0][1:]
    message = f'Error, use `!help {command_name}`'

    logging_message = (
        f'{datetime.datetime.now()} || {user} '
        f'|| {ctx.message.clean_content} || {message} || {exception}'
    )
    print(logging_message)
    logging.error(logging_message)

    # TODO: give user list of commands
    return message

    # Send help message and log things
    message = GENERAL_ERROR_MESSAGE.format_map({
        'mention': ctx.message.author.mention,
        'name': command_name
    })
    logging_message = '\n'.join([
        f'MESSAGE: {ctx.message.clean_content}',
        str(ctx.message),
        str(exception),
        ''
    ])
    logging.error(logging_message)
    print(datetime.datetime.now(), 'Exception found')
    print(logging_message)
    return message

######################## Define league membership commands
async def general_set_chesscom(mention, user, chesscom):
    if not LDB.chess_db.get_exists(chesscom):
        message = f'{mention} Chess.com username not found: `{chesscom}`'
        return message

    user_data = LDB.get_user_data(user.id)
    LDB.set_chesscom(user.id, str(user), chesscom)
    if len(user_data) < 1:
        message = (
            f'{mention} successfully linked '
            f'{user.mention} to Chess.com username `{chesscom}`'
        )
    else:
        message = (
            f'{mention} user {user.mention} was linked to Chess.com username '
            f'`{user_data["chesscom"][0]}` but is now linked to `{chesscom}`'
        )
    return message

@commands.command(name='set_chesscom')
async def user_set_chesscom(ctx, chesscom: str):
    '''Link your chess.com account to your discord account'''
    user = ctx.message.author
    mention = user.mention
    message = await general_set_chesscom(mention, user, chesscom)
    await ctx.send(message)

@commands.command(name='mod_set_chesscom')
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_set_chesscom(ctx, discord_mention: discord.Member, chesscom: str):
    '''Link a chess.com account to a discord account'''
    mention = ctx.message.author.mention
    message = await general_set_chesscom(mention, discord_mention, chesscom)
    await ctx.send(message)

async def general_join(mention, user, season_name, join_type, mod=False):
    join_error_message = f'{mention} Errors:'

    user_data = LDB.get_user_data(user.id)
    player_args = ['player', 'substitute']

    errors = []
    if len(user_data) < 1:
        errors.append(gen_chesscom_username_error(mention, user.mention, mod))
    else:
        chesscom = user_data['chesscom'][0]
        count_info = LDB.chess_db.get_count(chesscom)
        num_games = count_info['total_count']
        num_rapid_games = count_info['rapid_count']
        if not join_type in player_args:
            errors.append(f'Expected `{player_args}`, instead found: `{join_type}`')
        if num_rapid_games < 10:
            errors.append(
                f'Minimum 10 rapid games required, `{chesscom}` '
                f'has played only `{num_rapid_games}` rapid games'
            )
        if num_games < 50:
            errors.append(
                f'Minimum 50 games of any time control required, `{chesscom}`'
                f' has played only `{num_games}` games'
            )

    if errors:
        errors = ['* ' + e for e in errors]
        errors = [join_error_message] + errors
        message = '\n'.join(errors)
    else:
        LDB.league_join(
            season_name,
            user.id,
            join_type=='player',
        )
        message = '\n'.join([
            f'{mention} added {user.mention} to the league `{season_name}` season',
            f'* Chess.com username: `{chesscom}`',
            f'* Signed up as a: `{join_type}`',
        ])
    return message

@commands.command(name='join_current')
async def user_join_current(ctx):
    '''Join the current season of the rapid league as a substitute'''
    user = ctx.message.author
    mention = user.mention
    season_name = fgg.get_month(0)
    message = await general_join(mention, user, season_name, 'substitute')
    await ctx.send(message)

@commands.command(name='mod_join_current')
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_join_current(ctx, user: discord.Member, join_type: str):
    '''Add someone to the current season of the rapid league
        <user> Ping someone with @user'
        <join_type>: either "player" or "substitute"'''
    mention = ctx.message.author.mention
    season_name = fgg.get_month(0)
    message = await general_join(mention, user, season_name, join_type, mod=True)
    await ctx.send(message)

@commands.command(name='join_player')
async def user_join_player(ctx):
    '''Join the next season of the rapid league as a player'''
    user = ctx.message.author
    mention = user.mention
    season_name = fgg.get_month(1)
    message = await general_join(mention, user, season_name, 'player')
    await ctx.send(message)

@commands.command(name='mod_join_player')
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_join_player(ctx, user: discord.Member):
    '''Add someone to the next season of the rapid league as a player'''
    mention = ctx.message.author.mention
    season_name = fgg.get_month(1)
    message = await general_join(mention, user, season_name, 'player', mod=True)
    await ctx.send(message)

@commands.command(name='join_substitute')
async def user_join_substitute(ctx):
    '''Join the next season of the rapid league as a substitute'''
    user = ctx.message.author
    mention = user.mention
    season_name = fgg.get_month(1)
    message = await general_join(mention, user, season_name, 'substitute')
    await ctx.send(message)

@commands.command(name='mod_join_substitute')
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_join_substitute(ctx, user: discord.Member, join_type: str):
    '''Add someone to the next season of the rapid league as a substitute'''
    mention = ctx.message.author.mention
    season_name = fgg.get_month(1)
    message = await general_join(mention, user, season_name, 'substitute', mod=True)
    await ctx.send(message)

async def general_leave(mention, user, season_name):
    df = LDB.get_league_info(season_name, user.id)
    if len(df) == 0:
        message = (
            f'{mention} user {user.mention} is not currently signed up '
            f'for the rapid league `{season_name}` season'
        )
    else:
        LDB.league_leave(season_name, user.id)
        message = (
            f'{mention} user {user.mention} has left the '
            f'rapid league `{season_name}` season'
        )
    return message

@commands.command(name='leave_next')
async def user_leave_next(ctx):
    '''To leave the upcoming rapid league season'''
    user = ctx.message.author
    mention = user.mention
    season_name = fgg.get_month(1)
    message = await general_leave(mention, user, season_name)
    await ctx.send(message)

@commands.command(name='mod_leave_next')
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_leave_next(ctx, discord_mention: discord.Member):
    '''Remove user from upcoming league'''
    mention = ctx.message.author.mention
    season_name = fgg.get_month(1)
    message = await general_leave(mention, discord_mention, season_name)
    await ctx.send(message)

@commands.command(name='leave_current')
async def user_leave_current(ctx):
    '''To leave the current rapid league season'''
    user = ctx.message.author
    mention = user.mention
    season_name = fgg.get_month(0)
    message = await general_leave(mention, user, season_name)
    await ctx.send(message)

@commands.command(name='mod_leave_current')
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_leave_current(ctx, discord_mention: discord.Member):
    '''Remove user from current league'''
    mention = ctx.message.author.mention
    season_name = fgg.get_month(0)
    message = await general_leave(mention, discord_mention, season_name)
    await ctx.send(message)

######################### Define commands for setting results
def general_set_result(mention, user, game_id, url=None, mod=False, result=None):

    # Mods bypass everything
    if mod and url is None:
        if result not in [-1, 0, 1]:
            message = (f'Result must be in `{[-1, 0, 1]}`')
        else:
            LDB.set_result(game_id, result, url)
            display_result = DISPLAY_RESULT[result]
            message = f'{mention} Set result for game `{game_id}` to `{display_result}`'
        return message

    # Pull game info from the database
    game_df = LDB.get_game_by_id(game_id)
    if len(game_df) == 0:
        message = f'{mention} Game ID not found, pinging {GRUBBER_MENTION}'
        return message
    game_dict = {c: game_df[c][0] for c in game_df.columns}

    # Verify the user has a real chess.com username
    user_data = LDB.get_user_data(user.id)
    if len(user_data) < 1:
        message = gen_chesscom_username_error(mention, user.mention)
        return message
    chesscom = user_data['chesscom'][0]

    # Get cc_game_id from url
    cc_game_id = fcc.game_id_from_url(url)
    if cc_game_id is None:
        message = (f'{mention} No chesscom game_id found in url')
        return message

    # Get games and index by cc_game_id
    games = fcc.get_game_history_api(chesscom)
    cc_game_id_dict = {fcc.game_id_from_url(game['url']): game for game in games}

    # Make sure the user has played the game in question
    if cc_game_id not in cc_game_id_dict:
        message = f'{mention} Game not found in user game history: {url}'
        return message

    # Log errors about the game
    errors = []
    game = cc_game_id_dict[cc_game_id]
    chesscoms = {
        'white': game['white']['username'].lower(),
        'black': game['black']['username'].lower(),
    }
    if (
        game_dict['white_chesscom'].lower() != chesscoms['white'].lower()
        or game_dict['black_chesscom'].lower() != chesscoms['black'].lower()
    ):
        message = (
            f'Incorrect players, expected: '
            f'White: `{game_dict["white_chesscom"]}` '
            f'Black: `{game_dict["black_chesscom"]}` \n'
            f'Instead found:'
            f'White: `{chesscoms["white"]}` Black: `{chesscoms["black"]}`'
        )
        errors.append(message)
    if game['time_control'] != TIME_CONTROL:
        message = (
            f'Expected time control: `{TIME_CONTROL}` '
            f'Instead got time control: `{game["time_control"]}` '
        )
        errors.append(message)
    if not game['rated']:
        message = f'Game is unrated, all games must be rated.'
        errors.append(message)
    if (
        chesscom.lower() != chesscoms['white'].lower()
        and chesscom.lower() != chesscoms['black'].lower()
    ):
        message = (
            f'Incorrect permissions, user `{chesscom}` must be one '
            f'of the players, instead found `{chesscoms}`'
        )
        errors.append(message)

    if not mod and errors:
        errors = ['* ' + e for e in errors]
        errors = [f'{mention} Errors in setting the result:'] + errors
        message = '\n'.join(errors)
    else:
        if result is None:
            game_result = cc_game_id_dict[cc_game_id]['white']['result']
            result = WHITE_RESULTS_CODES[game_result]
        LDB.set_result(game_id, result, url)
        display_result = DISPLAY_RESULT[result]
        message = f'{mention} Set result for game `{game_id}` to `{display_result}`'
    return message

def title_to_game_id(title):
    game_id = int(title.split(' ')[0][1:])
    return game_id

@commands.command(name='user_set_result')
async def user_set_result(ctx, url):
    '''Use with the game url in a game thread to assign a result to the game'''
    user = ctx.message.author
    mention = ctx.message.author.mention

    if not isinstance(ctx.message.channel, discord.Thread):
        message = 'This command must be used in a game thread'
    else:
        game_id = title_to_game_id(ctx.message.channel.name)
        message = general_set_result(mention, user, game_id, url)
    await ctx.send(message)

@commands.command(name='mod_set_result')
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_set_result(ctx, user: discord.Member, url: str):
    '''Use with the game url in a game thread to assign a result to the game'''
    mention = ctx.message.author.mention

    if not isinstance(ctx.message.channel, discord.Thread):
        message = 'This command must be used in a game thread'
    else:
        game_id = title_to_game_id(ctx.message.channel.name)
        message = general_set_result(mention, user, game_id, url, mod=True)
    await ctx.send(message)

@commands.command(name='mod_custom_result')
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_custom_result(
        ctx,
        user: discord.Member,
        result: int,
        url: Optional[str]=None,
    ):
    '''
    result in `[-1, 0, 1]`, optionally include url (after result) for logging purposes
    '''
    mention = ctx.message.author.mention

    if not isinstance(ctx.message.channel, discord.Thread):
        message = 'This command must be used in a game thread'
    else:
        game_id = title_to_game_id(ctx.message.channel.name)
        message = general_set_result(mention, user, game_id, result=result, mod=True, url=url)
    await ctx.send(message)

######################## Define league substitution commands
async def general_claim_substitute(mention, user, seed_id):

    # Ensure seed_id exists
    df = LDB.get_claim_sub_from(seed_id)
    if len(df) == 0:
        message = (
            f'{mention} Seed ID `{seed_id}` does not exist'
        )
        return message

    team_name = df['team_name'][0]
    season_name = df['season_name'][0]
    week_num = df['week_num'][0]
    chesscom = df['chesscom'][0]
    rapid_rating = LDB.chess_db.get_rating(chesscom)['rapid']
    max_elo = rapid_rating + ELO_EXTRA

    # Ensure player is playing this season
    df = LDB.get_claim_sub_to(season_name, user.id)
    if len(df) == 0:
        message = (
            f'{mention} User {user.mention} is not playing in '
            f'season `{season_name}`'
        )
        return message

    # Ensure the player is on the same team as the one requesting the sub
    new_team_name = df['team_name'][0]
    if team_name != new_team_name:
        message = (
            f'{mention} Error, user {user.mention} is not on team '
            f'`{team_name}` but is instead on team `{new_team_name}`'
        )
        return message

    # Ensure the player is playing less than 2 games
    df = LDB.get_games_by_week(season_name, week_num)
    num_games = len(df)
    if len(df) >= 2:
        message = (
            f'{mention} User {user.mention} is already playing `{len(df)}` '
            f'games this week'
        )
        return message

    # Ensure the player is below ELO_EXTRA
    new_chesscom = df['chesscom'][0]
    new_rapid_rating = LDB.chess_db.get_rating(new_chesscom)['rapid']
    if new_rapid_rating > max_elo:
        message = (
            f'{mention} Error, max Elo for this game is `{max_elo}`, but '
            f'user {user.mention} has a rapid rating of `{new_rapid_rating}`'
        )
        return message

    # Do the substitute
    LDB.update_sub(season_name, seed_id, user.id)
    df = LDB.get_gameid_from_seedid(seed_id)
    game_id = df['game_id'][0]
    white_discord_id = df['white_discord_id'][0]
    black_discord_id = df['white_discord_id'][0]
    threads = await get_all_threads(ctx.guild)
    thread = [t for t in threads if t.name.startswith(f'g{game_id}')][0]

    message = (
        f'Hi! {user.mention} has claimed a substitute for this game.  '
        f'This game will be played where:\n\n'
        f'<@{white_discord_id}> will play white\n'
        f'<@{black_discord_id}> will play black\n\n'
        f'As always, please use this thread so I can help you.  If you '
        f'need a substitute, please ask in the #league-moderation '
        f'room.  This thread is for:\n'
        '* Scheduling your rapid game.  Any conversation outside of this '
        'thread cannot be regulated by moderators.  '
        '* Posting your result.  When your game is done please use '
        '`!set_result <url>` (in this thread) where `<url>` is a'
        f' link to the chess.com game.\n\n'
        'See the pairings online: https://docs.google.com/spreadsheets/d/1SFH7ntDpDW7blX_xBU_m_kSmvY2tLXkuwq-TOM9wyew/edit#gid=2039965781'
    )
    await thread.send(message)

    message = (
        f'{mention} User {user.mention} has successfully claimed a substitute.'
    )
    return message

@commands.command(name='claim_substitute')
async def user_claim_substitute(ctx, seed_id: int):
    '''
        <seed_id> the identifier for the substitution
    '''
    user = ctx.message.author
    mention = user.mention
    message = await general_claim_substitute(mention, user, seed_id)
    await ctx.send(message)

help_text = '\n'.join([
])
@commands.command(name='mod_claim_substitute', help=help_text)
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_claim_substitute(ctx, user: discord.Member, seed_id: int):
    '''
        <user> use @someone
        <seed_id> the identifier for the substitution
    '''
    mention = ctx.message.author.mention
    message = await general_claim_substitute(mention, user, seed_id)
    await ctx.send(message)

async def general_request_substitute(
        mention,
        user,
        is_next_season,
        week_num,
        mod=False,
    ):

    # Verify that sub week is in 1-4
    sub_weeks = list(range(1, 5))
    if week_num not in sub_weeks:
        message = (
            f'{mention} Expected one of `{sub_weeks}`, instead got `{week_num}`'
        )
        return message

    # Get user chesscom
    user_data = LDB.get_user_data(user.id)
    if len(user_data) == 0:
        message = gen_chesscom_username_error(mention, user_mention, mod=False)
        return message
    chesscom = user_data['chesscom'][0]

    # Verify that the user is signed up for the season
    season_name = fgg.get_month(int(is_next_season))
    df = LDB.get_league_info(season_name, user.id)
    if len(df) == 0:
        message = (
            f'{mention} User {user.mention} is not signed up for '
            f'the Rapid League `{season_name}` season'
        )
        return message

    LDB.request_sub(season_name, week_num, user.id)
    message = (
        f'{mention} user {user.mention} has requested a substitute on '
        f'week {week_num} of the rapid league `{season_name}` season'
    )

    df = LDB.get_sub_announce(season_name, week_num, user.id)
    print(df)
    if len(df) > 0:
        seed_id = df['seed_id'][0]
        team_name = df['team_name'][0]
        guild = ctx.guild
        team_mention = discord.utils.get(guild.roles, name=team_name).mention,
        await announce_substitute(
            user.mention,
            team_mention,
            guild,
            df['seed_id'][0],
            week_num,
        )

    return message

@commands.command(name='request_substitute_current')
async def user_request_substitute_current(ctx, sub_week: int):
    '''
        <sub_week> one of `1, 2, 3, 4` for the week you want a substitute
    '''
    user = ctx.message.author
    mention = user.mention
    message = await general_request_substitute(mention, user, False, sub_week)
    await ctx.send(message)

help_text = '\n'.join([
])
@commands.command(name='mod_request_substitute_current', help=help_text)
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_request_substitute_current(
        ctx,
        user: discord.Member,
        sub_week: int,
    ):
    '''
        <user> use @someone
        <sub_week> one of `1, 2, 3, 4` for the week you want a substitute
    '''
    mention = ctx.message.author.mention
    message = await general_request_substitute(
        mention, user, False, sub_week, mod=True)
    await ctx.send(message)

@commands.command(name='request_substitute_next')
async def user_request_substitute_next(ctx, sub_week: int):
    '''
        <sub_week> one of `1, 2, 3, 4` for the week you want a substitute
    '''
    user = ctx.message.author
    mention = user.mention
    message = await general_request_substitute(mention, user, True, sub_week)
    await ctx.send(message)

help_text = '\n'.join([
])
@commands.command(name='mod_request_substitute_next', help=help_text)
@commands.has_any_role(*MODERATOR_ROLES)
async def mod_request_substitute_next(
        ctx,
        user: discord.Member,
        sub_week: int,
        ):
    '''
        <user> use @someone
        <sub_week> one of `1, 2, 3, 4` for the week you want a substitute
    '''
    mention = ctx.message.author.mention
    message = await general_request_substitute(
        mention, user, True, sub_week, mod=True)
    await ctx.send(message)

############################### Other commands
@commands.command(name='test')
async def test(ctx):
    '''A test message to make sure GrubberBot is working'''
    await ctx.send('test successful')

@commands.command(name='league_info')
async def league_info(ctx, discord_mention: Optional[discord.Member]=None):
    '''Get league info, optionally @mention someone to get info about them'''
    mention = ctx.message.author.mention
    user = discord_mention

    next_month = fgg.get_month(flg.NEXT_MONTH)
    if discord_mention is None:
        message = '\n'.join([
            f'{mention} ',
            f'* Number of members in the {next_month} season: {len(df)}',
        ])
    else:
        df = LDB.get_league_info(fgg.get_month(1), user.id)
        if len(df) == 0:
            message = f'{mention} user {user.mention} is not signed up for the league {next_month} season'
        else:
            info = {str(c): df[c][0] for c in df.columns}
            message = '\n'.join([
                f'{mention} the user {user.mention} has:',
                pformat(info),
            ])

    await ctx.send(message)

class CustomClient(discord.Client):
    async def on_ready(self):
        guild = discord.utils.get(self.guilds, name=GUILD_NAME)
        print(f'Client {self.user} has connected to {guild.name}')

        save_user_data(guild)
        await save_discord_history(guild)

def main():
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.all()
    client = CustomClient(intents=intents)
    client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
