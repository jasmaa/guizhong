## Setup

### Setup Discord bot

Create a new bot on [Discord developer portal](https://discord.com/developers/applications).

Regenerate the bot token and copy its value. This will be `DISCORD_TOKEN`.

Go to Privileged Gateway Intents section. Enable message content intent.

Go to OAuth2 page and copy the client id. This wil be `DISCORD_CLIENT_ID`.

Visit following URL and invite bot to server:

```
https://discord.com/api/oauth2/authorize?client_id=<FILL WITH DISCORD_CLIENT_ID>&permissions=3148800&scope=bot%20applications.commands
```


### Run bot

Create `.env` from `sample.env` and fill with values.

Install [ffmpeg](https://ffmpeg.org/). Example is for Ubuntu:

```
sudo apt-get install ffmpeg
```

Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```
pip3 install uv
```

Install deps and run bot:

```
uv run main.py
```


### Setup systemd service (optional)

Create `guizhong.service` from `guizhong.sample.service`. Fill with your configuration:

- WorkDirectory will be the location of the your cloned repo.
- User will be the user that will run the bot. Make sure you run `sudo pip install -r "requirements.txt"` if using `root`.

Copy `guizhong.service` to `/etc/systemd/system`.

Reload systemd and start bot with:

```
sudo systemctl daemon-reload
sudo systemctl enable guizhong.service
sudo systemctl start guizhong.service
```

Check status of service with:

```
sudo systemctl status guizhong.service
journalctl -u guizhong.service | tail
```