from pathlib import Path

import ffmpeg


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
