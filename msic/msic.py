import argparse
import subprocess
import sys
from pathlib import Path

import ffmpeg


def convert(input_directory: Path, output_directory: Path):
    for file in input_directory.iterdir():
        if file.is_dir():
            convert(file, output_directory / file.name)
        elif file.is_file():
            output_file = output_directory / file.name
            print(f"{file} into {output_file}")
            output_directory.mkdir(parents=True, exist_ok=True)
            # https://kkroening.github.io/ffmpeg-python/
            (
                ffmpeg
                .input(str(file), vn=None)
                .output(str(output_file) + ".mp3", acodec="mp3", map='0:a:0', map_metadata=0, **{'b:a': "64k"})
                .run()
            )
            # result = subprocess.run([
            #     "ffmpeg",
            #     "-vn",
            #     "-i", str(file),
            #     "-c:a", "mp3",
            #     "-b:a", "64k",
            #     "-map_metadata", "0",
            #     str(output_file) + ".mp3"
            # ])
        else:
            print(f"Unknown file: {file}", file=sys.stderr)


def main(args: list[str]) -> int:
    print("Hello")
    parser = argparse.ArgumentParser(
        prog="msic",
        description="A MuSIC compressor to retain the directory structure and place output files in a separate location",
        epilog="Made by Lavender Shannon because I'm going to start and finish this program in an hour."
    )
    # https://docs.python.org/3/library/argparse.html#action
    parser.add_argument('-i', '--input', action="append")
    parser.add_argument('output')  # positional argument
    args = parser.parse_args(args)
    inputs: list[str] = args.input
    output = args.output
    if not inputs:
        print("You must provide inputs", file=sys.stderr)
        return 1
    input_paths = [Path(i) for i in inputs]
    output_path = Path(output)

    for input_path in input_paths:
        convert(input_path, output_path)

    return 0
