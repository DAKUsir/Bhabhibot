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

def create_embed(title, description="", color=0x7289da, thumbnail=None, footer_text=None):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if footer_text:
        embed.set_footer(text=footer_text)
    return embed

def get_streak(activity):
    if not activity:
        return 0
    today = datetime.datetime.utcnow().date()
    active_dates = set(datetime.date.fromisoformat(date) for date in activity)
    if not active_dates:
        return 0
    most_recent = max(active_dates)
    streak = 0
    current_date = most_recent
    while current_date in active_dates and current_date <= today:
        streak += 1
        current_date -= datetime.timedelta(days=1)
    return streak

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f'Logged in as {bot.user}')
    if not auto_reminder.is_running():
        auto_reminder.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = str(message.author.id)

    if user_id not in data:
        data[user_id] = {"problems_solved": 0, "last_active": "Never", "activity": {}, "goal": 0}

    if re.search(r"```(.|\n)*```", message.content):
        current_date = datetime.datetime.utcnow().date().isoformat()
        if "activity" not in data[user_id]:
            data[user_id]["activity"] = {}
        if current_date not in data[user_id]["activity"]:
            data[user_id]["activity"][current_date] = 0
        data[user_id]["activity"][current_date] += 1
        data[user_id]["problems_solved"] += 1
        data[user_id]["last_active"] = datetime.datetime.utcnow().isoformat()
        save_data(data)
        await message.reply("Excellent work! Your coding progress has been recorded.")

    await bot.process_commands(message)

