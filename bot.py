# bot.py
import os,random,json
import discord

from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.reactions = True
intents.guild_reactions = True
intents.dm_reactions = True
intents.message_content = True

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

ROLE_NEW = int(os.getenv('ROLE_NEW'))
ROLE_NORMAL = int(os.getenv('ROLE_NORMAL'))
ROLE_ADMIN = int(os.getenv('ROLE_ADMIN'))
ROLE_BANNED = int(os.getenv('ROLE_BANNED'))

SAYHI = int(os.getenv('SAYHI'))
GENERAL_CHAT = int(os.getenv('GENERAL_CHAT'))
BANNED = int(os.getenv('BANNED'))
ADMIN_REQUEST = int(os.getenv('ADMIN_REQUEST'))

# client = discord.Client(intents=intents)
# client._enable_debug_events = True

client = commands.Bot(command_prefix='/',intents=intents)

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
            print("Permissions :",res['permissions'])
            send_messages = True
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False,send_messages=False),
            }
            if "new" in res['permissions']:
                overwrites[message.guild.get_role(ROLE_NEW)] = discord.PermissionOverwrite(read_messages=True,send_messages=send_messages)
            if "normal" in res['permissions']:
                overwrites[message.guild.get_role(ROLE_NORMAL)] = discord.PermissionOverwrite(read_messages=True,send_messages=send_messages)
            if "admin" in res['permissions']:
                overwrites[message.guild.get_role(ROLE_ADMIN)] = discord.PermissionOverwrite(read_messages=True,send_messages=True)
            if "banned" in res['permissions']:
                overwrites[message.guild.get_role(ROLE_BANNED)] = discord.PermissionOverwrite(read_messages=True,send_messages=send_messages)
            
            await guild.create_text_channel(name,overwrites=overwrites)
            return guild,True
        elif res['type'] == 'create_role':
            print("Create Role")
            guild = message.guild
            name = res['name']
            print("Name of role:",name)
            perms = discord.Permissions()
            if "send_messages" in res['permissions']:
                perms.send_messages = True
            if "read_messages" in res['permissions']:
                perms.read_messages = True
            await guild.create_role(name=name,hoist=True,color=random.randint(0, 0xFFFFFF),permissions=perms)
            return guild,True
        else:
            print("Invalid type")
            return None,True
    except Exception as e:
        print(e)
        return None,True
        
@client.event
async def on_raw_reaction_add(payload):
    print("Hello")
    emoji = payload.emoji
    member = payload.member
    print(emoji.id)
    if payload.channel_id == ADMIN_REQUEST:
        role_admin =member.guild.get_role(ROLE_ADMIN)
        if member.get_role(ROLE_ADMIN):
            # Admin
            if emoji == None:return
            if emoji.name == "🏁":
                print("Changing to admin")
                guild = client.get_guild(payload.guild_id)
                channel = guild.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                if message:
                    member = message.author
                    await member.add_roles(role_admin)
                    await message.reply("Congratulations! You are now an admin!")
                    embed=discord.Embed(title=f"Congragulations!! \n You are now promoted!\nYou can Access more channels", color=random.randint(0, 0xFFFFFF))
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_author(name=member.name, icon_url=member.display_avatar.url   )
                    embed.set_footer(text=member.guild, icon_url=member.guild.icon.url if member.guild.icon else None)
                    await member.send(embed=embed)
@client.event
async def on_message(message):
    if message.webhook_id:
        res = await proccess_json_request(message)
        if res[0]:
            print("Proccessed json request successfully!")
        elif not res[1]:
            print("Not a JSON")
        else:
            print("Error with request (JSON, but error)")
    elif message.content.startswith("/"):
        await client.process_commands(message)
    else:
        if message.channel.id == SAYHI:
            member = message.author
            print("Promoting user to : normal : ",message.author.id)
            role_normal = message.guild.get_role(ROLE_NORMAL)
            if not member.get_role(ROLE_NORMAL):
                if member.get_role(ROLE_NEW):await member.remove_roles(member.get_role(ROLE_NEW))
                await member.add_roles(role_normal)
                await message.reply("Welcome to server man!!!\nCongragulations! You are now promoted to normal user")
                embed=discord.Embed(title=f"Congragulations!! \n You are now promoted!\nYou can Access more channels", color=random.randint(0, 0xFFFFFF))
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_author(name=member.name, icon_url=member.display_avatar.url   )
                embed.set_footer(text=member.guild, icon_url=member.guild.icon.url if member.guild.icon else None)
                await member.send(embed=embed)
        elif message.channel.id == GENERAL_CHAT:
            member = message.author
            print("Promoting user to : normal : ",message.author.id)
            role_normal = message.guild.get_role(ROLE_NORMAL)
            if not member.get_role(ROLE_NORMAL):
                if member.get_role(ROLE_NEW):await member.remove_roles(member.get_role(ROLE_NEW))
                await member.add_roles(role_normal)
                embed=discord.Embed(title=f"Congragulations!! \n You are now promoted!\nYou can Access more channels", color=random.randint(0, 0xFFFFFF))
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_author(name=member.name, icon_url=member.display_avatar.url   )
                embed.set_footer(text=member.guild, icon_url=member.guild.icon.url if member.guild.icon else None)
                await member.send(embed=embed)
        
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
    role_new = member.guild.get_role(ROLE_NEW)
    await member.add_roles(role_new)
    embed=discord.Embed(title=f"Welcome To Aswanth's Server. @"+member.name+"\nMay you get great experience in this server", color=random.randint(0, 0xFFFFFF))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_author(name=member.name, icon_url=member.display_avatar.url   )
    embed.set_footer(text=member.guild, icon_url=member.guild.icon.url if member.guild.icon else None)
    channel = client.get_channel(1162450448750477423)
    await channel.send("Checkout #new-commers-overview for more details on what to do",embed=embed)
    await member.send(embed=embed)

@client.command()
async def test(ctx, arg):
    await ctx.send(arg)


# client.add_command(make_admin)
client.run(TOKEN)