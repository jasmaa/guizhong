import os
import subprocess
import hashlib
from pathlib import Path
import asyncio
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

discord_token = os.environ.get("DISCORD_TOKEN")
discord_command_prefix = os.environ.get("DISCORD_COMMAND_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=discord_command_prefix, intents=intents)
session_cache = {}
music_cache_path = Path("/tmp/guizhong/music_cache")

AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE = (
    "You need to be in a voice channel to use this command."
)
NO_SESSION_FOUND_MESSAGE = f"You need to have music queued to use this command. Try playing something with `{discord_command_prefix}play <YOUTUBE VIDEO URL>`."
MAX_SONG_INFOS_TO_DISPLAY = 5


class Session:
    def __init__(self, vc):
        self.vc = vc
        self.queue = []
        self.play_music_task = None


class Song:
    def __init__(self, song_hash, song_filepath, title, duration):
        self.song_hash = song_hash
        self.song_filepath = song_filepath
        self.title = title
        self.duration = duration

    def __str__(self):
        return str(self.song_filepath)


def parse_youtube_video_url(url):
    """Parses Youtube video id from valid URL. Throws runtime error if URL is invalid."""
    url_parse = urlparse(url)

    if url_parse.hostname != "youtube.com" and url_parse.hostname != "www.youtube.com":
        raise RuntimeError("invalid hostname")
    if url_parse.path != "/watch":
        raise RuntimeError("invalid path")

    query_parse = parse_qs(url_parse.query)

    if query_parse.get("v")[0] is None:
        raise RuntimeError("invalid video id")

    video_id = query_parse.get("v")[0]

    return video_id


def get_or_download_youtube_mp3(voicechannel_id, video_id):
    """Gets Youtube MP3 by voicechannel id and video id. If song is not cached, downloads from web."""
    song_hash = hashlib.md5(video_id.encode("utf8")).hexdigest()
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    parent_path = music_cache_path / str(voicechannel_id) / song_hash
    song_filepath = parent_path / "song.mp3"
    metadata_filepath = parent_path / "metadata.json"

    if not os.path.exists(parent_path):
        subprocess.run(
            [
                "yt-dlp",
                "-x",
                "--audio-format",
                "mp3",
                "-o",
                song_filepath,
                video_url,
            ]
        )

        metadata = {}
        with open(metadata_filepath, "w") as f:
            output = subprocess.Popen(
                [
                    "yt-dlp",
                    "-J",
                    video_url,
                ],
                stdout=subprocess.PIPE,
            ).communicate()[0]
            metadata = json.loads(output.decode("utf8"))
            json.dump(metadata, f)

        return Song(
            song_hash=song_hash,
            song_filepath=song_filepath,
            title=metadata["title"],
            duration=metadata["duration"],
        )

    else:
        metadata = {"title": "Unknown", "duration": -1}
        with open(metadata_filepath, "r") as f:
            metadata = json.load(f)

        return Song(
            song_hash=song_hash,
            song_filepath=song_filepath,
            title=metadata["title"],
            duration=metadata["duration"],
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
        song_filepath = queue[0].song_filepath

        def post_play(e):
            queue.pop()
            fut = session.play_music_task = asyncio.run_coroutine_threadsafe(
                play_queue(voicechannel_id),
                bot.loop,
            )
            try:
                fut.result
            except:
                pass

        vc.stop()
        vc.play(discord.FFmpegPCMAudio(song_filepath), after=post_play)
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
async def play(ctx, arg):
    """Downloads and plays song in argument. If bot is not in call, bot will join call."""
    voicechannel = await get_author_voicechannel(ctx)
    if voicechannel is None:
        await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
        return

    # Connect or get voice client
    if voicechannel.id not in session_cache:
        vc = await voicechannel.connect()
        session_cache[voicechannel.id] = Session(vc=vc)

    session = session_cache[voicechannel.id]
    vc = session.vc
    queue = session.queue

    # Download or get music
    video_id = parse_youtube_video_url(arg)
    song = get_or_download_youtube_mp3(voicechannel.id, video_id)
    queue.append(song)
    print(f"Added {song} to queue")

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
async def skip(ctx):
    """Skips current song in queue."""
    voicechannel = await get_author_voicechannel(ctx)
    if voicechannel is None:
        await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
        return

    if voicechannel.id not in session_cache:
        await ctx.send(NO_SESSION_FOUND_MESSAGE)
        return

    session = session_cache[voicechannel.id]
    vc = session.vc

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


bot.run(discord_token)
