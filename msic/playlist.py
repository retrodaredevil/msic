import dataclasses
import sys
from argparse import Namespace
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

import m3u8


@dataclasses.dataclass
class PlaylistConfig:
    relative_to: Optional[Path]
    relative_prefix: Optional[Path]
    make_absolute: bool


def alter_playlist(config: PlaylistConfig, playlist: m3u8.M3U8):
    for segment in playlist.segments:
        segment: m3u8.Segment = segment
        if not urlsplit(segment.uri).scheme:  # ignore URLs
            path = Path(segment.uri)
            if config.make_absolute:
                relative_to = config.relative_to if config.relative_to is not None else Path(".")
                if not path.is_absolute():
                    path = (relative_to / path).absolute()
            elif config.relative_to is not None:
                if path.is_absolute():
                    path = path.relative_to(config.relative_to)
                if config.relative_prefix is not None:
                    path = config.relative_prefix / path

            segment.uri = str(path)



def handle_playlist(args: Namespace) -> int:
    input_string = args.input
    output_string = args.output

    config = PlaylistConfig(
        Path(args.relative_to) if args.relative_to is not None else None,
        Path(args.relative_prefix) if args.relative_to is not None else None,
        args.absolute,
    )
    if config.relative_prefix is not None and config.make_absolute:
        print("Cannot use both --relative-prefix and --absolute at the same time", file=sys.stderr)
        return 1

    playlist: m3u8.M3U8 = m3u8.load(input_string)
    alter_playlist(config, playlist)
    playlist.dump(output_string)

    return 0
