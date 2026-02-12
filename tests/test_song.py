import pytest
from src.song import Song


def test_song_happy_path(mocker):
    youtubedl_mock = mocker.patch("yt_dlp.YoutubeDL")
    youtubedl_mock.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }

    song = Song.extract_song("123")

    assert song is not None
    assert song.duration == 9000
    assert song.title == "It's MyGO!!!!!"

    source_url = song.get_source_url()

    assert source_url == "https://example.com/mygo.mp3"
