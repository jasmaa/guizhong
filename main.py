import os
from dotenv import load_dotenv
from src.bot import create_and_run_bot

if __name__ == "__main__":
    load_dotenv()

    discord_token = os.environ.get("DISCORD_TOKEN")
    discord_command_prefix = os.environ.get("DISCORD_COMMAND_PREFIX", "!")

    create_and_run_bot(discord_token, discord_command_prefix)
