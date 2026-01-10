import os
import subprocess
import hashlib
from pathlib import Path
import asyncio
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


class Session:
    def __init__(self, vc):
        self.vc = vc
        self.queue = []
        self.play_music_task = None


class Song:
    def __init__(self, name, filepath):
        self.filepath = filepath


def get_or_download_youtube_mp3(voicechannel_id, url):
    h = hashlib.md5(url.encode("utf8")).hexdigest()
    filename = f"{h}.mp3"

    parent_path = music_cache_path / str(voicechannel_id)
    filepath = parent_path / filename

    if not os.path.exists(filepath):
        subprocess.run(
            [
                "yt-dlp",
                "-x",
                "--audio-format",
                "mp3",
                "-P",
                parent_path,
                "-o",
                filename,
                url,
            ]
        )

    return filepath


@bot.event
async def on_ready():
    print("Bot is ready!")


async def get_voicechannel(ctx):
    voice_state = ctx.author.voice

    if voice_state is None:
        # Exiting if the user is not in a voice channel
        return await ctx.send("You need to be in a voice channel to use this command")

    voicechannel = voice_state.channel
    return voicechannel


async def play_queue(voicechannel_id):
    session = session_cache[voicechannel_id]
    vc = session.vc
    queue = session.queue

    # Play next song in the queue
    if len(queue) > 0:
        filepath = queue[0].filepath

        def post_play(e):
            queue.pop()
            session.play_loop_task = asyncio.create_task(play_queue(voicechannel_id))

        vc.stop()
        vc.play(discord.FFmpegPCMAudio(filepath), after=post_play)
    else:
        vc.stop()
        session.play_loop_task = None


@bot.command()
async def info(ctx):
    voicechannel = await get_voicechannel(ctx)
    if voicechannel.id in session_cache:
        session = session_cache[voicechannel.id]
        queue = session.queue

        if len(queue) > 0:
            current_song = queue[0]
            await ctx.send(
                "```\n"
                + f"Now playing: {current_song.filepath}\n\n"
                + "Queue:\n"
                + "\n".join(
                    [f"{i+1}: {song.filepath}" for i, song in enumerate(queue)][:5]
                )
                + "\n```"
            )
        else:
            await ctx.send("```\nNot playing\n```")
    else:
        await ctx.send("```\nNot playing...\n```")


@bot.command()
async def play(ctx, arg):
    voicechannel = await get_voicechannel(ctx)

    # Connect or get voice client
    if voicechannel.id not in session_cache:
        vc = await voicechannel.connect()
        session_cache[voicechannel.id] = Session(vc=vc)

    session = session_cache[voicechannel.id]
    vc = session.vc
    queue = session.queue

    # Download or get music
    print("Downloading...")
    url = arg
    filepath = get_or_download_youtube_mp3(voicechannel.id, url)
    print(f"Downloaded to {filepath}")

    # TODO: get song name
    song = Song(name=filepath, filepath=filepath)

    queue.append(song)
    print(f"Added {song} to queue")

    if not vc.is_playing():
        session.play_loop_task = asyncio.create_task(play_queue(voicechannel.id))


@bot.command()
async def pause(ctx):
    voicechannel = await get_voicechannel(ctx)

    if voicechannel.id not in session_cache:
        ctx.send("Not in the voice channel")
        return

    session = session_cache[voicechannel.id]
    vc = session.vc

    vc.pause()


@bot.command()
async def resume(ctx):
    voicechannel = await get_voicechannel(ctx)

    if voicechannel.id not in session_cache:
        ctx.send("Not in the voice channel")
        return

    session = session_cache[voicechannel.id]
    vc = session.vc

    vc.resume()


@bot.command()
async def stop(ctx):
    voicechannel = await get_voicechannel(ctx)
    if voicechannel.id in session_cache:
        session = session_cache[voicechannel.id]
        vc = session.vc
        play_loop_task = session.play_loop_task

        vc.stop()
        await vc.disconnect()
        if play_loop_task is not None:
            play_loop_task.cancel()
        del session_cache[voicechannel.id]


bot.run(discord_token)
