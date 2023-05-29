import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
session_cache = {}
BASE_PATH = "music"
DEFAULT_VOICE_CHANNEL_NAME = "General"


@bot.event
async def on_ready():
    print("Bot is ready!")


def get_voicechannel(ctx):
    voicechannel = discord.utils.get(
        ctx.guild.channels, name=DEFAULT_VOICE_CHANNEL_NAME)
    return voicechannel


async def summon(voicechannel):
    if voicechannel not in session_cache:
        vc = await voicechannel.connect()
        session_cache[voicechannel] = {
            "vc": vc,
            "queue": [f for f in os.listdir("music") if f.endswith("mp3")],
            "current_song": None,
        }


@bot.command()
async def info(ctx):
    voicechannel = get_voicechannel(ctx)
    await summon(voicechannel)
    q = session_cache[voicechannel]["queue"]
    current_song = session_cache[voicechannel]["current_song"]
    await ctx.send("```\n" + f"Currently playing: {current_song}\n\n" + "Queue:\n" + "\n".join([f'{i+1}: {f}' for i, f in enumerate(q)]) + "\n```")


@bot.command()
async def play(ctx):
    voicechannel = get_voicechannel(ctx)
    await summon(voicechannel)
    vc = session_cache[voicechannel]["vc"]
    f = session_cache[voicechannel]["queue"].pop(0)
    session_cache[voicechannel]["queue"].append(f)
    session_cache[voicechannel]["current_song"] = f
    p = os.path.join(BASE_PATH, f)
    await ctx.send(f"Playing {f}...")
    vc.stop()
    vc.play(discord.FFmpegPCMAudio(p),
            after=lambda e: print(f'Player error: {e}') if e else None)


@bot.command()
async def stop(ctx):
    voicechannel = get_voicechannel(ctx)
    if voicechannel in session_cache:
        vc = session_cache[voicechannel]["vc"]
        vc.stop()
        await vc.disconnect()
        del session_cache[voicechannel]

bot.run(os.environ.get("DISCORD_TOKEN"))
