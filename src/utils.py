import re
from urllib.parse import urlparse
from urllib.parse import parse_qs
from .errors import InvalidSongURLError


def parse_youtube_video_url(url):
    """Parses Youtube video id from valid URL. Throws InvalidSongURLError if URL is invalid."""
    url_parse = urlparse(url)

    valid_hostnames = ["youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"]

    if url_parse.hostname not in valid_hostnames:
        raise InvalidSongURLError("invalid hostname")

    if url_parse.hostname == "youtu.be":
        # Handle shortened URL
        m = re.search("^/(\\w+)$", url_parse.path)
        if m is None or m.group(1) is None:
            raise InvalidSongURLError("invalid path")

        video_id = m.group(1)
        return video_id
    else:
        # Handle normal URL
        if url_parse.path != "/watch":
            raise InvalidSongURLError("invalid path")

        query_parse = parse_qs(url_parse.query)

        if query_parse.get("v") is None or query_parse.get("v")[0] is None:
            raise InvalidSongURLError("invalid video id")

        video_id = query_parse.get("v")[0]
        return video_id
