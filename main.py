import discord
import os
from discord.ext import commands
from discord import app_commands
from user_commands import setup as setup_user_commands
from admin_commands import setup as setup_admin_commands
# Configuration
TOKEN = os.getenv("TOKEN")

# Intents setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!",
                   intents=intents,
                   member_cache_flags=discord.MemberCacheFlags.all())

# Load commands
setup_user_commands(bot)
setup_admin_commands(bot)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    for guild in bot.guilds:
        await guild.chunk()


# Run the bot
bot.run(TOKEN)
