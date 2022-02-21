import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--credential_directory", help="Directory where login credentials are data",)

    args = parser.parse_args()
    return args
