import os
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import youtube_dl

from myserver import server_on

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# บันทึก queue ของเพลง
queue = []
repeat = False

# ฟังก์ชั่นสำหรับเล่นเพลง
async def play_song(ctx, url):
    # ดาวน์โหลดและเล่นเพลง
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['url']
    
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client.is_playing():
        voice_client.play(discord.FFmpegPCMAudio(URL), after=lambda e: check_queue(ctx))

# ฟังก์ชั่นตรวจสอบคิวเพลง
def check_queue(ctx):
    if repeat and len(queue) > 0:
        song = queue[0]
        bot.loop.create_task(play_song(ctx, song))

    elif len(queue) > 0:
        queue.pop(0)
        if len(queue) > 0:
            song = queue[0]
            bot.loop.create_task(play_song(ctx, song))

# คำสั่งเชื่อมต่อ
@slash.slash(name="join")
async def join(ctx: SlashContext):
    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send("เข้าร่วมห้องแล้ว!")

# คำสั่งเล่นเพลง
@slash.slash(name="play")
async def play(ctx: SlashContext, *, url):
    queue.append(url)
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client.is_playing():
        await play_song(ctx, url)
    await ctx.send(f"เล่นเพลงจาก {url} แล้ว!")

# คำสั่งวนซ้ำเพลง
@slash.slash(name="repeat")
async def repeat_song(ctx: SlashContext):
    global repeat
    repeat = not repeat
    if repeat:
        await ctx.send("เปิดโหมดวนซ้ำเพลง!")
    else:
        await ctx.send("ปิดโหมดวนซ้ำเพลง!")

# คำสั่งหยุดเล่นเพลง
@slash.slash(name="stop")
async def stop(ctx: SlashContext):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("หยุดเล่นเพลงแล้ว!")

# คำสั่งออกจากห้อง
@slash.slash(name="leave")
async def leave(ctx: SlashContext):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("ออกจากห้องแล้ว!")

# เริ่มบอท

server_on()

bot.run(os.getenv('TOKEN'))
