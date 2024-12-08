from enum import Enum
import itertools
import dotenv
from musync.logger import logger
import typer

from musync.providers import SpotifyClient, YoutubeClient
from musync.providers.base import ProviderClient
from musync.sync import (
    delete_synced_playlists,
    sync_followed_artists,
    sync_followed_playlists,
    sync_users_playlists,
)

from typing import Type

dotenv.load_dotenv()

app = typer.Typer()


class Provider(str, Enum):
    spotify = "spotify"
    youtube = "youtube"


def get_provider_client(provider: Provider, read_only: bool) -> ProviderClient:
    clients: dict[Provider, Type[ProviderClient]] = {
        Provider.spotify: SpotifyClient,
        Provider.youtube: YoutubeClient,
    }

    try:
        return clients[provider].from_env(read_only=read_only)
    except KeyError:
        raise ValueError(f"Invalid provider: {provider}")


@app.command()
def unisync(
    source: Provider = typer.Option(..., help="The source provider"),
    destination: Provider = typer.Option(..., help="The destination provider"),
    user_playlists: bool = typer.Option(True, help="Whether to sync user playlists"),
    followed_playlists: bool = typer.Option(
        True, help="Whether to sync followed playlists"
    ),
    followed_artists: bool = typer.Option(
        True, help="Whether to sync followed artists"
    ),
    dry_run: bool = typer.Option(False, help="Whether to run in read-only mode"),
) -> None:
    source_client = get_provider_client(source, read_only=dry_run)
    destination_client = get_provider_client(destination, read_only=dry_run)

    if user_playlists:
        sync_users_playlists(source_client, destination_client)

    if followed_playlists:
        sync_followed_playlists(source_client, destination_client)

    if followed_artists:
        sync_followed_artists(source_client, destination_client)


@app.command()
def multisync(
    providers: list[Provider] = typer.Argument(..., help="The providers to sync"),
    user_playlists: bool = typer.Option(True, help="Whether to sync user playlists"),
    followed_playlists: bool = typer.Option(
        True, help="Whether to sync followed playlists"
    ),
    followed_artists: bool = typer.Option(
        True, help="Whether to sync followed artists"
    ),
    dry_run: bool = typer.Option(False, help="Whether to run in read-only mode"),
) -> None:
    logger.debug(
        f"Running multisync for providers: {providers} ({user_playlists=}, {followed_playlists=}, {dry_run=})"
    )
    clients = [
        get_provider_client(provider, read_only=dry_run) for provider in providers
    ]

    for source_client, destination_client in itertools.permutations(clients, 2):
        logger.info(
            f"Syncing {source_client.provider_name} to {destination_client.provider_name}"
        )
        if user_playlists:
            sync_users_playlists(source_client, destination_client)

        if followed_playlists:
            sync_followed_playlists(source_client, destination_client)

        if followed_artists:
            sync_followed_artists(source_client, destination_client)


@app.command()
def clear_playlists(
    provider: Provider = typer.Argument(
        ..., help="The provider to clear playlists from"
    ),
    dry_run: bool = typer.Option(False, help="Whether to run in read-only mode"),
) -> None:
    client = get_provider_client(provider, read_only=dry_run)
    delete_synced_playlists(client)


@app.command()
def test_auth():
    all_successful = True
    for provider in Provider:
        try:
            client: ProviderClient = get_provider_client(provider, read_only=True)
            logger.info(
                f"Successfully authenticated with {client.provider_name} as {client.username}"
            )
        except Exception:
            logger.exception(f"Failed to authenticate with {provider}")
            all_successful = False

    if not all_successful:
        raise typer.Exit(code=1)

    logger.info("musync is ready to use!")


if __name__ == "__main__":
    app()
