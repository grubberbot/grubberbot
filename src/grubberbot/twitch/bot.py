import os
import string

import pyttsx3
import yaml
from twitchobserver import Observer

# TODO get list of mods instead of hard-coding mod nicknames

# Path variables
CREDENTIALS_PATH = "credentials/credentials.yml"
TTS_USERS_PATH = "data/tts_users.yml"
SCREEN_TEXT_PATH = "data/tts.txt"

CHANNEL = "pawngrubber"
IGNORED_USER_TYPE = "ignore"
REGULAR_USER_TYPE = "user"


def load_yaml(filename):
    with open(filename, "r") as f:
        data = yaml.safe_load(f)
    return data


class TTS:
    def __init__(self):
        self.engine = self.build_engine()

        self.user_types = {
            "mods": {
                "voice": -2,
                "volume": 1.0,
            },
            "super_user": {
                "voice": -2,
                "volume": 0.75,
            },
            "user": {
                "voice": -1,
                "volume": 0.33,
            },
        }

    def get_user_type(self, nickname):
        data = load_yaml(TTS_USERS_PATH)
        user_type = data[nickname] if nickname in data else None
        return user_type

    def build_engine(self):
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        return engine

    def speak(self, message, nickname):
        user_type = self.get_user_type(nickname)

        if user_type == IGNORED_USER_TYPE:
            return
        elif user_type not in self.user_types:
            user_type = REGULAR_USER_TYPE

        # Set voice and volume
        voice = self.user_types[user_type]["voice"]
        volume = self.user_types[user_type]["volume"]
        self.engine.setProperty("voice", self.engine.getProperty("voices")[voice].id)
        self.engine.setProperty("volume", volume)

        # Actually speak now
        prefix = "!tts "
        if message.lower().startswith(prefix):
            text = message[len(prefix) :]
            text = "".join([t for t in text if t in string.printable])
            with open(SCREEN_TEXT_PATH, "w") as f:
                print(f"{nickname}: {text}", file=f)
            self.engine.say(text)
            self.engine.runAndWait()


def main():
    tts = TTS()

    credentials = load_yaml(CREDENTIALS_PATH)
    with Observer("username", credentials["OAUTH"]) as observer:
        observer.join_channel(CHANNEL)
        print("Joined channel", CHANNEL)

        # Twitch loop
        while True:
            try:
                for event in observer.get_events():
                    if event.type == "TWITCHCHATMESSAGE":
                        tts.speak(event.message, event.nickname)
            except Exception as e:
                print(e)
                observer.leave_channel(CHANNEL)
                break


if __name__ == "__main__":
    main()
