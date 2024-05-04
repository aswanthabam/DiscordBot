import discord
from decouple import config
from discord.ext import commands
import pymysql

BOT_TOKEN = config('BOT_TOKEN')

intents = discord.Intents(
    guilds=True,
    members=True,
    bans=True,
    emojis=True,
    voice_states=True,
    messages=True,
    reactions=True,
    message_content=True,
)

bot = commands.Bot(command_prefix='/', intents=intents)
connection = pymysql.connect(
    host=config("DB_HOST"),
    user=config("DB_USER"),
    password=config("DB_PASS"),
    database=config("DB_NAME")
)


@bot.listen()
async def on_message(ctx: discord.Message):
    if ctx.author == bot.user:
        return
    content = ctx.content
    user_id = ctx.author.id
    print(user_id)
    cursor = connection.cursor()
    for word in content.split():
        cursor.execute("INSERT INTO user_words(discord_id, word) VALUES (%s, %s)",
                       (str(user_id), word))
    connection.commit()


@bot.tree.command(name='ping')
async def run_command_1(ctx: discord.Interaction):
    await ctx.response.send_message("PONG PONG !", ephemeral=True)


select = discord.ui.Select(
    options=[
        discord.SelectOption(value='Explorer', label='Explorer'),
        discord.SelectOption(value='Professional', label='Professional'),
        discord.SelectOption(value='Official', label='Official'),
        discord.SelectOption(value='Other', label='Other'),
    ]
)


@bot.tree.command(name='select-role')
async def select_role(ctx: discord.Interaction):
    view = discord.ui.View(
        timeout=None
    )
    select.callback = select_role_callback
    view.add_item(select)
    await ctx.response.send_message(content='Please select a role.', view=view, ephemeral=True)


async def select_role_callback(interaction: discord.Interaction):
    selected = select.values
    roles: list[discord.Role] = [discord.utils.get(interaction.guild.roles, name=role)
                                 for role in selected if
                                 discord.utils.get(interaction.guild.roles, name=role) is not None or (
                                         discord.utils.get(interaction.guild.roles,
                                                           name=role) is None and await interaction.guild.create_role(
                                     name=role))]
    await interaction.user.add_roles(*roles)
    await interaction.response.send_message("Updated Role")


@bot.tree.command(name="word-status")
async def word_status(interaction: discord.Interaction):
    query = """
    SELECT word, COUNT(discord_id) count FROM user_words GROUP BY word  ORDER BY count DESC LIMIT 10
    """
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    message = "# Status\n" + '\n'.join([f"{row[0]}: {row[1]}" for row in data])
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="user-status")
async def user_status(interaction: discord.Interaction, user: discord.Member):
    query = """
    SELECT word, COUNT(*) count FROM user_words WHERE discord_id = %s GROUP BY word ORDER BY count DESC LIMIT 10
    """
    cursor = connection.cursor()
    cursor.execute(query, (user.id,))
    data = cursor.fetchall()
    print(data)
    print(user.id)
    message = "# Status\n" + '\n'.join([f"{row[0]}: {row[1]}" for row in data])
    await interaction.response.send_message(message, ephemeral=True)


@bot.event
async def on_ready():
    if not hasattr(bot, 'uptime'):
        uptime = discord.utils.utcnow()
    print('Ready: %s (ID: %s)', bot.user, bot.user.id)
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")


bot.run(BOT_TOKEN)
