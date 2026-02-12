import asyncio
import discord
from src.errors import InvalidSongURLError
from src.session import Session
from src.song import Song
from src.utils import parse_youtube_video_url

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

COMMAND_PREFIX = "!"
AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE = "You need to be in a voice channel to use this command. Try joining a voice and trying again."
SAMPLE_COMMAND_MESSAGE_PART = (
    f"Try playing something with `{COMMAND_PREFIX}play <YOUTUBE VIDEO URL>`."
)
NO_SESSION_FOUND_MESSAGE = (
    f"You need to have music queued to use this command. {SAMPLE_COMMAND_MESSAGE_PART}"
)
INVALID_ARGS_FOR_PLAY_MESSAGE = (
    f"A single URL must be provided for this command. {SAMPLE_COMMAND_MESSAGE_PART}"
)
INVALID_YOUTUBE_URL_FOR_PLAY_MESSAGE = (
    "Invalid URL provided. Please provide a valid Youtube video URL."
)
INVALID_NUMBER_OF_SONGS_TO_SKIP_MESSAGE = f"Invalid number of songs to skip. Try skipping songs with `{COMMAND_PREFIX}skip <NUMBER OF SONGS>`."
GENERAL_ERROR_FOR_PLAY_MESSAGE = (
    "Unable to queue song due to an unknown error. Please contact the bot owner."
)
MAX_SONG_INFOS_TO_DISPLAY = 5


class Handler:
    def __init__(self, bot):
        self.session_cache = {}
        self.bot = bot

    async def __get_author_voicechannel(self, ctx):
        """Gets voicechannel caller is in."""
        voice_state = ctx.author.voice

        if voice_state is None:
            return None

        voicechannel = voice_state.channel
        return voicechannel

    async def __play_queue(self, voicechannel_id):
        """Plays songs going down the session queue."""
        session = self.session_cache[voicechannel_id]
        vc = session.vc
        queue = session.queue

        if len(queue) > 0:
            # Play next song in the queue
            song = queue[0]

            def post_play(e):
                queue.pop(0)
                fut = session.play_music_task = asyncio.run_coroutine_threadsafe(
                    self.__play_queue(voicechannel_id),
                    self.bot.loop,
                )
                try:
                    fut.result
                except:
                    pass

            vc.stop()

            # Taken from: https://stackoverflow.com/questions/75680967/using-yt-dlp-in-discord-py-to-play-a-song
            source_url = song.get_source_url()
            source = discord.FFmpegPCMAudio(source_url, **FFMPEG_OPTIONS)
            vc.play(source, after=post_play)
        else:
            # No songs left in queue, clean up session and leave voice channel
            del self.session_cache[voicechannel_id]
            await vc.disconnect()

    async def info(self, ctx):
        """Provides info on current queue bot is playing."""
        voicechannel = await self.__get_author_voicechannel(ctx)
        if voicechannel is None:
            await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
            return

        if voicechannel.id not in self.session_cache:
            await ctx.send(NO_SESSION_FOUND_MESSAGE)
            return

        session = self.session_cache[voicechannel.id]
        queue = session.queue

        if len(queue) <= 0:
            await ctx.send("```\nNot playing\n```")
            return

        current_song = queue[0]
        await ctx.send(
            "```\n"
            + f"Now playing: {current_song.title} [{current_song.duration}s]\n\n"
            + "Queue:\n"
            + "\n".join(
                [f"{i+1}: {song.title}" for i, song in enumerate(queue)][
                    :MAX_SONG_INFOS_TO_DISPLAY
                ]
            )
            + "\n```"
        )

    async def play(self, ctx, *args):
        """Downloads and plays song in argument. If bot is not in call, bot will join call."""
        if not args:
            await ctx.send(INVALID_ARGS_FOR_PLAY_MESSAGE)
            return
        if len(args) != 1:
            await ctx.send(INVALID_ARGS_FOR_PLAY_MESSAGE)
            return

        voicechannel = await self.__get_author_voicechannel(ctx)
        if voicechannel is None:
            await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
            return

        # Connect or get voice client
        if voicechannel.id not in self.session_cache:
            vc = await voicechannel.connect()
            self.session_cache[voicechannel.id] = Session(vc=vc)

        session = self.session_cache[voicechannel.id]
        queue = session.queue

        # Extract and queue song
        url = args[0]
        video_id = None
        try:
            video_id = parse_youtube_video_url(url)
            song = Song.extract_song(video_id)
            queue.append(song)
            print(f"Added {song} to queue")
            await ctx.send(f"Successfully queued {song.title}!")
        except InvalidSongURLError:
            await ctx.send(INVALID_YOUTUBE_URL_FOR_PLAY_MESSAGE)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send(GENERAL_ERROR_FOR_PLAY_MESSAGE)
        finally:
            # Start a new music task if nothing is playing
            if session.play_music_task is None:
                session.play_music_task = asyncio.create_task(
                    self.__play_queue(voicechannel.id)
                )

    async def pause(self, ctx):
        """Pauses current song."""
        voicechannel = await self.__get_author_voicechannel(ctx)
        if voicechannel is None:
            await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
            return

        if voicechannel.id not in self.session_cache:
            await ctx.send(NO_SESSION_FOUND_MESSAGE)
            return

        session = self.session_cache[voicechannel.id]
        vc = session.vc

        vc.pause()

    async def resume(self, ctx):
        """Resumes current song."""
        voicechannel = await self.__get_author_voicechannel(ctx)
        if voicechannel is None:
            await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
            return

        if voicechannel.id not in self.session_cache:
            await ctx.send(NO_SESSION_FOUND_MESSAGE)
            return

        session = self.session_cache[voicechannel.id]
        vc = session.vc

        vc.resume()

    async def skip(self, ctx, *args):
        """Skips current song in queue."""

        n_skip = 1
        if args is not None and len(args) == 1:
            try:
                n_skip = int(args[0])
            except ValueError as e:
                await ctx.send(INVALID_NUMBER_OF_SONGS_TO_SKIP_MESSAGE)
                return

        # Cannot skip fewer than 1 song
        if n_skip <= 0:
            await ctx.send(INVALID_NUMBER_OF_SONGS_TO_SKIP_MESSAGE)
            return

        voicechannel = await self.__get_author_voicechannel(ctx)
        if voicechannel is None:
            await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
            return

        if voicechannel.id not in self.session_cache:
            await ctx.send(NO_SESSION_FOUND_MESSAGE)
            return

        session = self.session_cache[voicechannel.id]
        vc = session.vc
        queue = session.queue

        # Remove n-1 next songs
        del queue[1:n_skip]

        # Stopping current stream will trigger after callback and queue up next song
        vc.stop()

    async def stop(self, ctx):
        """Clears songs and stops playing from queue."""
        voicechannel = await self.__get_author_voicechannel(ctx)
        if voicechannel is None:
            await ctx.send(AUTHOR_NOT_IN_VOICE_CHANNEL_MESSAGE)
            return

        if voicechannel.id not in self.session_cache:
            await ctx.send(NO_SESSION_FOUND_MESSAGE)
            return

        session = self.session_cache[voicechannel.id]

        # Clear queue and stop voice client to force session clean-up
        session.queue = []
        session.vc.stop()
