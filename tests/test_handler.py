import pytest
from src.handler import Handler


@pytest.mark.asyncio
async def test_info_songs_queued(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
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
async def test_info_author_not_in_voice(mocker):
    bot = mocker.MagicMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice = None

    handler = Handler(bot=bot)

    await handler.info(ctx)

    args = ctx.send.call_args.args
    assert "You need to be in a voice channel to use this command." in args[0]


@pytest.mark.asyncio
async def test_info_no_songs_queued(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
    ctx = mocker.AsyncMock()
    ctx.author.voice.channel = voicechannel

    handler = Handler(bot=bot)

    await handler.info(ctx)

    args = ctx.send.call_args.args
    assert "You need to have music queued to use this command." in args[0]


@pytest.mark.asyncio
async def test_play_song_provided(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
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


@pytest.mark.asyncio
async def test_play_author_not_in_voice(mocker):
    bot = mocker.MagicMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice = None
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
    assert "You need to be in a voice channel to use this command." in args[0]


@pytest.mark.asyncio
async def test_play_bad_input(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
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

    await handler.play(ctx)

    args = ctx.send.call_args.args
    assert "A single URL must be provided for this command." in args[0]

    await handler.play(
        ctx, "https://youtube.com/watch?v=123", "https://youtube.com/watch?v=456"
    )

    args = ctx.send.call_args.args
    assert "A single URL must be provided for this command." in args[0]

    await handler.play(ctx, "not a url")

    args = ctx.send.call_args.args
    assert "Invalid URL provided." in args[0]


@pytest.mark.asyncio
async def test_pause_songs_queued(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
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
    await handler.pause(ctx)

    vc.pause.assert_called()


@pytest.mark.asyncio
async def test_pause_author_not_in_voice(mocker):
    bot = mocker.MagicMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice = None
    youtubedl_cls = mocker.patch("yt_dlp.YoutubeDL")
    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }
    mocker.patch("discord.FFmpegPCMAudio")

    handler = Handler(bot=bot)

    await handler.pause(ctx)

    args = ctx.send.call_args.args
    assert "You need to be in a voice channel to use this command." in args[0]


@pytest.mark.asyncio
async def test_resume_songs_queued(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
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
    await handler.pause(ctx)
    await handler.resume(ctx)

    vc.resume.assert_called()


@pytest.mark.asyncio
async def test_resume_author_not_in_voice(mocker):
    bot = mocker.MagicMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice = None
    youtubedl_cls = mocker.patch("yt_dlp.YoutubeDL")
    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }
    mocker.patch("discord.FFmpegPCMAudio")

    handler = Handler(bot=bot)

    await handler.resume(ctx)

    args = ctx.send.call_args.args
    assert "You need to be in a voice channel to use this command." in args[0]


@pytest.mark.asyncio
async def test_skip_default_stops_current_song(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
    ctx = mocker.AsyncMock()
    ctx.author.voice.channel = voicechannel
    youtubedl_cls = mocker.patch("yt_dlp.YoutubeDL")
    mocker.patch("discord.FFmpegPCMAudio")

    handler = Handler(bot=bot)

    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }
    await handler.play(ctx, "https://youtube.com/watch?v=123")

    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "Shikairo Days",
        "duration": 10,
        "url": "https://example.com/shikairodays.mp3",
    }
    await handler.play(ctx, "https://youtube.com/watch?v=456")

    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "Batman",
        "duration": 67,
        "url": "https://example.com/batman.mp3",
    }
    await handler.play(ctx, "https://youtube.com/watch?v=789")

    await handler.skip(ctx)

    vc.stop.assert_called()


@pytest.mark.asyncio
async def test_skip_multiple_removes_n_minus_one_and_stops_current_song(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
    ctx = mocker.AsyncMock()
    ctx.author.voice.channel = voicechannel
    youtubedl_cls = mocker.patch("yt_dlp.YoutubeDL")
    mocker.patch("discord.FFmpegPCMAudio")

    handler = Handler(bot=bot)

    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }
    await handler.play(ctx, "https://youtube.com/watch?v=123")

    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "Shikairo Days",
        "duration": 10,
        "url": "https://example.com/shikairodays.mp3",
    }
    await handler.play(ctx, "https://youtube.com/watch?v=456")

    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "Batman",
        "duration": 67,
        "url": "https://example.com/batman.mp3",
    }
    await handler.play(ctx, "https://youtube.com/watch?v=789")

    await handler.skip(ctx, 2)

    assert len(handler.session_cache["111111111111111111"].queue) == 2
    vc.stop.assert_called()


@pytest.mark.asyncio
async def test_skip_bad_inputs(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
    ctx = mocker.AsyncMock()
    ctx.author.voice.channel = voicechannel
    youtubedl_cls = mocker.patch("yt_dlp.YoutubeDL")
    mocker.patch("discord.FFmpegPCMAudio")

    handler = Handler(bot=bot)

    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }
    await handler.play(ctx, "https://youtube.com/watch?v=123")

    await handler.skip(ctx, "not a number")
    args = ctx.send.call_args.args
    assert "Invalid number of songs to skip." in args[0]

    await handler.skip(ctx, 0)
    args = ctx.send.call_args.args
    assert "Invalid number of songs to skip." in args[0]

    await handler.skip(ctx, -1)
    args = ctx.send.call_args.args
    assert "Invalid number of songs to skip." in args[0]

    await handler.skip(ctx, 1, 2)
    args = ctx.send.call_args.args
    assert "Invalid number of songs to skip." in args[0]


@pytest.mark.asyncio
async def test_skip_author_not_in_voice(mocker):
    bot = mocker.MagicMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice = None
    youtubedl_cls = mocker.patch("yt_dlp.YoutubeDL")
    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }
    mocker.patch("discord.FFmpegPCMAudio")

    handler = Handler(bot=bot)

    await handler.skip(ctx)

    args = ctx.send.call_args.args
    assert "You need to be in a voice channel to use this command." in args[0]


@pytest.mark.asyncio
async def test_stop_songs_queued(mocker):
    bot = mocker.MagicMock()
    voicechannel = mocker.AsyncMock()
    voicechannel.id = "111111111111111111"
    vc = mocker.AsyncMock()
    voicechannel.connect.return_value = vc
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
    await handler.stop(ctx)

    vc.stop.assert_called()


@pytest.mark.asyncio
async def test_stop_author_not_in_voice(mocker):
    bot = mocker.MagicMock()
    ctx = mocker.AsyncMock()
    ctx.author.voice = None
    youtubedl_cls = mocker.patch("yt_dlp.YoutubeDL")
    youtubedl_cls.return_value.__enter__.return_value.extract_info.return_value = {
        "title": "It's MyGO!!!!!",
        "duration": 9000,
        "url": "https://example.com/mygo.mp3",
    }
    mocker.patch("discord.FFmpegPCMAudio")

    handler = Handler(bot=bot)

    await handler.stop(ctx)

    args = ctx.send.call_args.args
    assert "You need to be in a voice channel to use this command." in args[0]
