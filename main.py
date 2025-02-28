import discord
import re
import os
import asyncio
import random
import json
from discord.ext import commands, tasks
from collections import defaultdict
from typing import Optional
import datetime

# Get token from environment variables
TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# Ensure token is provided
if not TOKEN:
    raise ValueError("Bot token is missing! Set it in Replit's Secrets.")

# Enable required intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Load data from JSON file
DATA_FILE = "data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


data = load_data()

#embeded message
def create_embed(title, description="", color=0x00ff00):
    embed = discord.Embed(title=title,
                          description=description,
                          color=color,
                          timestamp=datetime.datetime.utcnow())
    return embed


# Leaderboard dictionary to track solved problems
leaderboard = defaultdict(int)
# Last activity dictionary to track user activity time
last_activity = {}


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f'Logged in as {bot.user}')
    auto_roast.start()

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        user_id = str(message.author.id)

        # Ensure user is in data.json
        if user_id not in data:
            data[user_id] = {"problems_solved": 0, "last_active": "Never"}

        # Check if message contains a code block
        if re.search(r"```(.|\n)*```", message.content):
            data[user_id]["problems_solved"] += 1
            data[user_id]["last_active"] = str(message.created_at)
            save_data(data)  # Save updated data to file

            if message.author.id == OWNER_ID:
                await message.reply("Chai peene aa jaiye bhot coding ho gyi ☕")
            else:
                await message.reply("Badiya hai Devar ji! 👌")

        await bot.process_commands(message)


@tasks.loop(hours=24)
async def auto_roast():
    """Checks inactive users and roasts them."""
    current_time = asyncio.get_event_loop().time()
    for guild in bot.guilds:
        for member in guild.members:
            if member.bot:
                continue
            last_time = last_activity.get(member.id, 0)
            if current_time - last_time > 86400:  # 24 hours
                channel = guild.system_channel or next(
                    (ch for ch in guild.text_channels
                     if ch.permissions_for(guild.me).send_messages), None)
                if channel:
                    await channel.send(
                        f"{member.mention} Arre bhai, coding bhool gaye kya? Ya sirf Discord me timepass chal raha hai? 😏🔥"
                    )


@bot.tree.command(name="send", description="Send a message to a channel")
@commands.has_permissions(administrator=True)  # Only admins can use this
async def send(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)


@bot.tree.command(name="help",
                  description="Shows the list of available commands")
async def help_command(interaction: discord.Interaction):
    help_text = (
        "**🛠 Available Commands:**\n"
        "📊 **/leaderboard** - View the top coders in the community.\n"
        "📈 **/stats** - Check your coding progress and activity.\n"
        "🔥 **/motivate [@user]** - Send a motivation boost to someone.\n"
        "🛠 **/help** - Get the list of available commands.\n"
        "📨 **/send [message]** - Send a message to a channel (Admin only).\n"
        "\n🚀 *More features coming soon... Stay tuned!*")
    await interaction.response.send_message(help_text)


@bot.tree.command(name="motivate",
                  description="Motivate a specific person by mentioning them")
async def motivate(interaction: discord.Interaction, member: discord.Member):
    messages = [
        f"{member.mention}, keep pushing forward, success is just around the corner! 🚀",
        f"{member.mention}, you're capable of amazing things. Keep going! 💪",
        f"{member.mention}, every great achievement starts with a single step. Take yours today! 🏆",
        f"{member.mention}, believe in yourself! You have everything it takes to succeed. ✨",
        f"{member.mention}, hard work beats talent when talent doesn't work hard! 🔥"
    ]
    await interaction.response.send_message(random.choice(messages))








@bot.tree.command(name="leaderboard",
                  description="Shows the coding leaderboard")
async def leaderboard(interaction: discord.Interaction):
    async with interaction.channel.typing():
        sorted_users = sorted(data.items(),
                              key=lambda x: x[1].get("problems_solved", 0),
                              reverse=True)[:10]

        embed = create_embed("🏆 Coding Leaderboard 🏆",
                             "Top problem solvers in the community:",
                             0xffd700)

        for rank, (user_id, stats) in enumerate(sorted_users, 1):
            user = await bot.fetch_user(int(user_id))
            embed.add_field(
                name=f"{rank}. {user.display_name}",
                value=
                f"**Solved:** {stats['problems_solved']} | **Last Active:** {stats['last_active'][:10]}",
                inline=False)

        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="stats",
                  description="Shows your coding progress and activity stats")
async def stats(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    # Ensure user data exists
    if user_id not in data:
        data[user_id] = {
            "problems_solved": 0,
            "rank": 0,
            "last_active": "Never"
        }

    # Ensure "rank" key exists
    if "rank" not in data[user_id]:
        data[user_id]["rank"] = 0

    stats_message = (
        f"**📊 Your Coding Stats:**\n"
        f"👤 **User:** {interaction.user.display_name}\n"
        f"✅ **Problems Solved:** {data[user_id]['problems_solved']}\n"
        f"🏆 **Leaderboard Rank:** {data[user_id]['rank']}\n"
        f"🕒 **Last Active:** {data[user_id]['last_active']}\n")

    await interaction.response.send_message(stats_message)


# Run the bot
bot.run(TOKEN)
