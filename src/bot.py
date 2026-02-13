import discord
from discord.ext import commands
from src.handler import Handler


def create_bot(discord_command_prefix):

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix=discord_command_prefix, intents=intents)
    handler = Handler(bot=bot)

    @bot.event
    async def on_ready():
        print("Bot is ready!")

    @bot.command()
    async def info(ctx):
        print(handler.session_cache)
        await handler.info(ctx)

    @bot.command()
    async def play(ctx, *args):
        await handler.play(ctx, *args)

    @bot.command()
    async def pause(ctx):
        await handler.pause(ctx)

    @bot.command()
    async def resume(ctx):
        await handler.resume(ctx)

    @bot.command()
    async def skip(ctx, *args):
        await handler.skip(ctx, *args)

    @bot.command()
    async def stop(ctx):
        await handler.stop(ctx)

    return bot


def create_and_run_bot(discord_token, discord_command_prefix):
    bot = create_bot(discord_command_prefix)
    bot.run(discord_token)
