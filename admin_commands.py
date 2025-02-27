import discord
from discord import app_commands
from discord.ext import commands


def setup(bot):

    @bot.tree.command(name="test_command", description="A basic test command")
    async def test_command(interaction: discord.Interaction):
        await interaction.response.send_message("✅ Command executed!", ephemeral=True)

