import discord
from discord.ext import commands
import asyncio
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None

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
        await ctx.send("Left the voice channel!")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command()
async def play(ctx, *, url):
    global voice_client
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
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
        
        source = discord.FFmpegPCMAudio(executable="ffmpeg", source=url2)
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(source, after=lambda e: print(f"Finished playing: {e}"))
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

#bot.run aqui