@tasks.loop(hours=24)
async def auto_reminder():
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
                last_active = datetime.datetime.fromisoformat(last_active_str.split("+")[0])
            if last_active and (current_time - last_active).total_seconds() > 86400:
                channel = guild.system_channel or next(
                    (ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
                if channel:
                    try:
                        await channel.send(f"{member.mention}, we noticed you haven't shared code recently. Keep up your learning journey!")
                    except discord.Forbidden:
                        print(f"Missing permissions to send message in {channel.name}")
                    except Exception as e:
                        print(f"Error sending reminder: {e}")

@bot.tree.command(name="send", description="Send a message to a channel (Admin only)")
@commands.has_permissions(administrator=True)
async def send(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@bot.tree.command(name="help", description="Displays the list of available commands")
async def help_command(interaction: discord.Interaction):
    embed = create_embed("Available Commands", "Here are the commands you can use to enhance your coding journey:", thumbnail=bot.user.avatar.url, footer_text="Explore and enhance your coding skills!")
    commands_list = [
        ("/leaderboard", "View the top coders in the community based on problems solved."),
        ("/stats", "Check your own or another user's coding progress and activity."),
        ("/motivate [@user]", "Send a motivational message to a specified user."),
        ("/streak", "Display your current coding streak (consecutive days active)."),
        ("/top_streaks", "Show the top 10 users with the longest coding streaks."),
        ("/set_goal [number]", "Set or unset a personal goal for problems to solve."),
        ("/progress", "View your progress towards your goal and recent activity."),
        ("/daily_puzzle", "Participate in a daily coding-related puzzle to boost your skills."),
        ("/send [message]", "Send a message to a channel (Admin only)."),
        ("/modify_solves [@user] [amount]", "Adjust a user's problem solve count (Admin only)."),
        ("/user_report [@user]", "Generate a detailed activity report for a user (Admin only)."),
    ]
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="motivate", description="Send a friendly motivation boost to someone")
async def motivate(interaction: discord.Interaction, member: discord.Member):
    async with interaction.channel.typing():
        motivations = [
            {
                "message": f"{member.mention}, every programmer starts with fundamental concepts. Your commitment to learning and persistent efforts are highly commendable. Continue to strive for excellence.",
                "color": 0xFFD700,  # Gold
                "title": "Motivational Boost",
                "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmR1amdjaG12NGhrdnJkaGNmcmYyd2lvOWhmazl0aGVyOHVzeXF6dCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/o75ajIFH0QnQC3nCeD/giphy.gif"
            },
            {
                "message": f"{member.mention}, your proficiency in coding is notable. We encourage you to contribute your expertise to the community.",
                "color": 0xFF4500,  # OrangeRed
                "title": "Coding Encouragement",
                "gif": "https://media.giphy.com/media/LmNwrBhejkK9EFP504/giphy.gif"
            },
            {
                "message": f"{member.mention}, your passion for coding is apparent, and your advancements are significant. Maintain your exemplary performance.",
                "color": 0x00FF00,  # Lime
                "title": "Progress Acknowledgment",
                "gif": "https://media.giphy.com/media/26tn33aiTi1jkl6H6/giphy.gif"
            },
            {
                "message": f"{member.mention}, effectively addressing those technical challenges is a remarkable accomplishment. Excellent work, and persist in your endeavors.",
                "color": 0x8A2BE2,  # BlueViolet
                "title": "Achievement Recognition",
                "gif": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3Frem0waGw3eW1zamF6MjJweWJpeXNzZTAwY3Q0cTZxdHplYmNkYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/oYQRuoYd6btVNAh75z/giphy.gif"
            },
            {
                "message": f"{member.mention}, take a brief respite with a coffee, then resume your coding pursuits. It is important to remain refreshed and dedicated to continuous learning.",
                "color": 0x6F4E37,  # Coffee brown
                "title": "Learning Reminder",
                "gif": "https://media.giphy.com/media/3o7TKUM3IgJBX2as9O/giphy.gif"
            }
        ]

        motivation = random.choice(motivations)

        embed = discord.Embed(title=motivation["title"],
                              description=motivation["message"],
                              color=motivation["color"],
                              timestamp=datetime.datetime.utcnow())

        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        embed.set_image(url=motivation["gif"])

        embed.set_footer(
            text="Keep striving for excellence in your coding journey.",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        )

        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="leaderboard", description="Displays the coding leaderboard")
async def leaderboard(interaction: discord.Interaction):
    async with interaction.channel.typing():
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("problems_solved", 0), reverse=True)[:10]
        embed = create_embed("🏆 Top Coders Leaderboard", "The best problem solvers:", color=0xFFD700, thumbnail="https://cdn-icons-png.flaticon.com/512/888/888859.png", footer_text="Climb the ranks by solving more problems!")
        for rank, (user_id, stats) in enumerate(sorted_users, 1):
            user = await bot.fetch_user(int(user_id))
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
            embed.add_field(name=f"{medal} {rank}. {user.display_name}", value=f"**Solved:** {stats['problems_solved']} | **Last Active:** {stats['last_active'][:10]}", inline=False)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="View coding statistics for yourself or another user")
async def stats(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    async with interaction.channel.typing():
        target = member or interaction.user
        user_id = str(target.id)
        if user_id not in data:
            data[user_id] = {"problems_solved": 0, "last_active": "Never", "activity": {}, "goal": 0}
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("problems_solved", 0), reverse=True)
        user_ids = [uid for uid, _ in sorted_users]
        rank = user_ids.index(user_id) + 1 if user_id in user_ids else len(user_ids) + 1
        last_active = data[user_id]["last_active"] if data[user_id]["last_active"] != "Never" else "Never"
        if last_active != "Never":
            last_active = datetime.datetime.fromisoformat(last_active).strftime('%Y-%m-%d %H:%M')
        embed = create_embed(f"📊 {target.display_name}'s Coding Stats", thumbnail=target.avatar.url if target.avatar else target.default_avatar.url, footer_text="Keep up the great work!")
        embed.add_field(name="Problems Solved", value=f"```{data[user_id]['problems_solved']}```", inline=True)
        embed.add_field(name="Leaderboard Rank", value=f"```{rank}```", inline=True)
        embed.add_field(name="Last Active", value=f"```{last_active}```", inline=True)
        embed.add_field(name="Activity Level", value=f"```{'🔥 Active' if last_active != 'Never' else '❄️ Inactive'}```", inline=True)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="modify_solves", description="[ADMIN] Adjust a user's solved problems count")
