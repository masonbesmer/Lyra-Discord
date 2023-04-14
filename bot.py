import os
from dotenv import load_dotenv
import requests
import discord
import logging
import json
import random
from discord import Interaction, Message, app_commands
import youtube_dl
import re
from urllib import parse, request

load_dotenv()

token = os.getenv("discord_token")
my_guild = "Night City"
guild=discord.Object(id=925192180480491540)



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == my_guild:
            break
    
    await tree.sync(guild=discord.Object(id=925192180480491540))

    print(
        f"{client.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )

@client.event
async def on_message(message: Message):
    if message.author == client.user:
       return
    
    if "bee" in message.content.lower():
        await message.channel.send("According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.")

    if "was" in message.content.lower():
        await message.channel.send("was was")

    if "greg" in message.content.lower():
        await message.channel.send("greg")

    if "simply" in message.content.lower():
        await message.channel.send("shrimply")

rule34api = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index"

@tree.command(name = "rule34", description="Ask Lyra to query Rule 34 based on specified tags", nsfw=True, guild=guild)
@app_commands.describe(tags="The tags you want to search, separated by spaces")
async def rule_34(interaction, tags: str):
    PARAMS = {'limit':1000,
              'tags':tags,
              'json':1}

    r = requests.get(url=rule34api, params=PARAMS)
    handler.handle

    try:
        data = json.loads(r.content)
    except json.JSONDecodeError:
        await interaction.response.send_message(f"no results found for {tags}, or an error occured parsing JSON data, i don't fucking know, i'm just a god damn bot")
        return

    count = len(data)

    if count == 0:
        await interaction.response.send_message(f"no results found for {tags}")
        return
    
    image_data = data[random.randint(0,count-1)]
 
    embed = discord.Embed(
        title=f"search for \"{tags}\"",
        description=f"author: {image_data['owner']}",
        color=0xFF69B4
    )
    embed.set_image(url=image_data['file_url'])

    embed.add_field(name="", value=f"[direct link]({image_data['file_url']})", inline=False)

    await interaction.response.send_message(embed=embed)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@tree.command(name="join", description="Ask Lyra to join your current voice channel", guild=guild)
async def join(interaction: Interaction):
    if interaction.user.voice is None:
        return await interaction.response.send_message("silly goose, i can't join a voice channel if you aren't in one!")

    voice_channel = interaction.user.voice.channel
    if interaction.guild.voice_client is None:
        vc = await voice_channel.connect()
    else:
        vc = interaction.guild.voice_client
        if vc.channel == voice_channel:
            return await interaction.response.send_message("i'm literally already in here with you...")
    await vc.move_to(voice_channel)

    await interaction.guild.change_voice_state(channel=voice_channel, self_deaf=True, self_mute=False)
    return await interaction.response.send_message("okay, joined!")

@tree.command(name="leave", description="Ask Lyra to leave the her current voice channel", guild=guild)
async def leave(interaction: Interaction):
    voice_client = None
    if interaction.guild.voice_client is None:
        return await interaction.response.send_message("hey dumbass, i'm not even in a voice channel")
    else:
        voice_client = interaction.guild.voice_client
        await voice_client.disconnect()
        return await interaction.response.send_message("okay, left!")

@tree.command(name="play", description="Search YouTube for a video and play it (or provide a url)", guild=guild)
@app_commands.describe(input="YouTube URL or search query")
async def play(interaction: Interaction, input: str):
    if "https://youtu.be/" in input or "http://youtube.com/watch?v=" in input:
        #link provided
        await interaction.response.send_message("i cannot do that yet")
    query_string = parse.urlencode({'search_query': input})
    html_content = request.urlopen("https://www.youtube.com/results?search_query=" + query_string)
    search_content = html_content.read().decode()
    search_results = re.findall(r'\/watch\?v=\w+', search_content)
    await interaction.response.send_message("https://youtube.com/" + search_results[0])

client.run(token, log_handler=handler, log_level=logging.DEBUG)
