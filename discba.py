import discord
from discord.ext import commands
import asyncio
import yt_dlp
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None
queue = []

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        global voice_client
        if voice_client is None or not voice_client.is_connected():
            voice_client = await channel.connect()
            await ctx.send("Joined the voice channel!")
        else:
            await ctx.send("I'm already in a voice channel!")
    else:
        await ctx.send("You need to be in a voice channel for me to join!")

@bot.command()
async def leave(ctx):
    global voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        voice_client = None
        queue.clear()
        await ctx.send("Left the voice channel and cleared the queue!")
    else:
        await ctx.send("I'm not in a voice channel!")

def play_next(ctx):
    """Plays the next song in the queue, if available."""
    global queue, voice_client
    if queue:
        next_url = queue.pop(0)
        source = discord.FFmpegPCMAudio(executable="ffmpeg", source=next_url)
        voice_client.play(source, after=lambda e: play_next(ctx))
    else:
        asyncio.run_coroutine_threadsafe(ctx.send("Queue is empty, stopping playback!"), bot.loop)

@bot.command()
async def play(ctx, *, search_query):
    global voice_client, queue
    if not voice_client or not voice_client.is_connected():
        await ctx.send("I'm not in a voice channel! Use `!join` first.")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'audio.mp3',
        'default_search': 'ytsearch',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            url2 = info['url']

        if voice_client.is_playing():
            queue.append(url2)
            await ctx.send(f"Added to queue: {info['title']}")
        else:
            source = discord.FFmpegPCMAudio(executable="ffmpeg", source=url2)
            voice_client.play(source, after=lambda e: play_next(ctx))
            await ctx.send(f"Now playing: {info['title']}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def stop(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Stopped playback!")
    else:
        await ctx.send("No audio is currently playing.")

@bot.command()
async def skip(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop() 
        await ctx.send("Skipped to the next song!")
    else:
        await ctx.send("No audio is currently playing.")

bot.run("MTMwNzkzMTQ5MDQzNjI1MTY3OA.GpsIaT.pUmWr4ljKrgmvEz-xmQJVeem8vXE7DFnAn8_EM")
