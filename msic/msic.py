import argparse
from argparse import Namespace
from typing import Callable

from msic.compress import handle_convert
from msic.playlist import handle_playlist


def main(args: list[str]) -> int:
    root_parser = argparse.ArgumentParser(
        prog="msic",
        description="A MuSIC compressor to retain the directory structure and place output files in a separate location",
        epilog="Made by Lavender Shannon because I'm going to start and finish this program in an hour."
    )
    # https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers
    subparsers = root_parser.add_subparsers()

    compress_parser = subparsers.add_parser("compress")
    compress_parser.set_defaults(handle_args=handle_convert)
    # https://docs.python.org/3/library/argparse.html#action
    compress_parser.add_argument("inputs", nargs="+", help="Input directorie(s)")
    compress_parser.add_argument('output', help='Destination directory')
    compress_parser.add_argument('-y', action="store_true", help="Overwrite output files (the default)")
    compress_parser.add_argument('-n', action="store_true", help="Don't overwrite output files")
    compress_parser.add_argument('--skip-existing', action="store_true")
    compress_parser.add_argument('--skip-non-audio', action="store_true")


    playlist_parser = subparsers.add_parser("playlist")
    playlist_parser.set_defaults(handle_args=handle_playlist)
    # https://docs.python.org/3/library/argparse.html#action
    playlist_parser.add_argument("input", help="Input m3u file")
    playlist_parser.add_argument("output", help="Output m3u file")
    playlist_parser.add_argument("--relative-to", help="Make the files relative to this directory. When not specified, paths will not be altered unless --absolute is set.")
    playlist_parser.add_argument("--relative-prefix", help="The prefix added to all relative paths. Not valid when using --absolute.")
    playlist_parser.add_argument("--absolute", action="store_true", help="Make the output absolute. By default makes paths relative to the input playlist's parent directory. Optionally specify --relative-to to change this.")

    args = root_parser.parse_args(args)
    handle_args: Callable[[Namespace], int] = args.handle_args
    return handle_args(args)
