import os
import asyncio
import discord
from discord.ext import commands
from mutagen.mp3 import MP3
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
session_cache = {}
BASE_PATH = "music"
DEFAULT_VOICE_CHANNEL_NAME = "General"


async def play_loop(voicechannel):
    while True:
        if voicechannel.id in session_cache:
            vc = session_cache[voicechannel.id]["vc"]
            filename = session_cache[voicechannel.id]["queue"].pop(0)
            session_cache[voicechannel.id]["queue"].append(filename)
            session_cache[voicechannel.id]["current_song"] = filename

            p = os.path.join(BASE_PATH, filename)
            f = MP3(p)

            vc.stop()
            vc.play(discord.FFmpegPCMAudio(p), after=lambda e: print(
                f'Player error: {e}') if e else None)

            async def cancellable_sleep():
                try:
                    await asyncio.sleep(f.info.length)
                except asyncio.CancelledError:
                    print("sleep cancelled")

            session_cache[voicechannel.id]["sleep_task"] = asyncio.create_task(
                cancellable_sleep())
            await session_cache[voicechannel.id]["sleep_task"]
        else:
            break


@bot.event
async def on_ready():
    print("Bot is ready!")


def get_voicechannel(ctx):
    voicechannel = discord.utils.get(
        ctx.guild.channels, name=DEFAULT_VOICE_CHANNEL_NAME)
    if voicechannel == None:
        for channel in ctx.guild.channels:
            if type(channel) is discord.VoiceChannel:
                voicechannel = channel
                break
    return voicechannel


@bot.command()
async def info(ctx):
    voicechannel = get_voicechannel(ctx)
    if voicechannel.id in session_cache:
        q = session_cache[voicechannel.id]["queue"]
        current_song = session_cache[voicechannel.id]["current_song"]
        await ctx.send("```\n" + f"Now playing: {current_song}\n\n" + "Queue:\n" + "\n".join([f'{i+1}: {f}' for i, f in enumerate(q)]) + "\n```")
    else:
        await ctx.send("```\nNot playing...\n```")


@bot.command()
async def play(ctx):
    voicechannel = get_voicechannel(ctx)
    if voicechannel.id not in session_cache:
        vc = await voicechannel.connect()
        session_cache[voicechannel.id] = {
            "vc": vc,
            "queue": [f for f in os.listdir("music") if f.endswith("mp3")],
            "current_song": None,
            "sleep_task": None,
            "play_loop_task": asyncio.create_task(play_loop(voicechannel)),
        }
    if session_cache[voicechannel.id]["sleep_task"]:
        session_cache[voicechannel.id]["sleep_task"].cancel()


@bot.command()
async def stop(ctx):
    voicechannel = get_voicechannel(ctx)
    if voicechannel.id in session_cache:
        vc = session_cache[voicechannel.id]["vc"]
        vc.stop()
        await vc.disconnect()
        if session_cache[voicechannel.id]["sleep_task"]:
            session_cache[voicechannel.id]["sleep_task"].cancel()
        session_cache[voicechannel.id]["play_loop_task"].cancel()
        del session_cache[voicechannel.id]

bot.run(os.environ.get("DISCORD_TOKEN"))
