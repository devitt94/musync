from loguru import logger
from musync.models.playlist import Playlist
from musync.providers.base import ProviderClient

PLAYLIST_PREFIX = "[MUSYNC]"


def sync_playlists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
    playlists: list[Playlist],
) -> list[Playlist]:
    results: list[Playlist] = []

    for playlist in playlists:
        logger.info(
            f"Syncing playlist: {playlist.name} from {source_client.provider_name} to {destination_client.provider_name}"
        )

        playlist_to_create_name = (
            f"{PLAYLIST_PREFIX}[{source_client.provider_name}] {playlist.name}"
        )

        if destination_client.user_playlist_exists(playlist_to_create_name):
            logger.info(
                f"{destination_client.provider_name} playlist {playlist_to_create_name} already exists"
            )
            continue

        yt_songs = []
        for song in playlist.songs:
            yt_song = destination_client.find_song(song)
            if yt_song:
                yt_songs.append(yt_song)
                logger.debug(
                    f"Found {song.title} by {song.artist} on {destination_client.provider_name}"
                )
            else:
                logger.warning(
                    f"Could not find {song.title} by {song.artist} on {destination_client.provider_name}"
                )

        yt_playlist = destination_client.create_playlist(
            playlist_to_create_name, yt_songs
        )

        results.append(yt_playlist)

        logger.info(
            f"Created {destination_client.provider_name} playlist: {yt_playlist.name} with {len(yt_playlist.songs)} songs"
        )

    return results


def sync_users_playlists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
) -> list[Playlist]:
    logger.info(
        f"Fetching user playlists from {source_client.provider_name} to sync to {destination_client.provider_name}"
    )

    playlists_to_sync = [
        playlist
        for playlist in source_client.get_user_playlists()
        if not playlist.name.startswith(PLAYLIST_PREFIX)
    ]

    logger.info(f"Found {len(playlists_to_sync)} playlists to sync")

    return sync_playlists(source_client, destination_client, playlists_to_sync)


def sync_followed_playlists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
) -> list[Playlist]:
    playlists_to_sync = [
        playlist
        for playlist in source_client.get_followed_playlists()
        if not playlist.name.startswith(PLAYLIST_PREFIX)
    ]

    return sync_playlists(source_client, destination_client, playlists_to_sync)
