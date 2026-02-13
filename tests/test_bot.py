import pytest
from src.bot import create_and_run_bot


@pytest.mark.asyncio
async def test_create_and_run_bot(mocker):
    mocker.patch("discord.Intents.default")
    mocker.patch("discord.ext.commands.Bot")
    mocker.patch("src.handler.Handler")

    create_and_run_bot("my_token", "!")
