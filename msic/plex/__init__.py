from argparse import Namespace, _SubParsersAction
from typing import Optional

import musicbrainzngs
from plexapi.audio import Album, Artist, Track
from plexapi.library import MusicSection
from plexapi.media import Guid
from plexapi.server import PlexServer


def get_musicbrainz_identifier(guids: list[Guid]) -> Optional[str]:
    for guid in guids:
        if isinstance(guid.id, str) and guid.id.startswith("mbid://"):
            return guid.id[7:]
    return None


def print_recently_added_tracks(music: MusicSection):
    """
    Prints the recently added tracks.
    Unlike recently added albums, recently added tracks show tracks that were added even if it is a duplicate of an existing track in the library.
    :param music: The music section
    """
    artist_cache: dict[str, Artist] = dict()
    album_cache: dict[str, Album] = dict()

    print("Recently added tracks:")
    for track in music.recentlyAddedTracks(350):
        track: Track = track
        # Note since we only care about the artist.title and album.title we could use parentTitle and grandparentTitle,
        #   but we choose not to because this is a good example of how to do something like this (remember this code is mostly for prototyping purposes)
        try:
            artist = artist_cache[track.grandparentGuid]
        except KeyError:
            artist = track.artist()
            artist_cache[track.grandparentGuid] = artist
        try:
            album = album_cache[track.parentGuid]
        except KeyError:
            album = track.album()
            album_cache[track.parentGuid] = album

        mb_id = get_musicbrainz_identifier(track.guids) or ""
        print(f"{artist.title: <24} - {album.title: <24} - {track.title: <40} - {mb_id} - {track.guid} - {track.key}")

    print()


def print_recently_added_albums(music: MusicSection):
    print("Recently added albums:")
    for album in music.recentlyAddedAlbums(50):
        album: Album = album
        mb_id = get_musicbrainz_identifier(album.guids) or ""
        print(f"{album.parentTitle:<24} - {album.title:<24} - {mb_id}")
    print()


def find_duplicate_tracks_for_artist(artist: Artist):
    print(f"Finding duplicate tracks for {artist.title}")
    guid_set = set()
    mb_id_set = set()
    duplicate_guid_set = set()
    duplicate_mb_id_set = set()
    tracks = artist.tracks()
    for track in tracks:
        track: Track = track
        guid = track.guid
        mb_id = get_musicbrainz_identifier(track.guids)

        if guid in guid_set:
            duplicate_guid_set.add(guid)
        else:
            guid_set.add(guid)

        if mb_id is not None:
            if mb_id in mb_id_set:
                duplicate_mb_id_set.add(mb_id)
            else:
                mb_id_set.add(mb_id)


    for track in tracks:
        track: Track = track
        mb_id = get_musicbrainz_identifier(track.guids)
        is_duplicate = track.guid in duplicate_guid_set or mb_id in duplicate_mb_id_set
        duplicate_text = " - (DUPLICATE)" if is_duplicate else ""
        print(f"{track.grandparentTitle:<24} - {track.parentTitle:<24} - {track.title:<40} - {track.guid} - {mb_id}{duplicate_text}")

    print()


def setup_plex(subparsers: _SubParsersAction):
    parser = subparsers.add_parser("plex")
    parser.set_defaults(handle_args=handle_plex)

def handle_plex(args: Namespace):
    # https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
    # TODO supply token and url through arguments
    token = ""
    plex = PlexServer("", token)
    music: MusicSection = plex.library.section("Music")

    print_recently_added_tracks(music)
    print_recently_added_albums(music)

    find_duplicate_tracks_for_artist(music.get("Chappell Roan"))

    artist: Artist = music.get("Daft Punk")
    album: Album = artist.album("Discovery")

    print(album)
    print(album.fields)
    print(album.userRating)
    print(album.guid)
    print(album.guids)
    print(album.labels)
    print(album.key)
    print(album.ratingKey)
    print(album.parentGuid)
    print(album.parentTitle)


    musicbrainz_guid: Guid = album.guids[0]
    print(musicbrainz_guid.key)
    print(musicbrainz_guid.id)
    print(type(musicbrainz_guid.id))

    print(artist)
    print(artist.guid)

    # album.merge(rating key here)



