import requests
import discord
import logging
import json
import random
from discord import Interaction, Message, app_commands
import youtube_dl

token = "MTA5MDQ1OTE3ODY4Mzg2MzExMA.G9fE2C.urWS9YYEz6REOleMSQzsnIiXdvhVM6GdLxZJdw"
my_guild = "Night City"
guild=discord.Object(id=925192180480491540)

administrators=[ 181235555936239616 ]

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

    if "was" in message.content.lower():
        await message.channel.send("was was")

    if "greg" in message.content.lower():
        await message.channel.send("greg")

    if "simply" in message.content.lower():
        await message.channel.send("shrimply")

    if "nigger" in message.content.lower():
        await message.channel.send("hey mister, you said a bad word!")
        await message.delete()

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

@tree.command(name="restart", description="Restart Lyra's systemd service (authorized users only)", guild=guild)
async def restart(interaction: Interaction):
    await interaction.response.send_message("cmd recieved")
    # if interaction.message.author.id in administrators:
    #     await interaction.response.send_message("sure, restarting")
    #     SystemExit.code(0)
    #     return await interaction.response.send_message("uh oh, stinky! an unknown error occured!")
    # await interaction.response.send_message("ya not on the list")

client.run(token, log_handler=handler, log_level=logging.DEBUG)