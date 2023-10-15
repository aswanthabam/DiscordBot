# bot.py
import os,random,json
import discord

from dotenv import load_dotenv
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client(intents=intents)
client._enable_debug_events = True
my_guild = None
async def proccess_json_request(message):
    try:res = json.loads(message.content)
    except:return None,False
    try:
        if res['type'] == "create_channel":
            print("Create Channel")
            guild = message.guild
            name = res['name']
            print("Name of channel:",name)
            await guild.create_text_channel(name)
            return guild,True
        elif res['type'] == 'create_role':
            print("Create Role")
            guild = message.guild
            name = res['name']
            print("Name of role:",name)
            await guild.create_role(name=name)
            return guild,True
        else:
            return None,True
    except Exception as e:
        print(e)
        return None,True
        
@client.event
async def on_message(message):
    if message.webhook_id:
        res = await proccess_json_request(message)
        if res[0]:
            print("Proccessed json request successfully!")
        elif not res[1]:
            print("Not a JSON")
            print(res,res[2])
        else:
            print("Error with request (JSON, but error)")
        
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
# @client.event
# async def on_socket_raw_receive(msg):
    # print(msg)

client.run(TOKEN)