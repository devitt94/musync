import os
from pprint import pprint
import dotenv


from musync.models.song import Song
from musync.providers import SpotifyClient, YoutubeClient


dotenv.load_dotenv()


def main():

    spotify_client: SpotifyClient = SpotifyClient.from_env()

    youtube_client: YoutubeClient = YoutubeClient.from_env()

    playlists = spotify_client.get_user_playlists()

    playlist = playlists[0]

    print(f"Playlist: {playlist.name}")

    for song in playlist.songs:
        print(f"  - {song.title} by {song.artist}")

        yt_song = youtube_client.find_song(song)
        if yt_song is None:
            print("    - Not found on YouTube")

if __name__ == "__main__":
    main()
