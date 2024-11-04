import dataclasses
import json
import shutil
import sys
from argparse import Namespace
from enum import Enum, auto
from pathlib import Path

import ffmpeg

from msic.util import detect_file_type, get_duration_seconds


class CopyAudioType(Enum):
    NONE = auto()
    RAW = auto()
    COMPRESS = auto()


@dataclasses.dataclass
class CopyConfig:
    overwrite: bool
    copy_audio: CopyAudioType
    skip_existing: bool
    skip_non_audio_files: bool
    generate_metadata_json: bool


def convert_directory(config: CopyConfig, input_directory: Path, output_directory: Path):
    overwrite_arg = {"y": None} if (config.overwrite and not config.skip_existing) else {"n": None}
    for file in input_directory.iterdir():
        if file.is_dir():
            convert_directory(config, file, output_directory / file.name)
        elif file.is_file():
            file_type = detect_file_type(file)
            if "audio" in file_type:
                skip_audio_copy = config.copy_audio == CopyAudioType.NONE
                compress = config.copy_audio == CopyAudioType.COMPRESS
                generate_metadata_json = config.generate_metadata_json
            else:
                skip_audio_copy = config.skip_non_audio_files
                compress = False
                generate_metadata_json = False

            if not skip_audio_copy:
                # region Copy Audio
                if compress:  # if compress is true, then we can assume it is an audio file
                    output_file = output_directory / (file.name + ".mp3")
                    if output_file.exists():
                        if config.skip_existing:
                            existing_file_metadata = ffmpeg.probe(str(output_file))
                            print(f"{file} exists! Skipping. Metadata: {json.dumps(existing_file_metadata, indent=4)}")
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
                    output_file = output_directory / file.name
                    if output_file.exists() and config.skip_existing:
                        print(f"{file} exists! Skipping")
                        continue
                    print(f"{file} into {output_file}")
                    output_directory.mkdir(parents=True, exist_ok=True)
                    shutil.copy(file, output_file)
                # endregion Copy Audio
            # region Generate Metadata
            if generate_metadata_json:
                metadata_file = output_directory / (file.name + ".metadata.json")
                metadata = ffmpeg.probe(str(file))
                output_metadata = {
                    "ffprobe_format": metadata["format"]
                }
                with metadata_file.open("w") as opened_file:
                    opened_file.write(json.dumps(output_metadata, indent=2))
                # TODO copy album art
                # ffmpeg -i input.mp3 -an -vcodec copy cover.jpg
            # endregion Generate Metadata

        else:
            print(f"Unknown file: {file}", file=sys.stderr)


def convert(config: CopyConfig, input_paths: list[Path], output_path: Path) -> None:
    for input_path in input_paths:
        convert_directory(config, input_path, output_path)


def handle_copy(args: Namespace) -> int:
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

    if args.audio == "none":
        copy_audio = CopyAudioType.NONE
    elif args.audio == "raw":
        copy_audio = CopyAudioType.RAW
    elif args.audio == "compress":
        copy_audio = CopyAudioType.COMPRESS
    else:
        raise NotImplementedError(f"Unknown copy option: {args.audio}")

    config = CopyConfig(
        overwrite,
        copy_audio,
        args.skip_existing,
        args.skip_non_audio,
        args.metadata,
    )
    convert(config, input_paths, output_path)
