import argparse
import dataclasses
import json
import sys
from argparse import Namespace
from pathlib import Path

import ffmpeg

from msic.util import detect_file_type, get_duration_seconds


@dataclasses.dataclass
class CompressConfig:
    overwrite: bool
    skip_existing: bool
    skip_non_audio_files: bool


def convert_directory(config: CompressConfig, input_directory: Path, output_directory: Path):
    overwrite_arg = {"y": None} if (config.overwrite and not config.skip_existing) else {"n": None}
    for file in input_directory.iterdir():
        if file.is_dir():
            convert_directory(config, file, output_directory / file.name)
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


def convert(config: CompressConfig, input_paths: list[Path], output_path: Path) -> None:
    for input_path in input_paths:
        convert_directory(config, input_path, output_path)


def handle_convert(args: Namespace) -> int:
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

    config = CompressConfig(
        overwrite,
        args.skip_existing,
        args.skip_non_audio,
    )
    convert(config, input_paths, output_path)
