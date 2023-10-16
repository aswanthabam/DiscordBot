# bot.py
import os,random,json, typing
import discord
import mysql.connector

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

TOKEN = os.environ['DISCORD_TOKEN']
GUILD = os.environ['DISCORD_GUILD']

ROLE_NEW = int(os.environ['ROLE_NEW'])
ROLE_NORMAL = int(os.environ['ROLE_NORMAL'])
ROLE_ADMIN = int(os.environ['ROLE_ADMIN'])
ROLE_BANNED = int(os.environ['ROLE_BANNED'])

SAYHI = int(os.environ['SAYHI'])
GENERAL_CHAT = int(os.environ['GENERAL_CHAT'])
BANNED = int(os.environ['BANNED'])
ADMIN_REQUEST = int(os.environ['ADMIN_REQUEST'])

client = commands.Bot(command_prefix='$',intents=intents)

my_guild = None

mydb = mysql.connector.connect(
  host=os.environ['DB_HOST'],
  user=os.environ['DB_USER'],
  password=os.environ['DB_PASSWORD'],
  database=os.environ['DB_DATABASE'],
)

cursor = mydb.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS DiscordProfile (
id INT PRIMARY KEY AUTO_INCREMENT NOT NULL UNIQUE,
discord_id VARCHAR(100) NOT NULL UNIQUE,
discord_name TEXT NOT NULL,
roles TEXT NOT NULL);""")

def get_roles_db(discord_id):
    try:
        query = "SELECT roles from DiscordProfile where discord_id=%s"
        cursor.execute(query,(discord_id,))
        data = cursor.fetchall()
        if len(data) != 1:
            print(data,str(discord_id))
            return False
        data = data[0]
        roles = json.loads(data[0])[1:]
        return roles
    except Exception as e:
        print(e)
        return False
def create_user_db(discord_id,name,roles):
    try:
        roles = [role.id for role in roles]
        roles = json.dumps(roles)
        query = "INSERT INTO DiscordProfile(discord_id,discord_name,roles) VALUES(%s, %s, %s)"
        print("NEW USER :",name,":",roles)
        cursor.execute(query,(discord_id,name,roles,))
        mydb.commit()
        return True
    except Exception as e:
        print(e)
        return False
def update_user_role_db(discord_id,roles):
    try:
        roles = [role.id for role in roles]
        roles = json.dumps(roles)
        query = "UPDATE DiscordProfile SET roles=%s where discord_id=%s;"
        cursor.execute(query,(roles,discord_id))
        mydb.commit()
        return True
    except Exception as e:
        print(e)
        return False
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
    try:
        sync = await client.tree.sync()
        print(sync)
    except:print("Error syncing commands ")
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
    print(member.roles)
    if not create_user_db(str(member.id),member.name,member.roles):
        await member.send("Hi,"+str(member.name)+"\nWe experienced an error while updating our database on your request.\nRun /sync-profile on server to sync. \n if you dont face any issue just sit back and relax")
    embed=discord.Embed(title=f"Welcome To Aswanth's Server. @"+member.name+"\nMay you get great experience in this server", color=random.randint(0, 0xFFFFFF))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_author(name=member.name, icon_url=member.display_avatar.url   )
    embed.set_footer(text=member.guild, icon_url=member.guild.icon.url if member.guild.icon else None)
    channel = client.get_channel(1162450448750477423)
    await channel.send("Checkout #new-commers-overview for more details on what to do",embed=embed)
    await member.send(embed=embed)


@client.tree.command(name="sync-role",description="Sync your role with database or back")
async def sync(ctx,from_:typing.Literal['database','discord'],to_:typing.Literal['database','discord']):
    response = ctx.response
    member = ctx.user
    if from_ == "discord" and to_ == "database":
        print("Request to sync with database")
        query = "SELECT id from DiscordProfile where discord_id=%s"
        cursor.execute(query,(str(member.id),))
        data = cursor.fetchall()
        if len(data) < 1:
            if not create_user_db(str(member.id),member.name,member.roles):
                await response.send_message("There was an error syncing with database")
                return
        else:
            if not update_user_role_db(str(member.id),member.roles):
                await response.send_message("There was an error syncing with database")
                return
        await response.send_message("Successfully synced discord role with database")
    elif from_ == "database" and to_ == "discord":
        print("Request to sync with discord")
        roles = get_roles_db(str(member.id))
        if roles:
            print(member.roles)
            for role in member.roles[1:]:
                await member.remove_roles(role)
            for role in roles:
                await member.add_roles(member.guild.get_role(role))
            await response.send_message("Successfully synced database with discord role")
        else:
            await response.send_message("There was an error in getting the data from discord(x1)")
    else:
        await response.send_message("invalid option to sync from :",from_,"to",to_)


client.run(TOKEN)