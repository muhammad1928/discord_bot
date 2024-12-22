import discord
from discord.ext import commands
import yt_dlp as youtube_dl

# Open the token from a file (for security purposes, it's better to use environment variables or a config file)
with open("../api_token_discord.txt", "r") as f:
    TOKEN = f.read().strip()

# Bot setup
intents = discord.Intents.default()
intents.members = True  # For accessing member info (Server Members Intent)
intents.presences = True  # For tracking presence (Presence Intent)
intents.message_content = True  # Required for message content access
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Variables
queue = []
current_song = None
is_paused = False

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

# Simple chat interaction
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Example responses
    if "hello" in message.content.lower():
        await message.channel.send(f"Hello {message.author.mention}! How can I assist you today?")
    elif "how are you" in message.content.lower():
        await message.channel.send("I'm just a bot, but I'm doing great! Thanks for asking.")
    elif "help" in message.content.lower():
        await message.channel.send("Here are some commands you can use: !play, !pause, !resume, !next, !stop, !playlist, !join, !leave")

    # Process commands
    await bot.process_commands(message)

# Join the voice channel
@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command!")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

# Leave the voice channel
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I am not connected to a voice channel.")

# Play a song
@bot.command()
async def play(ctx, *, url):
    global is_paused
    global current_song

    is_paused = False

    # Ensure the bot is connected to a voice channel
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You need to be in a voice channel or connect me to one!")
            return

    # Add the song to the queue
    queue.append(url)

    # Play the song if no other song is currently playing
    if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
        current_song = queue.pop(0)
        await play_song(ctx, current_song)
    else:
        await ctx.send("Added to the queue!")

async def play_song(ctx, url):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        title = info['title']

    ctx.voice_client.play(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS), after=lambda e: next_song(ctx))
    await ctx.send(f"Now playing: {title}")

# Pause the song
@bot.command()
async def pause(ctx):
    global is_paused
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        is_paused = True
        await ctx.send("Music paused.")
    else:
        await ctx.send("No music is playing.")

# Resume the song
@bot.command()
async def resume(ctx):
    global is_paused
    if is_paused:
        ctx.voice_client.resume()
        is_paused = False
        await ctx.send("Music resumed.")
    else:
        await ctx.send("Music is not paused.")

# Skip to the next song
@bot.command()
async def next(ctx):
    if queue:
        ctx.voice_client.stop()
        await ctx.send("Skipped to the next song.")
    else:
        await ctx.send("The queue is empty.")

# Display the playlist
@bot.command()
async def playlist(ctx):
    if queue:
        message = "\n".join([f"{i + 1}. {url}" for i, url in enumerate(queue)])
        await ctx.send(f"Current playlist:\n{message}")
    else:
        await ctx.send("The playlist is empty.")

# Stop playback
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Music stopped.")
    else:
        await ctx.send("I'm not playing anything.")

# Helper: Automatically play the next song in the queue
def next_song(ctx):
    global current_song
    if queue:
        current_song = queue.pop(0)
        fut = play_song(ctx, current_song)
        bot.loop.create_task(fut)
    else:
        current_song = None

# Run the bot
bot.run(TOKEN)
