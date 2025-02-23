import discord
import re
import os
from discord.ext import commands

# Get token from environment variables
TOKEN = os.getenv("TOKEN")

# Ensure token is provided
if not TOKEN:
    raise ValueError("Bot token is missing! Set it in Replit's Secrets.")

# Enable required intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Ensure message content access is enabled

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    print(f"Received message: {message.content}")  # Debugging line

    if message.author == bot.user:
        return

    # Check if the message contains a code block
    if re.search(r"```(.|\n)*```", message.content):
        if message.author.id == int(os.getenv("OWNER_ID")):  # Set OWNER_ID in Replit Secrets
            await message.reply("Chai peene aa jaiye bhot coding ho gyi ☕")
        else:
            await message.reply("Badiya hai Devar ji! 👌")

    await bot.process_commands(message)

# Run the bot
bot.run(TOKEN)
