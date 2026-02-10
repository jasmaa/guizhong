import pytest
from src.bot import parse_youtube_video_url


def test_parse_youtube_url():
    assert parse_youtube_video_url("https://youtube.com/watch?v=123") == "123"
    assert parse_youtube_video_url("http://www.youtube.com/watch?v=34") == "34"
    assert (
        parse_youtube_video_url(
            "https://www.youtube.com/watch?v=x2iKC0C32-g&list=RDx2iKC0C32-g&start_radio=1"
        )
        == "x2iKC0C32-g"
    )
