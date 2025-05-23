import argparse
from argparse import Namespace
from typing import Callable

from msic.audio import setup_audio
from msic.plex import setup_plex


def main(args: list[str]) -> int:
    root_parser = argparse.ArgumentParser(
        prog="msic",
        description="A MuSIC compressor to retain the directory structure and place output files in a separate location",
        epilog="Made by Lavender Shannon because I'm going to start and finish this program in an hour."
    )
    # https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers
    subparsers = root_parser.add_subparsers()

    setup_audio(subparsers)
    setup_plex(subparsers)

    args = root_parser.parse_args(args)
    handle_args: Callable[[Namespace], int] = args.handle_args
    return handle_args(args)
