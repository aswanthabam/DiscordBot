# bot.py
import os,random,json, typing
import discord
import mysql.connector

from dotenv import load_dotenv
from discord.ext import commands
# Intents
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.reactions = True
intents.guild_reactions = True
intents.dm_reactions = True
intents.message_content = True
# load .env
load_dotenv()
# Load tokens
TOKEN = os.environ['DISCORD_TOKEN']
GUILD = os.environ['DISCORD_GUILD']
# Roles
ROLE_NEW = int(os.environ['ROLE_NEW'])
ROLE_NORMAL = int(os.environ['ROLE_NORMAL'])
ROLE_ADMIN = int(os.environ['ROLE_ADMIN'])
ROLE_BANNED = int(os.environ['ROLE_BANNED'])
# List all valid roles for future purpose
VALID_ROLES = [ROLE_NEW,ROLE_NORMAL,ROLE_ADMIN, ROLE_BANNED]
# cahnnels
SAYHI = int(os.environ['SAYHI'])
GENERAL_CHAT = int(os.environ['GENERAL_CHAT'])
BANNED = int(os.environ['BANNED'])
ADMIN_REQUEST = int(os.environ['ADMIN_REQUEST'])
# create client
client = commands.Bot(command_prefix='$',intents=intents)

my_guild = None
# connect with database
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
roles TEXT NOT NULL);""") # Create table

"""Function to create an embed message and return"""
def get_embed_message(title,member,color=None):
    embed=discord.Embed(title=title, color=color if color else random.randint(0, 0xFFFFFF))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_author(name=member.name, icon_url=member.display_avatar.url   )
    embed.set_footer(text=member.guild, icon_url=member.guild.icon.url if member.guild.icon else None)
    return embed
"""Get list of all members from database"""
def get_all_members():
    try:
        members = {}
        query = "SELECT discord_id,roles FROM DiscordProfile"
        cursor.execute(query)
        data = cursor.fetchall()
        for i in data:
            members[i[0]] = json.loads(i[1])
        print(members)
        return members
    except Exception as e:
        print(e)
        return None
"""Get role of a user from the database using the discord id"""
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
"""Insert the data of a new user"""
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
"""Update roles of a member from discord to database"""
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
"""Function used to proccess a webhook request, which is in json format"""
async def proccess_json_request(message):
    try:res = json.loads(message.content)
    except:return None,False
    try:
        if res['type'] == "create_channel":
            # Create channel request
            print("Create Channel")
            guild = message.guild
            name = res['name']
            print("Name of channel:",name)
            print("Permissions :",res['permissions'])
            send_messages = True
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False,send_messages=False),
            }
            # set permission for the roles
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
            # request to create a roles
            print("Create Role")
            guild = message.guild
            name = res['name']
            print("Name of role:",name)
            # change default permission of the role
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

"""On a reaction add"""        
@client.event
async def on_raw_reaction_add(payload):
    emoji = payload.emoji # the emoji added
    member = payload.member # member
    if payload.channel_id == ADMIN_REQUEST:
        # from the admin request channel, used to change a user permission to admin
        role_admin =member.guild.get_role(ROLE_ADMIN)
        if member.get_role(ROLE_ADMIN):
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
                    embed=get_embed_message(member=member,title=f"Congragulations!! \n You are now promoted!\nYou can Access more channels")
                    await member.send(embed=embed)
""" On message recieve """
@client.event
async def on_message(message):
    if message.webhook_id: # a webhook reques
        res = await proccess_json_request(message) # try to proccess as a json request
        if res[0]:print("Proccessed json request successfully!")
        elif not res[1]:print("Not a JSON")
        else:print("Error with request (JSON, but error)")
    else:
        if message.channel.id == SAYHI:
            # first task is to send a message in sayhi channel
            member = message.author
            print("Promoting user to : normal : ",message.author.id)
            role_normal = message.guild.get_role(ROLE_NORMAL)
            if not member.get_role(ROLE_NORMAL):
                if member.get_role(ROLE_NEW):await member.remove_roles(member.get_role(ROLE_NEW))
                await member.add_roles(role_normal)
                await message.reply("Welcome to server man!!!\nCongragulations! You are now promoted to normal user")
                embed = get_embed_message(member=member,title=f"Congragulations!! \n You are now promoted!\nYou can Access more channels")
                await member.send(embed=embed)
        elif message.channel.id == GENERAL_CHAT:
            # here we moderate the chat conetnts
            member = message.author
            if message.content.lower() == "worst server":
                await message.reply("Dont ever say that :(, \nThat hurted me a lot\n** !! You are banned !! **")
                embed = get_embed_message(member=member,title=f"Congragulation buddy :(\nYou are banned from AVC Tech for a reason, say your justifications on #banned-user channel")
                await member.send(embed=embed)
                for role in member.roles:
                    if role.id in VALID_ROLES:
                        await member.remove_roles(role)
                await member.add_roles(member.guild.get_role(ROLE_BANNED))
        # nothing more here

"""On ready"""
@client.event
async def on_ready():
    try:
        sync = await client.tree.sync() # sync the commands
    except:print("Error syncing commands ")
    for guild in client.guilds:
        if guild.name == GUILD:
            my_guild = guild
            print("Started on guild : "+my_guild.name)
            print("Channels : ")
            for channel in my_guild.channels:
                print(channel, channel.id)
    print(f'{client.user} has connected to Discord!')
"""On member join"""
@client.event
async def on_member_join(member):
    role_new = member.guild.get_role(ROLE_NEW)
    await member.add_roles(role_new)
    if not create_user_db(str(member.id),member.name,member.roles):
        await member.send("Hi,"+str(member.name)+"\nWe experienced an error while updating our database on your request.\nRun /sync-profile on server to sync. \n if you dont face any issue just sit back and relax")
    embed=get_embed_message(member=member,title=f"Welcome To Aswanth's Server. @"+member.name+"\nMay you get great experience in this server")
    channel = client.get_channel(1162450448750477423)
    await channel.send("Checkout #new-commers-overview for more details on what to do\n",embed=embed)
    await member.send(embed=embed)

"""Sync Role Command"""
@client.tree.command(name="sync-role",description="Sync your role with database or back")
async def sync(ctx:discord.ext.commands.Context,from_:typing.Literal['database','discord'],to_:typing.Literal['database','discord']):
    response = ctx.response
    member:discord.Member = ctx.user
    if member.get_role(ROLE_ADMIN): # the requester want to be an admin
        await response.send_message("Your request is initiated. Please wait until completion")
        if from_ == "discord" and to_ == "database":
            print("Request to sync with database")
            members = member.guild.members
            for memb in members: # get all member profiles
                query = "SELECT id from DiscordProfile where discord_id=%s"
                cursor.execute(query,(str(memb.id),))
                data = cursor.fetchall()
                if len(data) < 1:
                    if not create_user_db(str(memb.id),memb.name,memb.roles):
                        await member.send(embed=get_embed_message(member=member,title=f"Result of /sync-profile `{from_}` to `{to_}` \nResult : There was an error syncing with database"))
                        return
                else:
                    if not update_user_role_db(str(memb.id),memb.roles):
                        await member.send(embed=get_embed_message(member=member,title=f"Result of /sync-profile `{from_}` to `{to_}` \nResult : There was an error syncing with database"))
                        return
            await member.send(embed=get_embed_message(member=member,title=f"Result of /sync-profile `{from_}` to `{to_}` \nResult : Successfully synced discord role with database"))
        elif from_ == "database" and to_ == "discord":
            print("Request to sync with discord")
            members = get_all_members() # from database
            if members:
                for mem_id, mem_roles in members.items():
                    memb = await member.guild.fetch_member(int(mem_id))
                    for role in memb.roles[1:]:
                        if role.id in VALID_ROLES:
                            await memb.remove_roles(role)
                    for role in mem_roles[1:]:
                        if role in VALID_ROLES:
                            await memb.add_roles(memb.guild.get_role(role))
                await member.send(embed=get_embed_message(member=member,title=f"Result of /sync-profile `{from_}` to `{to_}` \nResult : Successfully synced discord from database"))
            else:
                await member.send(embed=get_embed_message(member=member,title=f"Result of /sync-profile `{from_}` to `{to_}` \nResult : There was an error syncing with discord"))
        else:
            await response.send_message("invalid option to sync from :",from_,"to",to_)
    else:
        print("Requested by a non admin user")
        await response.send_message("You are not allowed to perform this operation!")


client.run(TOKEN) # run the server