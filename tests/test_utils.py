import pytest
from src.utils import parse_youtube_video_url
from src.errors import InvalidSongURLError


def test_parse_youtube_url_happy_path():
    assert parse_youtube_video_url("https://youtube.com/watch?v=123") == "123"
    assert parse_youtube_video_url("http://www.youtube.com/watch?v=34") == "34"
    assert parse_youtube_video_url("http://m.youtube.com/watch?v=67") == "67"
    assert (
        parse_youtube_video_url(
            "https://www.youtube.com/watch?v=x2iKC0C32-g&list=RDx2iKC0C32-g&start_radio=1"
        )
        == "x2iKC0C32-g"
    )
    assert (
        parse_youtube_video_url("https://www.youtube.com/watch?v=first&v=second")
        == "first"
    )


def test_parse_youtube_url_invalid_urls():
    with pytest.raises(InvalidSongURLError):
        assert parse_youtube_video_url("https://example.com")
    with pytest.raises(InvalidSongURLError):
        assert parse_youtube_video_url("http://www.youtube.com/watch")
    with pytest.raises(InvalidSongURLError):
        assert parse_youtube_video_url("http://www.youtube.com/watch?random=23")
