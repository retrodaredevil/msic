# msic
A MuSIC compressor to retain the directory structure and place output files in a separate location.


## Usage

```shell
msic copy --audio=compress ~/Music/MainLibrary/music-my-cd ~/Music/Compressed
```

## Local Setup

```shell
# Running the "env use" command is only required if you do not have a Python version >= 3.11
poetry env use /home/linuxbrew/.linuxbrew/bin/python3
# or
poetry env use python3.13

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

## Random Links

* https://python-plexapi.readthedocs.io/en/latest/
* https://musicbrainz.org/doc/MusicBrainz_API
* https://support.plex.tv/articles/201018248-merge-or-split-items/
* https://pypi.org/project/musicbrainzngs/

## Plex API Stuff

We use [plexapi](https://python-plexapi.readthedocs.io/en/latest/) to query plex.
Once you have a [MusicSection](https://python-plexapi.readthedocs.io/en/latest/modules/library.html#plexapi.library.MusicSection),
you can begin querying artists, albums, and tracks.
The MusicBrainz Identifiers attached to these map to [artists](https://musicbrainz.org/doc/Artist), [releases](https://musicbrainz.org/doc/Release), and [tracks](https://musicbrainz.org/doc/Track) respectively.
Remember that different versions of the same album may have the same recording of a song, but different tracks.
So often times it is most useful to convert the track [Musicbrainz Identifier](https://musicbrainz.org/doc/MusicBrainz_Identifier) to the recording mbid.

## MusicBrainz track querying
To query a track, you can query something like https://musicbrainz.org/ws/2/release?track=dc2784b9-59ca-46ca-a19e-b998c98f278c&fmt=json, which is not possible via musicbrainzngs.
Note that the returned tracks may not contain the MBID given in the query if a merge has occurred.
Remember that the returned tracks are all the tracks on a given release.
That can make it difficult to accurately determine which track is actually the one you queried for.


## Related Stuff
* https://beets.io/
* https://github.com/arsaboo/beets-plexsync
