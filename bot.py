# bot.py
import os,random

import discord
from dotenv import load_dotenv
intents = discord.Intents.default()
intents.members = True
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client(intents=intents)

my_guild = None
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            my_guild = guild
            print("Started on guild : "+my_guild.name)
            print("Channels : ")
            for channel in my_guild.channels:
                print(channel, channel.id)
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_member_join(member):
    embed=discord.Embed(title=f"Welcome To Aswanth's Server. @"+member.name+"\nMay you get great experience in this server", color=random.randint(0, 0xFFFFFF))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_author(name=member.name, icon_url=member.display_avatar.url   )
    embed.set_footer(text=member.guild, icon_url=member.guild.icon.url if member.guild.icon else None)
    channel = client.get_channel(1162450448750477423)
    await channel.send(embed=embed)
    await member.send(embed=embed)

client.run(TOKEN)