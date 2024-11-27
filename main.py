from enum import Enum
import dotenv
from loguru import logger
import typer

from musync.models.playlist import Playlist
from musync.providers import SpotifyClient, YoutubeClient
from musync.providers.base import ProviderClient

from typing import TypeVar

dotenv.load_dotenv()

app = typer.Typer()

PLAYLIST_PREFIX = "[MUSYNC]"


ProviderClientType = TypeVar("ProviderClientType", bound=ProviderClient)


class Provider(str, Enum):
    spotify = "spotify"
    youtube = "youtube"


def get_provider_client(provider: Provider, read_only: bool) -> ProviderClient:
    clients: dict[Provider, ProviderClientType] = {
        Provider.spotify: SpotifyClient,
        Provider.youtube: YoutubeClient,
    }

    try:
        return clients[provider].from_env(read_only=read_only)
    except KeyError:
        raise ValueError(f"Invalid provider: {provider}")


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
    playlists_to_sync = [
        playlist
        for playlist in source_client.get_user_playlists()
        if not playlist.name.startswith(PLAYLIST_PREFIX)
    ]

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


@app.command()
def unisync(
    source: Provider = typer.Argument(..., help="The source provider"),
    destination: Provider = typer.Argument(..., help="The destination provider"),
    read_only: bool = typer.Option(False, help="Whether to run in read-only mode"),
) -> None:
    source_client = get_provider_client(source, read_only)
    destination_client = get_provider_client(destination, read_only)

    sync_users_playlists(source_client, destination_client)
    sync_followed_playlists(source_client, destination_client)


if __name__ == "__main__":
    app()