@commands.has_permissions(administrator=True)
async def modify_solves(interaction: discord.Interaction, member: discord.Member, amount: int):
    if amount == 0:
        await interaction.response.send_message("The adjustment amount cannot be zero.", ephemeral=True)
        return
    user_id = str(member.id)
    if user_id not in data:
        data[user_id] = {"problems_solved": 0, "last_active": "Never", "activity": {}, "goal": 0}
    original_count = data[user_id]["problems_solved"]
    data[user_id]["problems_solved"] = max(0, data[user_id]["problems_solved"] + amount)
    save_data(data)
    embed = create_embed("Admin Action: Problem Count Adjustment", f"Updated {member.mention}'s problem solve count:", thumbnail=member.avatar.url if member.avatar else member.default_avatar.url, footer_text=f"Action performed by {interaction.user.display_name}")
    embed.add_field(name="Previous Count", value=f"```{original_count}```", inline=True)
    embed.add_field(name="Adjustment", value=f"```{'+' if amount > 0 else ''}{amount}```", inline=True)
    embed.add_field(name="New Count", value=f"```{data[user_id]['problems_solved']}```", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@modify_solves.error
async def modify_solves_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)

@bot.tree.command(name="streak", description="Shows your current coding streak")
async def streak(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in data:
        data[user_id] = {"problems_solved": 0, "last_active": "Never", "activity": {}, "goal": 0}
    activity = data[user_id].get("activity", {})
    streak_count = get_streak(activity)
    embed = create_embed("Your Coding Streak", thumbnail=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url, footer_text="Keep the streak alive!")
    embed.add_field(name="Current Streak", value=f"```{streak_count} days```", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="top_streaks", description="Shows the top 10 users with the longest coding streaks")
async def top_streaks(interaction: discord.Interaction):
    streaks = []
    for user_id in data:
        activity = data[user_id].get("activity", {})
        streak_count = get_streak(activity)
        if streak_count > 0:
            streaks.append((user_id, streak_count))
    top_streaks = sorted(streaks, key=lambda x: x[1], reverse=True)[:10]
    embed = create_embed("Top Coding Streaks", thumbnail="https://cdn-icons-png.flaticon.com/512/4096/4096148.png", footer_text="Consistency is key!")
    for rank, (user_id, streak_count) in enumerate(top_streaks, 1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(name=f"{rank}. {user.display_name}", value=f"```{streak_count} days```", inline=False)
    if not top_streaks:
        embed.description = "No active streaks yet. Start coding to build your streak!"
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="set_goal", description="Set your personal goal for problems to solve")
async def set_goal(interaction: discord.Interaction, number: int):
    if number < 0:
        await interaction.response.send_message("Goal must be a non-negative integer.", ephemeral=True)
        return
    user_id = str(interaction.user.id)
    if user_id not in data:
        data[user_id] = {"problems_solved": 0, "last_active": "Never", "activity": {}, "goal": 0}
    if number == 0:
        data[user_id]["goal"] = 0
        await interaction.response.send_message("Your goal has been unset.", ephemeral=True)
    else:
        data[user_id]["goal"] = number
        await interaction.response.send_message(f"Your goal has been set to {number} problems.", ephemeral=True)
    save_data(data)

@bot.tree.command(name="progress", description="Shows your progress towards your goal and recent activity")
async def progress(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in data:
        data[user_id] = {"problems_solved": 0, "last_active": "Never", "activity": {}, "goal": 0}
    problems_solved = data[user_id]["problems_solved"]
    goal = data[user_id].get("goal", 0)
    activity = data[user_id].get("activity", {})
    today = datetime.datetime.utcnow().date()
    last_7_days = [(today - datetime.timedelta(days=i)).isoformat() for i in range(7)]
    recent_activity = sum(activity.get(date, 0) for date in last_7_days)
    embed = create_embed("Your Coding Progress", thumbnail=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url, footer_text="Track your progress daily!")
    embed.add_field(name="Total Problems Solved", value=f"```{problems_solved}```", inline=True)
    if goal > 0:
        progress_percentage = (problems_solved / goal) * 100
        embed.add_field(name="Goal Progress", value=f"```{problems_solved} / {goal} ({progress_percentage:.1f}%)```", inline=True)
    else:
        embed.add_field(name="Goal", value="```Not set```", inline=True)
    embed.add_field(name="Last 7 Days", value=f"```{recent_activity}```", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily_puzzle", description="Participate in a daily coding-related puzzle")
async def daily_puzzle(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in data:
        data[user_id] = {"problems_solved": 0, "last_active": "Never", "activity": {}, "goal": 0}

    current_date = datetime.datetime.utcnow().date().isoformat()
    activity = data[user_id].get("activity", {})

    if current_date in activity and activity[current_date] > 0:
        embed = create_embed("Daily Puzzle", "You've already participated in today's puzzle!", thumbnail="https://cdn-icons-png.flaticon.com/512/4096/4096148.png", footer_text="Sharpen your mind daily!")
        embed.add_field(name="Status", value="```🔒 Done```", inline=True)
    else:
        if "activity" not in data[user_id]:
            data[user_id]["activity"] = {}
        if current_date not in data[user_id]["activity"]:
            data[user_id]["activity"][current_date] = 0
        data[user_id]["activity"][current_date] += 1
        data[user_id]["problems_solved"] += 1
        data[user_id]["last_active"] = datetime.datetime.utcnow().isoformat()
        save_data(data)

        puzzles = [
            "What is the time complexity of a binary search algorithm?",
            "Explain the difference between '==' and '===' in JavaScript.",
            "How would you reverse a string in Python without using built-in functions?"
        ]
        puzzle = random.choice(puzzles)

        embed = create_embed("Daily Puzzle", f"**Today's Puzzle:**\n{puzzle}", thumbnail="https://cdn-icons-png.flaticon.com/512/4096/4096148.png", footer_text="Sharpen your mind daily!")
        embed.add_field(name="Status", value="```✅ Active```", inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="user_report", description="[ADMIN] Generate a detailed activity report for a user")
@commands.has_permissions(administrator=True)
async def user_report(interaction: discord.Interaction, member: discord.Member):
    user_id = str(member.id)
    if user_id not in data:
        data[user_id] = {"problems_solved": 0, "last_active": "Never", "activity": {}, "goal": 0}

    problems_solved = data[user_id]["problems_solved"]
    activity = data[user_id].get("activity", {})
    streak_count = get_streak(activity)
    goal = data[user_id].get("goal", 0)
    last_active = data[user_id]["last_active"] if data[user_id]["last_active"] != "Never" else "Never"

    today = datetime.datetime.utcnow().date()
    last_30_days = [(today - datetime.timedelta(days=i)).isoformat() for i in range(30)]
    recent_activity = sum(activity.get(date, 0) for date in last_30_days)

    embed = create_embed(f"Activity Report for {member.display_name}", thumbnail=member.avatar.url if member.avatar else member.default_avatar.url, footer_text=f"Report generated by {interaction.user.display_name}")
    embed.add_field(name="Total Problems Solved", value=f"```{problems_solved}```", inline=True)
    embed.add_field(name="Current Streak", value=f"```{streak_count} days```", inline=True)
    if goal > 0:
        progress_percentage = (problems_solved / goal) * 100
        embed.add_field(name="Goal Progress", value=f"```{problems_solved} / {goal} ({progress_percentage:.1f}%)```", inline=True)
    else:
        embed.add_field(name="Goal", value="```Not set```", inline=True)
    embed.add_field(name="Last Active", value=f"```{last_active[:10]}```" if last_active != "Never" else "```Never```", inline=True)
    embed.add_field(name="Last 30 Days", value=f"```{recent_activity}```", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@user_report.error
async def user_report_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)

bot.run(TOKEN)