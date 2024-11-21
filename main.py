import dotenv

from musync.providers import SpotifyClient, YoutubeClient


dotenv.load_dotenv()

PLAYLIST_PREFIX = "[MUSYNC]"


def main():
    spotify_client: SpotifyClient = SpotifyClient.from_env()

    youtube_client: YoutubeClient = YoutubeClient.from_env()

    playlists_to_sync = [
        playlist
        for playlist in spotify_client.get_user_playlists()
        if not playlist.name.startswith(PLAYLIST_PREFIX)
    ]

    for playlist in playlists_to_sync:
        print(f"Syncing playlist: {playlist.name} from Spotify to YouTube")

        playlist_to_create_name = f"{PLAYLIST_PREFIX} {playlist.name}"

        if youtube_client.user_playlist_exists(playlist_to_create_name):
            print(f"YouTube playlist {playlist_to_create_name} already exists")
            continue

        yt_songs = []
        for song in playlist.songs:
            print(f"Searching for {song.title} by {song.artist} on YouTube")

            yt_song = youtube_client.find_song(song)
            if yt_song:
                yt_songs.append(yt_song)
            else:
                print(f"Could not find {song.title} by {song.artist} on YouTube")

        yt_playlist = youtube_client.create_playlist(playlist_to_create_name, yt_songs)

        print(f"Created YouTube playlist: {yt_playlist.name}")


if __name__ == "__main__":
    main()
