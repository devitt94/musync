from unittest.mock import MagicMock
import pytest

from musync.providers.youtube import YoutubeClient
from musync.models.song import Song


@pytest.fixture
def yt_client():
    return YoutubeClient.from_env()


def test_find_song(yt_client: YoutubeClient):
    song = Song(
        id="test_id",
        title="Wonderwall",
        artist="Oasis",
    )

    yt_client._client.search = MagicMock(
        return_value=[
            {
                "category": "Songs",
                "resultType": "song",
                "title": "Wonderwall",
                "album": {
                    "name": "(What's The Story) Morning Glory?",
                    "id": "MPREb_PITqkpE6ExP",
                },
                "inLibrary": False,
                "feedbackTokens": {
                    "add": "AB9zfpIWFHHT0ynIuCZQy7J29A-9bOt8wFRjelymQ73MWWBgVSe-C5N6fesBrKeKylnrJ15gka7TwM_Z9iPWkiqccb8Php-Mfg",
                    "remove": "AB9zfpJpvggJR51HwCG8XjvcybaxLj0ntOA6h3Rmg5P7Weio3hOoQNgV8EOhfSfBedsoOFIf49hAQrpko-TWgQ1NaEq01_DmQg",
                },
                "videoId": "hpSrLjc5SMs",
                "videoType": "MUSIC_VIDEO_TYPE_ATV",
                "duration": "4:19",
                "year": None,
                "artists": [{"name": "Oasis", "id": "UCmMUZbaYdNH0bEd1PAlAqsA"}],
                "duration_seconds": 259,
                "isExplicit": False,
                "thumbnails": [
                    {
                        "url": "https://lh3.googleusercontent.com/SP0cN9Mypy_WeKEajm03ERYOU_53KkHZpu4EQpSJUzcQ1H_3HhS1FmjR34KTstf-0DX83JLCCj9ouc-k1g=w60-h60-l90-rj",
                        "width": 60,
                        "height": 60,
                    },
                    {
                        "url": "https://lh3.googleusercontent.com/SP0cN9Mypy_WeKEajm03ERYOU_53KkHZpu4EQpSJUzcQ1H_3HhS1FmjR34KTstf-0DX83JLCCj9ouc-k1g=w120-h120-l90-rj",
                        "width": 120,
                        "height": 120,
                    },
                ],
            },
            {
                "category": "Songs",
                "resultType": "song",
                "title": "Wonderwall",
                "album": {
                    "name": "(What's The Story) Morning Glory? (Deluxe Remastered Edition)",
                    "id": "MPREb_SmEdOAdN7en",
                },
                "inLibrary": False,
                "feedbackTokens": {
                    "add": "AB9zfpIPLY93ZwV6SYFJC2u59w8y5Z4-t0MIC6HY8wPS1lqHH3pJjjNP73z007ZQNmcaKB8Lb8m5mJvTomqXZUX8_Ghr4whiFg",
                    "remove": "AB9zfpKH6OJ5e_6mvzZFoTVPe7Aiz-jXyzlfqMm3DxXUp5J8jPEAf-v3ayuhSvPafzOKPw7BZ916u1Tq5oMFgjdB_l-EhvgNzA",
                },
                "videoId": "FVdjZYfDuLE",
                "videoType": "MUSIC_VIDEO_TYPE_ATV",
                "duration": "4:19",
                "year": None,
                "artists": [{"name": "Oasis", "id": "UCmMUZbaYdNH0bEd1PAlAqsA"}],
                "duration_seconds": 259,
                "isExplicit": None,
                "thumbnails": [
                    {
                        "url": "https://lh3.googleusercontent.com/cJPWEK7Y4QJzQBRmWrhHAlxk9yKdZuh-zcEGoYlBY7CbpHq_9gTwON-3aMXjXxQvFtEuKl1on6EOWAE=w60-h60-l90-rj",
                        "width": 60,
                        "height": 60,
                    },
                    {
                        "url": "https://lh3.googleusercontent.com/cJPWEK7Y4QJzQBRmWrhHAlxk9yKdZuh-zcEGoYlBY7CbpHq_9gTwON-3aMXjXxQvFtEuKl1on6EOWAE=w120-h120-l90-rj",
                        "width": 120,
                        "height": 120,
                    },
                ],
            },
        ]
    )

    yt_song = yt_client.find_song(song)

    assert yt_song is not None
    assert yt_song.id == "hpSrLjc5SMs"
    assert yt_song.title == song.title
    assert yt_song.artist == song.artist


def test_find_song_no_results(yt_client: YoutubeClient):
    song = Song(
        id="test_id",
        title="Wonderwall",
        artist="Oasis",
    )

    yt_client._client.search = MagicMock(return_value=[])

    yt_song = yt_client.find_song(song)

    assert yt_song is None


def test_find_song_no_album(yt_client: YoutubeClient):
    song = Song(
        id="test_id",
        title="Wonderwall",
        artist="Oasis",
    )

    yt_client._client.search = MagicMock(
        return_value=[
            {
                "category": "Songs",
                "resultType": "song",
                "title": "Wonderwall",
                "album": None,
                "inLibrary": False,
                "feedbackTokens": {
                    "add": "AB9zfpIWFHHT0ynIuCZQy7J29A-9bOt8wFRjelymQ73MWWBgVSe-C5N6fesBrKeKylnrJ15gka7TwM_Z9iPWkiqccb8Php-Mfg",
                    "remove": "AB9zfpJpvggJR51HwCG8XjvcybaxLj0ntOA6h3Rmg5P7Weio3hOoQNgV8EOhfSfBedsoOFIf49hAQrpko-TWgQ1NaEq01_DmQg",
                },
                "videoId": "hpSrLjc5SMs",
                "videoType": "MUSIC_VIDEO_TYPE_ATV",
                "duration": "4:19",
                "year": None,
                "artists": [{"name": "Oasis", "id": "UCmMUZbaYdNH0bEd1PAlAqsA"}],
                "duration_seconds": 259,
                "isExplicit": False,
                "thumbnails": [
                    {
                        "url": "https://lh3.googleusercontent.com/SP0cN9Mypy_WeKEajm03ERYOU_53KkHZpu4EQpSJUzcQ1H_3HhS1FmjR34KTstf-0DX83JLCCj9ouc-k1g=w60-h60-l90-rj",
                        "width": 60,
                        "height": 60,
                    },
                    {
                        "url": "https://lh3.googleusercontent.com/SP0cN9Mypy_WeKEajm03ERYOU_53KkHZpu4EQpSJUzcQ1H_3HhS1FmjR34KTstf-0DX83JLCCj9ouc-k1g=w120-h120-l90-rj",
                        "width": 120,
                        "height": 120,
                    },
                ],
            }
        ]
    )

    yt_song = yt_client.find_song(song)

    assert yt_song is not None
    assert yt_song.album is None
