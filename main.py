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
intents.members = True  # Enable server members intent

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
    if not auto_roast.is_running():  # Check if task isn't already running
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
        data[user_id]["last_active"] = datetime.datetime.utcnow().isoformat()
        save_data(data)  # Save updated data to file

        if message.author.id == OWNER_ID:
            await message.reply("Chai peene aa jaiye bhot coding ho gyi ☕")
        else:
            await message.reply("Badiya hai Devar ji! 👌")

    await bot.process_commands(message)


@tasks.loop(hours=24)
async def auto_roast():
    current_time = datetime.datetime.utcnow()

    for guild in bot.guilds:
        for member in guild.members:
            if member.bot:
                continue

            user_id = str(member.id)
            user_data = data.get(user_id, {})
            last_active_str = user_data.get("last_active", "Never")

            if last_active_str == "Never":
                last_active = None
            else:
                last_active = datetime.datetime.fromisoformat(
                    last_active_str.split("+")[0])

            if last_active and (current_time -
                                last_active).total_seconds() > 86400:
                channel = guild.system_channel or next(
                    (ch for ch in guild.text_channels
                     if ch.permissions_for(guild.me).send_messages), None)
                if channel:
                    try:
                        await channel.send(
                            f"{member.mention} Arre bhai, coding bhool gaye kya? Ya sirf Discord me timepass chal raha hai? 😏🔥"
                        )
                    except discord.Forbidden:
                        print(
                            f"Missing permissions to send message in {channel.name}"
                        )
                    except Exception as e:
                        print(f"Error sending roast: {e}")


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
                  description="Bhaiyon ko coding ke liye protsaahit karein")
async def motivate(interaction: discord.Interaction, member: discord.Member):
    async with interaction.channel.typing():
        motivations = [
            {
                "message":
                f"{member.mention} beta, tumse na ho payega? Kabhi nahi! 💪\nAage badho, hum tumpe vishwas rakhte hain!",
                "color":
                0xFFD700,  # Gold
                "title":
                "Maa ka Ashirwaad 👐",
                "gif":
                "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmR1amdjaG12NGhrdnJkaGNmcmYyd2lvOWhmazl0aGVyOHVzeXF6dCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/o75ajIFH0QnQC3nCeD/giphy.gif"  # Mother blessing
            },
            {
                "message":
                f"{member.mention} bhai, keyboard toh jal raha hai tumhare haathon se! 🔥\nChhote bhaiyon ko seekhane ka time aa gaya!",
                "color": 0xFF4500,  # OrangeRed
                "title": "Bhabhi ki Taakat 💻",
                "gif":
                "https://media.giphy.com/media/LmNwrBhejkK9EFP504/giphy.gif"  # Fiery typing
            },
            {
                "message":
                f"{member.mention} ka to X-FACTOR dikh gaya! 🧠\nAb ghar ka genius kaun kehta hai?",
                "color": 0x00FF00,  # Lime
                "title": "Family Genius 🤓",
                "gif":
                "https://media.giphy.com/media/26tn33aiTi1jkl6H6/giphy.gif"  # Brain sparkles
            },
            {
                "message":
                f"{member.mention} ne bugs ko mara jhatka! 🐛⚡\nAb ye kehne ka time hai - 'Maa kasam code perfect hai!'",
                "color":
                0x8A2BE2,  # BlueViolet
                "title":
                "Debugging Champion 🏆",
                "gif":
                "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3Frem0waGw3eW1zamF6MjJweWJpeXNzZTAwY3Q0cTZxdHplYmNkYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/oYQRuoYd6btVNAh75z/giphy.gif"  # Bug squashing
            },
            {
                "message":
                f"{member.mention} coffee piyo, code likho ☕\nRaat bhar jag kar bhi chehre pe chamak!",
                "color": 0x6F4E37,  # Coffee brown
                "title": "Bhabhi ka Special ☕",
                "gif":
                "https://media.giphy.com/media/3o7TKUM3IgJBX2as9O/giphy.gif"  # Coffee coding
            }
        ]

        # Select random motivation
        motivation = random.choice(motivations)

        # Create personalized embed
        embed = discord.Embed(title=motivation["title"],
                              description=motivation["message"],
                              color=motivation["color"],
                              timestamp=datetime.datetime.utcnow())

        # Set thumbnail to the mentioned user's profile photo
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.
                            default_avatar.url)

        # Set the GIF for the embed
        embed.set_image(url=motivation["gif"])

        # Set footer with family message
        embed.set_footer(
            text="Parivaar hamesha aapke saath ❤️",
            icon_url=interaction.user.avatar.url if interaction.user.avatar
            else interaction.user.default_avatar.url)

        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="leaderboard",
                  description="Shows the coding leaderboard")
async def leaderboard(interaction: discord.Interaction):
    async with interaction.channel.typing():
        sorted_users = sorted(data.items(),
                              key=lambda x: x[1].get("problems_solved", 0),
                              reverse=True)[:10]

        embed = create_embed("🏆 Coding Leaderboard 🏆",
                             "Top problem solvers in the community:", 0xffd700)

        for rank, (user_id, stats) in enumerate(sorted_users, 1):
            user = await bot.fetch_user(int(user_id))
            embed.add_field(
                name=f"{rank}. {user.display_name}",
                value=
                f"**Solved:** {stats['problems_solved']} | **Last Active:** {stats['last_active'][:10]}",
                inline=False)

        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="stats",
                  description="Check coding stats for yourself or others")
async def stats(interaction: discord.Interaction,
                member: Optional[discord.Member] = None):
    async with interaction.channel.typing():
        target = member or interaction.user
        user_id = str(target.id)

        if user_id not in data:
            data[user_id] = {"problems_solved": 0, "last_active": "Never"}

        # Ensure "rank" key exists
        if "rank" not in data[user_id]:
            data[user_id]["rank"] = 0

        last_active = datetime.datetime.fromisoformat(data[user_id]["last_active"]) \
            if data[user_id]["last_active"] != "Never" else "Never"

        embed = create_embed(f"📊 {target.display_name}'s Coding Stats",
                             color=0x7289da)
        embed.set_thumbnail(url=target.avatar.url if target.avatar else target.
                            default_avatar.url)
        embed.add_field(name="Problems Solved",
                        value=f"```{data[user_id]['problems_solved']}```",
                        inline=True)
        embed.add_field(name="Leaderboard Rank",
                        value=f"```{data[user_id]['rank']}```",
                        inline=True)
        embed.add_field(
            name="Last Active",
            value=
            f"```{last_active if isinstance(last_active, str) else last_active.strftime('%Y-%m-%d %H:%M')}```",
            inline=True)
        embed.add_field(
            name="Activity Level",
            value=
            f"```{'🔥 Active' if data[user_id]['last_active'] != 'Never' else '❄️ Inactive'}```",
            inline=True)

        await interaction.response.send_message(embed=embed)


# Run the bot
bot.run(TOKEN)
