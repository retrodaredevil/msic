import argparse
import dataclasses
import json
import sys
from pathlib import Path

import ffmpeg


@dataclasses.dataclass
class Config:
    overwrite: bool
    skip_existing: bool
    skip_non_audio_files: bool


def detect_file_type(file: Path) -> str:
    try:
        # noinspection PyUnresolvedReferences
        import magic

        # NOTE: magic.from_file(path) works when path is a pathlib.Path on Linux, but does not work on Windows.
        #   We must convert to string first!
        return magic.from_file(str(file))
    except FileNotFoundError:
        raise
    except OSError:
        raise
    except ImportError:
        raise
    except AttributeError as e:
        # An AttributeError occurs on Windows when python-magic-bin is not installed
        #   `AttributeError: module 'magic' has no attribute 'from_file'
        # https://github.com/ahupp/python-magic?tab=readme-ov-file#installation
        raise ValueError("libmagic is not installed. This test will fail. Make sure that python-magic-bin is installed if you are on Windows.") from e


def get_duration_seconds(file: Path) -> float:
    data = ffmpeg.probe(file)
    try:
        stream = next(stream for stream in data["streams"] if stream["codec_type"] == "audio")
    except StopIteration:
        raise ValueError(f"No audio streams present in {file}!")
    return float(stream["duration"])


def convert(config: Config, input_directory: Path, output_directory: Path):
    overwrite_arg = {"y": None} if (config.overwrite and not config.skip_existing) else {"n": None}
    for file in input_directory.iterdir():
        if file.is_dir():
            convert(config, file, output_directory / file.name)
        elif file.is_file():
            if config.skip_non_audio_files and file.exists():
                file_type = detect_file_type(file)
                if "audio" not in file_type:
                    print(f"{file} is of the type {repr(file_type)}! Skipping")
                    continue

            output_file = output_directory / (file.name + ".mp3")
            if output_file.exists():
                if config.skip_existing:
                    metadata = ffmpeg.probe(str(output_file))
                    print(f"{file} exists! Skipping. Metadata: {json.dumps(metadata, indent=4)}")
                    continue
                else:
                    source_duration = get_duration_seconds(file)
                    try:
                        destination_duration = get_duration_seconds(output_file)
                    except ValueError:
                        pass
                    else:
                        if abs(source_duration - destination_duration) <= 0.1:
                            print(f"{file} has similar duration for destination. Skipping")
                            continue

            print(f"{file} into {output_file}")
            output_directory.mkdir(parents=True, exist_ok=True)
            # https://kkroening.github.io/ffmpeg-python/
            (
                ffmpeg
                .input(str(file), vn=None)
                .output(str(output_file), acodec="mp3", map_metadata=0, **{'b:a': "64k"}, **overwrite_arg)
                .run()
            )
        else:
            print(f"Unknown file: {file}", file=sys.stderr)


def main(args: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="msic",
        description="A MuSIC compressor to retain the directory structure and place output files in a separate location",
        epilog="Made by Lavender Shannon because I'm going to start and finish this program in an hour."
    )
    # https://docs.python.org/3/library/argparse.html#action
    parser.add_argument("inputs", nargs="+", help="Input directorie(s)")
    parser.add_argument('output', help='Destination directory')
    parser.add_argument('-y', action="store_true", help="Overwrite output files (the default)")
    parser.add_argument('-n', action="store_true", help="Don't overwrite output files")
    parser.add_argument('--skip-existing', action="store_true")
    parser.add_argument('--skip-non-audio', action="store_true")
    args = parser.parse_args(args)
    inputs: list[str] = args.inputs
    output = args.output
    if not inputs:
        print("You must provide inputs", file=sys.stderr)
        return 1
    overwrite = not args.n  # we can ignore the `-y` option, as it is the default
    if not overwrite and args.y:
        print("You cannot use both -y and -n at the same time!", file=sys.stderr)
        return 1
    input_paths = [Path(i) for i in inputs]
    output_path = Path(output)

    config = Config(
        overwrite,
        args.skip_existing,
        args.skip_non_audio,
    )

    for input_path in input_paths:
        convert(config, input_path, output_path)

    return 0
