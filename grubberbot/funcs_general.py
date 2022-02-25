import datetime

import gspread
import numpy as np
import pandas as pd
from html2image import Html2Image

GOOGLE_TOKEN = "credentials/google_credentials.json"
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/\
                    1dJzqT0R5bfv_22je6W-rL0S0qvnb8cR5QIQkMV5Q32g/"
REFRESH_MESSAGE = "Hi! Looks like "


class cellLocationConstants:
    """
    Constants that help gspread find the cell where the scores
    and the team names are defined here.
    """

    # Name of the sheet within the Google Sheet where the scores are located
    SHEET_NAME = "Scoresheet"
    TEAM_1_SCORE_ACELL = (
        "Q4"  # {Letter}{Number} coordinates where the value is located.
    )
    TEAM_2_SCORE_ACELL = "Q5"

    TEAM_1_NAME_ACELL = "P4"
    TEAM_2_NAME_ACELL = "P5"


def get_month(month_delta=0, to_str=True):
    date = datetime.datetime.now()
    date = date.replace(day=1)

    for _ in range(abs(month_delta)):
        if month_delta > 0:
            delta = datetime.timedelta(31)
        elif month_delta < 0:
            delta = -datetime.timedelta(2)
        date = date + delta
        date = date.replace(day=1)

    if to_str:
        date = date.strftime("%Y%B")
    return date


def gen_substitute_thread_name(seed_id):
    name = f"s{seed_id} Substitute Request"
    return name


def gen_pairing_thread_name(game_id, white_name, black_name):
    thread_name = f"{white_name} vs {black_name} g{game_id}"
    return thread_name


def arr_to_sheet(arr, sheet=0):
    gc = gspread.service_account(filename=GOOGLE_TOKEN)
    sh = gc.open_by_url(GOOGLE_SHEET_URL)
    sheet = sh.get_worksheet(sheet)

    if len(arr):
        row_length = len(arr[0])
    else:
        row_length = 0

    sheet_array = arr
    sheet_array = sheet_array + [["" for _ in range(row_length)] for _ in range(100)]
    sheet_array = [row + ["" for _ in range(100)] for row in sheet_array]
    sheet.update(sheet_array)


def gen_df_to_sheet(df, title=None):
    for col in df.columns:
        df[col] = [str(e) for e in np.array(df[col])]

    if title is None:
        sheet_array = []
    else:
        sheet_array = [["" for _ in range(len(list(df.columns)))] for _ in title]
        for r, row in enumerate(title):
            for e, elem in enumerate(row):
                sheet_array[r][e] = elem
    sheet_array = sheet_array + [df.columns.values.tolist()]
    sheet_array = sheet_array + df.values.tolist()
    return sheet_array


def df_to_sheet(df, sheet=0, title=None):
    sheet_array = gen_df_to_sheet(df, title=title)
    arr_to_sheet(sheet_array, sheet=sheet)


def dfs_to_sheet(dfs, sheet=0):
    arrs = [gen_df_to_sheet(df, title=title) for title, df in dfs.items()]
    arrs = sorted(arrs, key=lambda x: len(x), reverse=True)
    if len(dfs):
        longest_arr = max(len(a) for a in arrs)
    else:
        longest_arr = 0
    for arr in arrs:
        while len(arr) < longest_arr:
            arr.append(["" for _ in range(len(arr[0]))])

        for row in arr:
            row.append("")

    sheet_array = []
    for i in range(longest_arr):
        row = []
        for j in range(len(arrs)):
            row.extend(arrs[j][i])
        sheet_array.append(row)

    arr_to_sheet(sheet_array, sheet=sheet)


def get_scores():
    """
    Uses gspread to get the scores and the names of the teams.

    Returns a list with 4 items:
    * l[0] = Name of the 1st team
    * l[1] = Name of the 2nd team
    * l[2] = Points scored by the 1st team
    * l[3] = Points scored by the 2nd team
    """
    gc = gspread.service_account(filename=GOOGLE_TOKEN)

    sheet = gc.open_by_url(cellLocationConstants.GOOGLE_SHEET_URL)
    scoresheet = sheet.worksheet(cellLocationConstants.SCORESHEET_NAME)

    team1_score = scoresheet.acell(cellLocationConstants.TEAM_1_SCORE_ACELL).value
    team2_score = scoresheet.acell(cellLocationConstants.TEAM_2_SCORE_ACELL).value

    team1_name = scoresheet.acell(cellLocationConstants.TEAM_1_NAME_ACELL).value
    team2_name = scoresheet.acell(cellLocationConstants.TEAM_2_NAME_ACELL).value

    return [team1_name, team2_name, team1_score, team2_score]


def get_html_str(team_1_name, team_2_name, team_1_score, team_2_score):
    """
    Replaces the Jynga inspired variables, {{ var }} in the
    HTML file with their values. Returns the edited string.
    """
    with open(".\\templates\\index.html") as f:

        edited_html_str = (
            f.read()
            .replace("{{ team_1_name }}", team_1_name)
            .replace("{{ team_2_name }}", team_2_name)
            .replace("{{ team_1_score }}", team_1_score)
            .replace("{{ team_2_score }}", team_2_score)
        )
        return edited_html_str


async def save_image(team_1_name, team_2_name, team_1_score, team_2_score):
    """
    Takes in the names of both the teams and the score. Html2Image opens
    a headless browser window (this is why Chrome needs to be added to the
    Dockerfile) and screenshots the html file, saving it in a file called
    score.png located in the img  directory inside the assets folder. (If the
    file already exists, it overwrites it). This file is then uploaded to the
    channel where the !score command was used.
    """

    html = get_html_str(team_1_name, team_2_name, team_1_score, team_2_score)

    hti = Html2Image(size=(800, 352))
    hti.load_file(".\\templates\\assets\\bg.jpg")
    hti.screenshot(
        html_str=html, css_file=".\\templates\\styles\\main.css", save_as="score.png"
    )
