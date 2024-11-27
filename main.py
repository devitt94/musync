import dotenv
from loguru import logger

from musync.models.playlist import Playlist
from musync.providers import SpotifyClient, YoutubeClient
from musync.providers.base import ProviderClient


dotenv.load_dotenv()

PLAYLIST_PREFIX = "[MUSYNC]"


def sync_playlists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
    playlists: list[Playlist],
) -> None:
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
            else:
                logger.warning(
                    f"Could not find {song.title} by {song.artist} on {destination_client.provider_name}"
                )

        yt_playlist = destination_client.create_playlist(
            playlist_to_create_name, yt_songs
        )

        logger.info(
            f"Created {destination_client.provider_name} playlist: {yt_playlist.name}"
        )


def sync_users_playlists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
) -> None:
    playlists_to_sync = [
        playlist
        for playlist in source_client.get_user_playlists()
        if not playlist.name.startswith(PLAYLIST_PREFIX)
    ]

    sync_playlists(source_client, destination_client, playlists_to_sync)


def sync_followed_playlists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
) -> None:
    playlists_to_sync = [
        playlist
        for playlist in source_client.get_followed_playlists()
        if not playlist.name.startswith(PLAYLIST_PREFIX)
    ]

    sync_playlists(source_client, destination_client, playlists_to_sync)


def main() -> None:
    read_only = True
    spotify_client: SpotifyClient = SpotifyClient.from_env(read_only=read_only)

    youtube_client: YoutubeClient = YoutubeClient.from_env(read_only=read_only)

    sync_users_playlists(spotify_client, youtube_client)
    sync_followed_playlists(spotify_client, youtube_client)

    sync_users_playlists(youtube_client, spotify_client)
    sync_followed_playlists(youtube_client, spotify_client)


if __name__ == "__main__":
    main()
