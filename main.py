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

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

if not TOKEN:
    raise ValueError("Bot token is missing! Set it in Replit's Secrets.")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

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


def create_embed(title, description="", color=0x00ff00):
    embed = discord.Embed(title=title,
                          description=description,
                          color=color,
                          timestamp=datetime.datetime.utcnow())
    return embed


leaderboard = defaultdict(int)

last_activity = {}


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f'Logged in as {bot.user}')
    if not auto_roast.is_running():
        auto_roast.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = str(message.author.id)

    if user_id not in data:
        data[user_id] = {"problems_solved": 0, "last_active": "Never"}

    if re.search(r"```(.|\n)*```", message.content):
        data[user_id]["problems_solved"] += 1
        data[user_id]["last_active"] = datetime.datetime.utcnow().isoformat()
        save_data(data)

        if message.author.id == OWNER_ID:
            await message.reply("Great job, darling! 💖")
        else:
            await message.reply("Great job! 😊")

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

            if last_active and (current_time - last_active).total_seconds() > 86400:
                channel = guild.system_channel or next(
                    (ch for ch in guild.text_channels
                     if ch.permissions_for(guild.me).send_messages), None)
                if channel:
                    try:
                        if member.id == OWNER_ID:
                            await channel.send(
                                f"{member.mention} Darling, missing your code! 💖"
                            )
                        else:
                            await channel.send(
                                f"{member.mention} Bhabhi noticed you haven't coded in a while! Don't forget to keep learning and have fun. She's cheering for you! 😊"
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
                  description="Send a friendly motivation boost to someone")
async def motivate(interaction: discord.Interaction, member: discord.Member):
    async with interaction.channel.typing():
        motivations = [
            {
                "message":
                f"{member.mention}, remember, every coder starts somewhere! 💪\nKeep going, your efforts matter!",
                "color":
                0xFFD700,  # Gold
                "title":
                "A Little Push from Bhabhi 👐",
                "gif":
                "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmR1amdjaG12NGhrdnJkaGNmcmYyd2lvOWhmazl0aGVyOHVzeXF6dCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/o75ajIFH0QnQC3nCeD/giphy.gif"
            },
            {
                "message":
                f"{member.mention}, your keyboard skills are on fire! 🔥\nBhabhi says: Share your wisdom with the group!",
                "color": 0xFF4500,  # OrangeRed
                "title": "Bhabhi's Coding Cheers 💻",
                "gif":
                "https://media.giphy.com/media/LmNwrBhejkK9EFP504/giphy.gif"
            },
            {
                "message":
                f"{member.mention}, your coding spark is shining bright! 🧠\nBhabhi is proud of your progress!",
                "color": 0x00FF00,  # Lime
                "title": "Bhabhi's Genius Badge 🤓",
                "gif":
                "https://media.giphy.com/media/26tn33aiTi1jkl6H6/giphy.gif"
            },
            {
                "message":
                f"{member.mention}, you just squashed those bugs! 🐛⚡\nBhabhi says: 'Great job, keep it up!'",
                "color":
                0x8A2BE2,  # BlueViolet
                "title":
                "Bhabhi's Debugging Star 🏆",
                "gif":
                "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3Frem0waGw3eW1zamF6MjJweWJpeXNzZTAwY3Q0cTZxdHplYmNkYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/oYQRuoYd6btVNAh75z/giphy.gif"
            },
            {
                "message":
                f"{member.mention}, grab a coffee and code on! ☕\nBhabhi reminds you: Stay refreshed and keep learning!",
                "color": 0x6F4E37,  # Coffee brown
                "title": "Bhabhi's Coffee Break ☕",
                "gif":
                "https://media.giphy.com/media/3o7TKUM3IgJBX2as9O/giphy.gif"
            }
        ]

        motivation = random.choice(motivations)

        embed = discord.Embed(title=motivation["title"],
                              description=motivation["message"],
                              color=motivation["color"],
                              timestamp=datetime.datetime.utcnow())

        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.
                            default_avatar.url)

        embed.set_image(url=motivation["gif"])

        embed.set_footer(
            text="Bhabhi is always cheering for you! ❤️",
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

        # Dynamically calculate the user's rank
        sorted_users = sorted(data.items(),
                              key=lambda x: x[1].get("problems_solved", 0),
                              reverse=True)
        user_ids = [uid for uid, _ in sorted_users]
        try:
            rank = user_ids.index(user_id) + 1
        except ValueError:
            rank = len(user_ids) + 1  # Handle if user not found

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
                        value=f"```{rank}```",
                        inline=True)
        embed.add_field(
            name="Last Active",
            value=
            f"```{last_active if isinstance(last_active, str) else last_active.strftime('%Y-%m-%d %H:%M')}```",
            inline=True)
        embed.add_field(
            name="Activity Level",
            value=
            f"```{'🔥 Active' if data[user_id]['last_active'] != 'Never' and not isinstance(last_active, str) else '❄️ Inactive'}```",
            inline=True)

        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="modify_solves",
                  description="[ADMIN] Adjust a user's solved problems count")
@commands.has_permissions(administrator=True)
async def modify_solves(interaction: discord.Interaction,
                        member: discord.Member, amount: int):
    """Admin command to modify problem solve count for a user"""
    if amount == 0:
        await interaction.response.send_message("Amount cannot be zero!",
                                                ephemeral=True)
        return

    user_id = str(member.id)

    # Initialize user if not in data
    if user_id not in data:
        data[user_id] = {"problems_solved": 0, "last_active": "Never"}

    original_count = data[user_id]["problems_solved"]
    data[user_id]["problems_solved"] = max(
        0, data[user_id]["problems_solved"] + amount)
    save_data(data)

    embed = create_embed("🔧 Admin Action - Solve Count Modified",
                         f"Updated {member.mention}'s problem solves:",
                         0x7289da)
    embed.add_field(name="Previous Count",
                    value=str(original_count),
                    inline=True)
    embed.add_field(name="Adjustment",
                    value=f"{'+' if amount > 0 else ''}{amount}",
                    inline=True)
    embed.add_field(name="New Count",
                    value=str(data[user_id]["problems_solved"]),
                    inline=True)
    embed.set_footer(
        text=f"Action performed by {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed, ephemeral=True)


@modify_solves.error
async def modify_solves_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command!", ephemeral=True)
    else:
        await interaction.response.send_message(
            f"An error occurred: {str(error)}", ephemeral=True)


# Run the bot
bot.run(TOKEN)
