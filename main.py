import logging
import os
from discord import guild, user
from dotenv import load_dotenv

import discord
from discord import Interaction, app_commands
from discord.ext import commands
import datetime

load_dotenv()

# Required env vars
TOKEN = os.getenv("BOT_TOKEN")
DEV_ID = os.getenv("DEV_ID") or os.getenv("DEV") # numeric ID prioritized
DEV = os.getenv("DEV")
SHADOW_ID = os.getenv("SHADOW_ID") or os.getenv("SHADOW")
SHADOW = os.getenv("SHADOW")
SHADOW_GUILD = os.getenv("SHADOWS_COMMUNITY_GUILD_ID")
ADMIN = os.getenv("ADMIN_ROLE_ID")
SHADOW_ROLE = os.getenv("SHADOW_ROLE_ID")
MODERATOR = os.getenv("MODERATOR_ROLE_ID")
YT_API = os.getenv("YOUTUBE_API_KEY")

GUILD = discord.Object(id=SHADOW_GUILD)


if not TOKEN:
    raise SystemExit("BOT_TOKEN environment variable is required.")

class MyClient(discord.Client):
    user = discord.Client.user

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.tree.command()
@commands.is_owner()
async def clear_slash(interaction: discord.Interaction): # use this ONLY if slash commands remain in the guild (list) after removal from code. requires restart after! developer use only!
    # clr local tree
    client.tree.clear_commands(guild=None)
    client.tree.clear_commands(guild=GUILD)
    # sync empty tree to global
    await client.tree.sync()
    await interaction.response.send_message("Cleared all slash commands from `global`, and `guild` (Shadow's Community)\n`INFO:` Restart required to sync.")


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hello, {interaction.user.mention}!')

@client.tree.command()
async def pingsb(interaction: discord.Interaction):
    """Returns the bot's latency."""
    await interaction.response.send_message(f'Pong! {int(client.latency * 1000)}ms')

@client.tree.command()
async def am_i_shadow(interaction: discord.Interaction):
    if str(interaction.user.id) == SHADOW_ID:
        await interaction.response.send_message(f'Yes, you are {SHADOW}.')
    else:
        await interaction.response.send_message(f"You ain't {SHADOW} :(")

@client.tree.command()
@commands.is_owner()
async def devtest(interaction: discord.Interaction):
    """Dev-only test command usable only by the application/bot owner."""
    await interaction.response.send_message(
        "devtest. Hello world!\n"
        f"`Client connected to Discord Gateway & logged in as {client.user}.`"
    )

# region Moderation commands
@client.tree.command(name="mute", description="Timeout a member (mute).")
@commands.has_any_role(SHADOW_ROLE or ADMIN or MODERATOR)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided."):
    duration = datetime.timedelta(minutes=float(minutes))
    if interaction.guild.me.top_role >= member.top_role:
        await member.timeout(duration, reason=reason)
        await interaction.response.send_message(f"### Timeout successful!\n**User:** {member.name} (ID: {member.id})\n**Duration:** {minutes} minutes\n**Reason:** {reason}")
    else:
        await interaction.response.send_message("Failed to timeout because the user has a higher role than me.", ephemeral=True)

# unmute command here

@client.tree.command(name="kick", description="Kick a member from the server.")
@commands.has_any_role(SHADOW_ROLE or ADMIN or MODERATOR)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
    if interaction.guild.me.top_role >= member.top_role:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"### Kick successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
    else:
        await interaction.response.send_message("Failed to kick because the user has a higher role than me.", ephemeral=True)

# endregion

@client.tree.command(name="membercount", description="Returns the number of members on the server")
async def membercount(interaction: discord.Interaction):
    membernum = interaction.guild.member_count
    await interaction.response.send_message(f'The server has {membernum} members!')


if __name__ == "__main__":
    client.run(TOKEN)
