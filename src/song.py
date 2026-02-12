import yt_dlp

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "quiet": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}


class Song:
    def __init__(self, title, duration, video_url):
        self.title = title
        self.duration = duration
        self.video_url = video_url

    def __str__(self):
        return str(self.title)

    @staticmethod
    def extract_song(video_id):
        """Gets Youtube song info by voicechannel id and video id."""
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            url = video_url
            info = ydl.extract_info(url, download=False)

            return Song(
                video_url=video_url,
                title=info["title"],
                duration=info["duration"],
            )

    def get_source_url(self):
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(self.video_url, download=False)
            source_url = info["url"]
            return source_url
