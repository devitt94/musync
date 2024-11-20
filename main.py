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

    yt_songs = []
    for song in playlist.songs:

        yt_song = youtube_client.find_song(song)
        if yt_song:
            yt_songs.append(yt_song)
        else:
            print(f"    - Could not find {song.title} by {song.artist} on YouTube")

    yt_playlist = youtube_client.create_playlist(f"[MUSYNC] {playlist.name}", yt_songs)

    print(f"Created YouTube playlist: {yt_playlist.name}")

    
if __name__ == "__main__":
    main()
