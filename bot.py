import discord
from decouple import config
from discord.ext import commands

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


@bot.tree.command(name='ping')
async def run_command_1(ctx: discord.Interaction):
    await ctx.response.send_message("PONG PONG !", ephemeral=True)


@bot.event
async def on_ready():
    if not hasattr(bot, 'uptime'):
        uptime = discord.utils.utcnow()
    print('Ready: %s (ID: %s)', bot.user, bot.user.id)
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")


bot.run(BOT_TOKEN)
