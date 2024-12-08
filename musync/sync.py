from musync.logger import logger
from musync.models.artist import Artist
from musync.models.playlist import Playlist
from musync.providers.base import ProviderClient

PLAYLIST_SUFFIX = "[MUSYNC]"


def is_musync_playlist(playlist: Playlist) -> bool:
    return playlist.name.startswith(PLAYLIST_SUFFIX)


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

        playlist_to_create_name = f"{playlist.name} {PLAYLIST_SUFFIX}"

        existing_playlist = destination_client.get_playlist_by_name(
            playlist_to_create_name
        )
        if existing_playlist:
            logger.info(
                f"{destination_client.provider_name} playlist {playlist_to_create_name} already exists"
            )

            songs_already_added = {
                (song.title, song.artist) for song in existing_playlist.songs
            }
        else:
            songs_already_added = set()

        songs_to_add = []
        for song in playlist.songs:
            if (song.title, song.artist) in songs_already_added:
                continue

            destination_song = destination_client.find_song(song)
            if not destination_song:
                logger.warning(
                    f"Could not find {song.title} by {song.artist} on {destination_client.provider_name}"
                )
                continue

            if (destination_song.title, destination_song.artist) in songs_already_added:
                continue

            logger.debug(f"Adding song: {destination_song}")
            songs_to_add.append(destination_song)

        if existing_playlist:
            if songs_to_add:
                logger.info(
                    f"Adding {len(songs_to_add)} songs to {destination_client.provider_name} playlist: {playlist_to_create_name}"
                )
                destination_playlist = destination_client.add_songs_to_playlist(
                    existing_playlist, songs_to_add
                )
                results.append(destination_playlist)
                logger.debug(f"Playlist updated: {destination_playlist}")
            else:
                logger.info(
                    f"No new songs to add to {destination_client.provider_name} playlist: {existing_playlist}"
                )
                destination_playlist = existing_playlist
        else:
            logger.info(
                f"Creating {destination_client.provider_name} playlist: {playlist_to_create_name} with {len(songs_to_add)} songs"
            )

            destination_playlist = destination_client.create_playlist(
                playlist_to_create_name, songs_to_add
            )

        results.append(destination_playlist)

    return results


def sync_users_playlists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
) -> list[Playlist]:
    logger.info(
        f"Fetching user's playlists from {source_client.provider_name} to sync to {destination_client.provider_name}"
    )

    playlists_to_sync = [
        playlist
        for playlist in source_client.get_user_playlists()
        if not playlist.name.endswith(PLAYLIST_SUFFIX)
    ]

    logger.info(f"Found {len(playlists_to_sync)} playlists to sync")

    return sync_playlists(source_client, destination_client, playlists_to_sync)


def sync_followed_playlists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
) -> list[Playlist]:
    logger.info(
        f"Fetching user's followed playlists from {source_client.provider_name} to sync to {destination_client.provider_name}"
    )

    playlists_to_sync = [
        playlist
        for playlist in source_client.get_followed_playlists()
        if not playlist.name.startswith(PLAYLIST_SUFFIX)
    ]

    logger.info(f"Found {len(playlists_to_sync)} playlists to sync")

    return sync_playlists(source_client, destination_client, playlists_to_sync)


def sync_followed_artists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
) -> list[Artist]:
    source_artists = source_client.get_followed_artists()
    synced_artists = []

    for artist in source_artists:
        destination_artist = destination_client.find_artist(artist)
        if not destination_artist:
            logger.warning(
                f"Could not find match for artist '{artist.name}' on {destination_client.provider_name}"
            )
            continue

        logger.info(
            f"Syncing artist '{artist.name}' from {source_client.provider_name} to {destination_client.provider_name}"
        )
        destination_client.follow_artist(destination_artist)
        synced_artists.append(destination_artist)

    return synced_artists


def delete_synced_playlists(client: ProviderClient) -> None:
    logger.info(f"Fetching playlists from {client.provider_name} ")
    playlists = client.get_user_playlists()
    playlists = [playlist for playlist in playlists if is_musync_playlist(playlist)]
    logger.info(f"Found {len(playlists)} playlists to delete")

    for playlist in playlists:
        logger.info(f"Deleting playlist '{playlist.name}' from {client.provider_name}")
        client.delete_playlist(playlist)

    logger.info(f"Deleted {len(playlists)} playlists")
