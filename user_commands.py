import discord
from discord.ext import commands
from typing import Optional
import json
import datetime
import random

# Load data
DATA_FILE = "data.json"


def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


data = load_data()


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def create_embed(title, description="", color=0x00ff00):
    embed = discord.Embed(title=title,
                          description=description,
                          color=color,
                          timestamp=datetime.datetime.utcnow())
    return embed


def setup(bot):

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
                      description="Check coding stats for yourself or others")
    async def stats(interaction: discord.Interaction,
                    member: Optional[discord.Member] = None):
        async with interaction.channel.typing():
            target = member or interaction.user
            user_id = str(target.id)

            if user_id not in data:
                data[user_id] = {"problems_solved": 0, "last_active": "Never"}

            last_active = datetime.datetime.fromisoformat(data[user_id]["last_active"]) \
                if data[user_id]["last_active"] != "Never" else "Never"

            embed = create_embed(f"📊 {target.display_name}'s Coding Stats",
                                 color=0x7289da)
            embed.set_thumbnail(url=target.avatar.url)
            embed.add_field(name="Problems Solved",
                            value=f"```{data[user_id]['problems_solved']}```",
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

    @bot.tree.command(
        name="motivate",
        description="Bhaiyon ko coding ke liye protsaahit karein")
    async def motivate(interaction: discord.Interaction,
                       member: discord.Member):
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
                    "color":
                    0xFF4500,  # OrangeRed
                    "title":
                    "Bhabhi ki Taakat 💻",
                    "gif":
                    "https://media.giphy.com/media/LmNwrBhejkK9EFP504/giphy.gif"  # Fiery typing
                },
                {
                    "message":
                    f"{member.mention} ka to X-FACTOR dikh gaya! 🧠\nAb ghar ka genius kaun kehta hai?",
                    "color":
                    0x00FF00,  # Lime
                    "title":
                    "Family Genius 🤓",
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
                    "color":
                    0x6F4E37,  # Coffee brown
                    "title":
                    "Bhabhi ka Special ☕",
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
            embed.set_thumbnail(url=member.avatar.url)

            # Set the GIF for the embed
            embed.set_image(url=motivation["gif"])

            # Set footer with family message
            embed.set_footer(
                text="Parivaar hamesha aapke saath ❤️",
                icon_url=interaction.user.avatar.
                url  # Use the command user's avatar as footer icon
            )

            await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="admin_command",
                      description="An example admin command")
    @commands.has_permissions(administrator=True)
    async def admin_command(interaction: discord.Interaction):
        await interaction.response.send_message("This is an admin command!")

    @bot.tree.command(
        name="help", description="List all available commands and their usage")
    async def help(interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 Command Help",
            description="Here are all the commands you can use:",
            color=0x7289da)

        # Add fields for each command
        embed.add_field(
            name="🏆 /leaderboard",
            value="Shows the coding leaderboard with the top problem solvers.",
            inline=False)
        embed.add_field(
            name="📊 /stats [member]",
            value="Check coding stats for yourself or another member.",
            inline=False)
        embed.add_field(name="💪 /motivate @member",
                        value="Motivate a member to keep coding!",
                        inline=False)
        embed.add_field(
            name="📨 /send #channel message",
            value="(Admin only) Send a message to a specific channel.",
            inline=False)
        embed.add_field(name="🛠️ /admin_command",
                        value="(Admin only) An example admin command.",
                        inline=False)
        embed.add_field(name="❓ /help",
                        value="Show this help message.",
                        inline=False)

        # Set footer
        embed.set_footer(
            text="Use / before each command to interact with the bot!")

        await interaction.response.send_message(embed=embed)

