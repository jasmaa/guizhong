import pytest
from src.handler import Handler


@pytest.mark.asyncio
async def test_info_author_not_in_voice(mocker):
    bot = mocker.MagicMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice = None

    handler = Handler(bot=bot)

    await handler.info(ctx)

    args = ctx.send.call_args.args
    assert "You need to be in a voice channel to use this command." in args[0]


@pytest.mark.asyncio
async def test_info_no_music_queued(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice.channel = voicechannel

    handler = Handler(bot=bot)

    await handler.info(ctx)

    args = ctx.send.call_args.args
    assert "You need to have music queued to use this command." in args[0]


@pytest.mark.asyncio
async def test_info_music_queued(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice.channel = voicechannel
    youtubedl_cls = mocker.patch("yt_dlp.YoutubeDL")
    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }
    mocker.patch("discord.FFmpegPCMAudio")

    handler = Handler(bot=bot)

    await handler.play(ctx, "https://youtube.com/watch?v=123")
    await handler.info(ctx)

    args = ctx.send.call_args.args
    assert "Now playing: It's MyGO!!!!!" in args[0]


@pytest.mark.asyncio
async def test_play_queue_music(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice.channel = voicechannel
    youtubedl_cls = mocker.patch("yt_dlp.YoutubeDL")
    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }
    mocker.patch("discord.FFmpegPCMAudio")

    handler = Handler(bot=bot)

    await handler.play(ctx, "https://youtube.com/watch?v=123")

    args = ctx.send.call_args.args
    assert "Successfully queued It's MyGO!!!!!!" in args[0]
