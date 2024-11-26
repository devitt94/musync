import dotenv
from loguru import logger

from musync.providers import SpotifyClient, YoutubeClient
from musync.providers.base import ProviderClient


dotenv.load_dotenv()

PLAYLIST_PREFIX = "[MUSYNC]"


def sync_users_playlists(
    source_client: ProviderClient,
    destination_client: ProviderClient,
) -> None:
    playlists_to_sync = [
        playlist
        for playlist in source_client.get_user_playlists()
        if not playlist.name.startswith(PLAYLIST_PREFIX)
    ]

    for playlist in playlists_to_sync:
        logger.info(
            f"Syncing playlist: {playlist.name} from {source_client.provider_name} to {destination_client.provider_name}"
        )

        playlist_to_create_name = f"{PLAYLIST_PREFIX} {playlist.name}"

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


def main() -> None:
    spotify_client: SpotifyClient = SpotifyClient.from_env()

    youtube_client: YoutubeClient = YoutubeClient.from_env()

    sync_users_playlists(spotify_client, youtube_client)


if __name__ == "__main__":
    main()
