import discord
from discord.ext import commands
from keep_alive import keep_alive  # This keeps Replit running
import os

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "hello" in message.content.lower():
        await message.channel.send(f"Hello, {message.author.name}! ❤️ - Bhabhi"
                                   )


keep_alive()  # Keeps bot alive
bot.run(os.getenv("TOKEN"))  # Fetch token from environment variable
