import json
import urllib.request


def get_player_id(chesscom_name):

    # Get url
    url = f"https://api.chess.com/pub/player/{chesscom_name}"
    try:
        with urllib.request.urlopen(url) as response:
            info = response.read()
    except urllib.error.HTTPError:
        return None

    info = json.loads(info)
    if "player_id" in info:
        return info["player_id"]
    else:
        return None


def main():
    foo = get_player_id("pawngrubberr")
    print(foo)

    foo = get_player_id("pawngrubber")
    print(foo)


if __name__ == "__main__":
    main()
