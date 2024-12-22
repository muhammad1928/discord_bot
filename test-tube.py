from pytube import YouTube
import discord
from discord.ext import commands

f = open("../api_token_discord.txt", "r")

bot = commands.Bot(command_prefix="!")

@bot.command()
async def play(ctx, url):
    """Command to play audio from YouTube using pytube."""
    # Download the audio stream from YouTube
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(filename="audio.mp4")

    # Join voice channel and play audio
    if not ctx.voice_client:
        channel = ctx.author.voice.channel
        await channel.connect()

    voice_client = ctx.voice_client
    voice_client.play(discord.FFmpegPCMAudio("audio.mp4"))

    await ctx.send(f"Now playing: {yt.title}")

bot.run(f.read())
