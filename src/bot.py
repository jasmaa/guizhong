import os
from pathlib import Path
import asyncio
from urllib.parse import urlparse
from urllib.parse import parse_qs
import discord
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp

load_dotenv()

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

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

discord_token = os.environ.get("DISCORD_TOKEN")
discord_command_prefix = os.environ.get("DISCORD_COMMAND_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=discord_command_prefix, intents=intents)
session_cache = {}

AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE = "You need to be in a voice channel to use this command. Try joining a voice and trying again."
SAMPLE_COMMAND_MESSAGE_PART = (
    f"Try playing something with `{discord_command_prefix}play <YOUTUBE VIDEO URL>`."
)
NO_SESSION_FOUND_MESSAGE = (
    f"You need to have music queued to use this command. {SAMPLE_COMMAND_MESSAGE_PART}"
)
INVALID_ARGS_FOR_PLAY_MESSAGE = (
    f"A single URL must be provided for this command. {SAMPLE_COMMAND_MESSAGE_PART}"
)
INVALID_YOUTUBE_URL_FOR_PLAY_MESSAGE = (
    "Invalid URL provided. Please provide a valid Youtube video URL."
)
GENERAL_ERROR_FOR_PLAY_MESSAGE = (
    "Unable to queue song due to an unknown error. Please contact the bot owner."
)
MAX_SONG_INFOS_TO_DISPLAY = 5


class Session:
    def __init__(self, vc):
        self.vc = vc
        self.queue = []
        self.play_music_task = None


class Song:
    def __init__(self, title, duration, video_url):
        self.title = title
        self.duration = duration
        self.video_url = video_url

    def __str__(self):
        return str(self.title)


class InvalidSongURLError(RuntimeError):
    """Exception for invalid song URL on parse."""


def parse_youtube_video_url(url):
    """Parses Youtube video id from valid URL. Throws InvalidSongURLError if URL is invalid."""
    url_parse = urlparse(url)

    valid_hostnames = ["youtube.com", "www.youtube.com", "m.youtube.com"]

    if url_parse.hostname not in valid_hostnames:
        raise InvalidSongURLError("invalid hostname")
    if url_parse.path != "/watch":
        raise InvalidSongURLError("invalid path")

    query_parse = parse_qs(url_parse.query)

    if query_parse.get("v")[0] is None:
        raise InvalidSongURLError("invalid video id")

    video_id = query_parse.get("v")[0]

    return video_id


async def extract_song(video_id):
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


async def get_author_voicechannel(ctx):
    """Gets voicechannel caller is in."""
    voice_state = ctx.author.voice

    if voice_state is None:
        return None

    voicechannel = voice_state.channel
    return voicechannel


async def play_queue(voicechannel_id):
    """Plays songs going down the session queue."""
    session = session_cache[voicechannel_id]
    vc = session.vc
    queue = session.queue

    if len(queue) > 0:
        # Play next song in the queue
        video_url = queue[0].video_url

        def post_play(e):
            queue.pop(0)
            fut = session.play_music_task = asyncio.run_coroutine_threadsafe(
                play_queue(voicechannel_id),
                bot.loop,
            )
            try:
                fut.result
            except:
                pass

        vc.stop()

        # Taken from: https://stackoverflow.com/questions/75680967/using-yt-dlp-in-discord-py-to-play-a-song
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            url2 = info["url"]
            source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
            vc.play(source, after=post_play)
    else:
        # No songs left in queue, clean up session and leave voice channel
        del session_cache[voicechannel_id]
        await vc.disconnect()


@bot.event
async def on_ready():
    print("Bot is ready!")


@bot.command()
async def info(ctx):
    """Provides info on current queue bot is playing."""
    voicechannel = await get_author_voicechannel(ctx)
    if voicechannel is None:
        await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
        return

    if voicechannel.id not in session_cache:
        await ctx.send(NO_SESSION_FOUND_MESSAGE)
        return

    session = session_cache[voicechannel.id]
    queue = session.queue

    if len(queue) <= 0:
        await ctx.send("```\nNot playing\n```")
        return

    current_song = queue[0]
    await ctx.send(
        "```\n"
        + f"Now playing: {current_song.title} [{current_song.duration}s]\n\n"
        + "Queue:\n"
        + "\n".join(
            [f"{i+1}: {song.title}" for i, song in enumerate(queue)][
                :MAX_SONG_INFOS_TO_DISPLAY
            ]
        )
        + "\n```"
    )


@bot.command()
async def play(ctx, *args):
    """Downloads and plays song in argument. If bot is not in call, bot will join call."""
    if not args:
        await ctx.send(INVALID_ARGS_FOR_PLAY_MESSAGE)
        return
    if len(args) != 1:
        await ctx.send(INVALID_ARGS_FOR_PLAY_MESSAGE)
        return

    voicechannel = await get_author_voicechannel(ctx)
    if voicechannel is None:
        await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
        return

    # Connect or get voice client
    if voicechannel.id not in session_cache:
        vc = await voicechannel.connect()
        session_cache[voicechannel.id] = Session(vc=vc)

    session = session_cache[voicechannel.id]
    queue = session.queue

    # Extract and queue song
    url = args[0]
    video_id = None
    try:
        video_id = parse_youtube_video_url(url)
        song = await extract_song(video_id)
        queue.append(song)
        print(f"Added {song} to queue")
        await ctx.send(f"Successfully queued {song.title}!")
    except InvalidSongURLError:
        await ctx.send(INVALID_YOUTUBE_URL_FOR_PLAY_MESSAGE)
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(GENERAL_ERROR_FOR_PLAY_MESSAGE)
    finally:
        # Start a new music task if nothing is playing
        if session.play_music_task is None:
            session.play_music_task = asyncio.create_task(play_queue(voicechannel.id))


@bot.command()
async def pause(ctx):
    """Pauses current song."""
    voicechannel = await get_author_voicechannel(ctx)
    if voicechannel is None:
        await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
        return

    if voicechannel.id not in session_cache:
        await ctx.send(NO_SESSION_FOUND_MESSAGE)
        return

    session = session_cache[voicechannel.id]
    vc = session.vc

    vc.pause()


@bot.command()
async def resume(ctx):
    """Resumes current song."""
    voicechannel = await get_author_voicechannel(ctx)
    if voicechannel is None:
        await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
        return

    if voicechannel.id not in session_cache:
        await ctx.send(NO_SESSION_FOUND_MESSAGE)
        return

    session = session_cache[voicechannel.id]
    vc = session.vc

    vc.resume()


@bot.command()
async def skip(ctx, *args):
    """Skips current song in queue."""

    n_skip = 1
    if args is not None and len(args) == 1:
        try:
            n_skip = int(args[0])
        except ValueError as e:
            await ctx.send(
                f"Invalid number of songs to skip. Try skipping songs with `{discord_command_prefix}skip <NUMBER OF SONGS>`."
            )
            return

    # Cannot skip fewer than 1 song
    if n_skip <= 0:
        await ctx.send(
            f"Invalid number of songs to skip. Try skipping songs with `{discord_command_prefix}skip <NUMBER OF SONGS>`."
        )
        return

    voicechannel = await get_author_voicechannel(ctx)
    if voicechannel is None:
        await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
        return

    if voicechannel.id not in session_cache:
        await ctx.send(NO_SESSION_FOUND_MESSAGE)
        return

    session = session_cache[voicechannel.id]
    vc = session.vc
    queue = session.queue

    # Remove n-1 next songs
    del queue[1:n_skip]

    # Stopping current stream will trigger after callback and queue up next song
    vc.stop()


@bot.command()
async def stop(ctx):
    """Clears songs and stops playing from queue."""
    voicechannel = await get_author_voicechannel(ctx)
    if voicechannel is None:
        await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
        return

    if voicechannel.id not in session_cache:
        await ctx.send(NO_SESSION_FOUND_MESSAGE)
        return

    session = session_cache[voicechannel.id]

    # Clear queue and stop voice client to force session clean-up
    session.queue = []
    session.vc.stop()


if __name__ == "__main__":
    bot.run(discord_token)
