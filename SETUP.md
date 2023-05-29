## Setup

### Setup Discord bot

Create a new bot on [Discord developer portal](https://discord.com/developers/applications).

Regenerate the bot token and copy its value. This will be `DISCORD_TOKEN`.

Go to Privileged Gateway Intents section. Enable message content intent.

Go to OAuth2 page and copy the client id. This wil be `DISCORD_CLIENT_ID`.

Visit following URL and invite bot to server:

```
https://discord.com/api/oauth2/authorize?client_id=<FILL WITH DISCORD_CLIENT_ID>&scope=bot%20applications.commands
```


### Add music

Add MP3s to the `music` folder in the repo root.


### Run bot

Create `.env` from `sample.env` and fill with values.

Install deps and run bot:

```
pip install -r "requirements.txt"
python main.py
```