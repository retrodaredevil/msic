# msic
A MuSIC compressor to retain the directory structure and place output files in a separate location.


## Usage

```shell
msic --input ~/Music/MainLibrary ~/Music/Compressed
```

* `--input` A directory. This argument can be included multiple times.

## Local Setup

```shell
poetry install
poetry run python -m msic
```

## TODO

* Try out this library: https://github.com/jonghwanhyeon/python-ffmpeg
  * It's more up to date and has docs: https://python-ffmpeg.readthedocs.io/en/stable/
* (Maybe) rewrite in Rust using https://github.com/zmwangx/rust-ffmpeg
* Docker image with hardware accelerated ffmpeg: https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html
