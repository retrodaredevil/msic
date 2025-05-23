from argparse import _SubParsersAction, Namespace

from msic.audio.copy import setup_copy
from msic.audio.playlist import setup_playlist


def setup_audio(subparsers: _SubParsersAction):
    parser = subparsers.add_parser("audio")
    parser.set_defaults(handle_args=handle_audio)
    audio_subparsers = parser.add_subparsers()
    setup_copy(audio_subparsers)
    setup_playlist(audio_subparsers)


def handle_audio(args: Namespace) -> int:
    print("Please specify a subcommand")
    return 1
