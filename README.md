# Musync

A simple CLI tool for syncing user data across streaming services.

## Motivation

Considering moving from Spotify to YouTube Music (or vice versa), but afraid of losing all of your playlists, liked songs and followed artists? Musync makes it easy to transfer your user data from one streaming service to another.

## Usage

### Installation

Using pip:

```bash
pip install musync
```

Using pipx:

```bash
pipx install musync
```

You can verify the installation worked by running:

```bash
musync --help
```

### Authentication setup

For musync to work, it needs to authenticate with the streaming services used.

#### Spotify

Musync uses [spotipy](https://spotipy.readthedocs.io/en/2.24.0/) to interact with the Spotify API. See the [spotipy documentation](https://spotipy.readthedocs.io/en/2.24.0/#authorization-code-flow) for more information on how to authenticate with Spotify.

#### YouTube Music

Musync uses [ytmusicapi](https://ytmusicapi.readthedocs.io/en/latest/) to interact with the YouTube Music API. See the [ytmusicapi documentation](https://ytmusicapi.readthedocs.io/en/latest/setup.html) for more information on how to authenticate with YouTube Music.

Once you have authenticated with both services, copy the `.env.example` file to a new file called `.env` and populate it with your credentials.

```bash
cp .env.example .env
```

To test if the authentication is working, run the following command:

```bash
musync test-auth
```

You should see a message indicating that the authentication was successful, and your relevant username should be displayed.

```
2024-12-08 17:48:09.780 | INFO     | Successfully authenticated with Spotify as rorydevitt
2024-12-08 17:48:09.864 | INFO     | Successfully authenticated with YouTube as @rdevitt941
2024-12-08 17:48:09.864 | INFO     | musync is ready to use!
```

### Syncing your data

To sync your data, you can use the `unisync` command. This command will sync all of your data from one service to another.

```bash
musync unisync --source spotify --destination youtube
```

If you're hesitant at first and would like to see what actions musync will perform - you can specify the `--dry-run` flag to run the command in read-only mode, where no changes will be made to the destination service.

```bash
musync unisync --source spotify --destination youtube --dry-run
```

By default, `unisync` will sync all of your data. You can exlcude certain data types by using the relevant flags.

```bash
# Exclude user playlists
musync unisync --source spotify --destination youtube --no-user-playlists

# Exclude followed playlists
musync unisync --source spotify --destination youtube --no-followed-playlists

# Exclude followed artists
musync unisync --source spotify --destination youtube --no-followed-artists
```

These flags can be combined to exclude multiple data types.

#### Clearing playlists

If you want to clear all of the playlists that musync has created on the destination service, you can use the `clear-playlists` command.

```bash
# Clear all playlists created by musync on YouTube Music
musync clear-playlists --provider youtube
```

#### Other things to note

- Musync will not duplicate data on the destination service. If a playlist with the same name already exists, musync updates the existing playlist with any new tracks that have been added to the source playlist. This allows syncing to be run multiple times without creating duplicate data.
- Musync will not delete any data on the destination service. If a playlist is deleted on the source service, it will not be deleted on the destination service. Similarly, if a track is removed from a playlist on the source service, it will not be removed from the destination service.
- All playlists are created on the destination service with the suffix `[MUSYNC]` in their name, to make it clear that they were created by musync. This is also how musync identifies playlists that it has created, when deciding whether to update or create a new playlist and also when running the `clear-playlists` command.


## Contributing

Coming soon...
