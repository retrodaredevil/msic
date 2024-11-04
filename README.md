# msic
A MuSIC compressor to retain the directory structure and place output files in a separate location.


## Usage

```shell
msic copy --audio=compress ~/Music/MainLibrary/music-my-cd ~/Music/Compressed
```

## Local Setup

```shell
poetry install
poetry run python -m msic
```

## Notes

At one point I thought that using a hardware accelerated ffmpeg (such as [this](https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html)) would speed up conversions.
This would not be the case with audio conversions, so there's little point in it.
If we were seriously interested in using a hardware accelerated ffmpeg, I would wrap this in a docker container and use this as a base: https://github.com/jrottenberg/ffmpeg

## TODO

* Make conversions in parallel
* Try out this library: https://github.com/jonghwanhyeon/python-ffmpeg
  * It's more up to date and has docs: https://python-ffmpeg.readthedocs.io/en/stable/
* (Maybe) rewrite in Rust using https://github.com/zmwangx/rust-ffmpeg
* A subcommand to convert files to a smaller file size only if some criteria is met
  * Example: 
    * Convert all sample rates above 50 to 44.1
    * Convert all MP3 files to OPUS
  * The idea here is that you should be able to specify these complex rules, and then have a test output so you can see what will happen
* Consider using https://beets.io/ as a dependency
