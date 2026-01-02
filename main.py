import logging
import os
from discord import Guild, User
from dotenv import load_dotenv

import discord
from discord import Interaction, app_commands
from discord.ext import commands
import datetime
from googleapiclient.discovery import build

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
SM_CH_ID = os.getenv("SM_YT_CHANNEL_ID")

GUILD = discord.Object(id=SHADOW_GUILD)
youtube = build('youtube', 'v3', developerKey=YT_API)


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

@client.tree.command(name="clear_slash", description="Clear all slash commands in case of a bug. - **Developer use only!**")
@commands.is_owner()
async def clear_slash(interaction: discord.Interaction): # use this ONLY if slash commands remain in the guild (list) after removal from code. requires restart after! developer use only!
    # clr local tree
    client.tree.clear_commands(guild=None)
    client.tree.clear_commands(guild=GUILD)
    # sync empty tree to global
    await client.tree.sync()
    await interaction.response.send_message("Cleared all slash commands from `global`, and `guild` (Shadow's Community)\n`INFO:` Restart required to sync.")


@client.tree.command(name="hello", description="Says hello to the user.")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hello, {interaction.user.mention}!')

@client.tree.command(name="pingsb", description="Returns the bot's latency.")
async def pingsb(interaction: discord.Interaction):
    """Returns the bot's latency."""
    await interaction.response.send_message(f'Pong! {int(client.latency * 1000)}ms')

@client.tree.command(name="am_i_shadow", description="Returns if the user is @Shadow Master or not.")
async def am_i_shadow(interaction: discord.Interaction):
    if str(interaction.user.id) == SHADOW_ID:
        await interaction.response.send_message(f'Yes, you are {SHADOW}.')
    else:
        await interaction.response.send_message(f"You ain't {SHADOW} :(")

@client.tree.command(name="devtest", description="Bot status test command. - **Developer use only!**")
@commands.is_owner()
async def devtest(interaction: discord.Interaction):
    """Dev-only test command usable only by the application/bot owner."""
    await interaction.response.send_message(
        "devtest. Hello world!\n"
        f"`Client connected to Discord Gateway & logged in as {client.user}.`"
    )

# Moderation commands (Timeout/Untimeout, Kick, Ban/Unban)
# region

# MUTE / TIMEOUT
@client.tree.command(name="mute", description="Timeout a member (mute). - **Moderator use only!**")
@commands.has_any_role(SHADOW_ROLE or ADMIN or MODERATOR)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided."):
    duration = datetime.timedelta(minutes=float(minutes))
    try:
        if interaction.guild.me.top_role > member.top_role:
            await member.timeout(duration, reason=reason)
            await interaction.response.send_message(f"### Timeout successful!\n**User:** {member.name} (ID: {member.id})\n**Duration:** {minutes} minutes\n**Reason:** {reason}")
        else:
            await interaction.response.send_message("Failed to mute/timeout because I am not high enough in the role hierarchy.", ephemeral=True)
    except Exception as e:
        return e

# UNMUTE / UNTIMEOUT
@client.tree.command(name="unmute", description="Remove timeout (unmute) from a member. - **Moderator use only!**")
@commands.has_any_role(SHADOW_ROLE or ADMIN or MODERATOR)
async def unmute(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
    if interaction.guild.me.top_role > member.top_role:
        await member.timeout(None, reason=reason)
        await interaction.response.send_message(f"### Untimeout successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
    else:
        await interaction.response.send_message("Failed to unmute/untimeout because I am not high enough in the role hierarchy.", ephemeral=True)

# KICK
@client.tree.command(name="kick", description="Kick a member from the server. - **Moderator use only!**")
@commands.has_any_role(SHADOW_ROLE or ADMIN or MODERATOR)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
    try:
        if interaction.guild.me.top_role > member.top_role:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"### Kick successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
        else:
            await interaction.response.send_message("Failed to kick because I am not high enough in the role hierarchy.", ephemeral=True)
    except Exception as e:
        return e
# BAN
@client.tree.command(name="ban", description="Ban a member from the server. - **Moderator use only!**")
@commands.has_any_role(SHADOW_ROLE or ADMIN or MODERATOR)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided."):
    try:
        if interaction.guild.me.top_role > member.top_role:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"### Ban successful!\n**User:** {member.name} (ID: {member.id})\n**Reason:** {reason}")
        else:
            await interaction.response.send_message("Failed to ban because I am not high enough in the role hierarchy.", ephemeral=True)
    except Exception as e:
        return e

# UNBAN
@client.tree.command(name="unban", description="Unban a member from the server. - **Moderator use only!**")
@commands.has_any_role(SHADOW_ROLE or ADMIN or MODERATOR)
async def unban(interaction: discord.Interaction, user: User, reason: str ="No reason provided."):
    try:
        handled = False
        async for ban in interaction.guild.bans():
            if ban.user.id == user.id:
                await interaction.guild.unban(user, reason=reason)
                await interaction.response.send_message(f"### Unban successful!\n**User:** {user.name} (ID: {user.id})\n**Reason:** {reason}")
                handled = True
        if handled == False:
            await interaction.response.send("User not found in ban list.", ephemeral=True)
    except Exception as e:
        return e

# endregion

# Membercount command
@client.tree.command(name="membercount", description="Returns the number of members on the server.")
async def membercount(interaction: discord.Interaction):
    try:
        membernum = interaction.guild.member_count
        await interaction.response.send_message(f'The server has {membernum} members!')
    except Exception as e:
        return e

# Member records commands
# region

# Recordsauthor command
@client.tree.command(name="recordsauthor", description="Show the records of a user. - **Moderator use only!**")
@app_commands.checks.has_permissions(view_audit_log=True)
async def recordsauthor(interaction: discord.Interaction, user: discord.User):
    # 1. Acknowledge the command immediately
    await interaction.response.send_message(f"### Records of: **{user.name}** (ID: {user.id})\nSearching logs...")

    try:
        found_logs = False
        # 2. Filter audit logs by the specific user to save memory and time
        async for entry in interaction.guild.audit_logs(limit=10, user=user):
            found_logs = True
            log_message = (
                f"**Moderator:** <@{entry.user_id}>\n"
                f"**Action:** {entry.action}\n"
                f"**Target:** {entry.target}\n"
                f"**Reason:** {entry.reason if entry.reason else 'No reason provided'}\n"
                "---"
            )
            # 3. Use followup because the initial response is already sent
            await interaction.followup.send(content=log_message)

        if not found_logs:
            await interaction.followup.send("No recent audit log entries found for this user.", ephemeral=True)

    except discord.Forbidden:
        await interaction.followup.send("I do not have the 'View Audit Log' permission.", ephemeral=True)
    except Exception as e:
        print(f"Error: {e}")
        await interaction.followup.send("An error occurred while fetching logs.", ephemeral=True)


# Recordstarget command
@client.tree.command(name="recordstarget", description="Show records targeted at a user. - **Moderator use only!**")
@app_commands.checks.has_permissions(view_audit_log=True)
async def recordstarget(interaction: discord.Interaction, user: discord.User):
    # 1. Immediate response to prevent timeout
    await interaction.response.send_message(f"### Actions taken against: **{user.name}**\nSearching...")

    try:
        results = []
        # 2. Iterate with a limit. Note: target filtering happens in the loop
        async for entry in interaction.guild.audit_logs(limit=100):
            if entry.target and entry.target.id == user.id:
                Action = f"**Action:** {entry.action}"
                results.append(
                    f"**Target:** {entry.target}\n"
                    f"**Action:** {entry.action}\n"
                    f"**Moderator:** <@{entry.user_id}>\n"
                    f"**Reason:** {entry.reason or 'No reason provided'}\n"
                    "---"
                )

        if not results:
            await interaction.followup.send("No records found for this user in the last 100 audit entries.", ephemeral=True)
        else:
            # 3. Join results to avoid sending dozens of individual messages (avoids rate limits)
            full_log = "\n".join(results)
            # If the log is too long for one message (2000 char limit), we slice it
            await interaction.followup.send(content=full_log[:2000])

    except discord.Forbidden:
        await interaction.followup.send("I don't have 'View Audit Log' permissions.", ephemeral=True)
    except Exception as e:
        print(f"Error: {e}")
        await interaction.followup.send("An error occurred.", ephemeral=True)
# endregion
# YouTube integration commands
# region

@client.tree.command(name="recentvids", description="Get recent videos of Shadow!")
@app_commands.describe(amount="Number of recent videos to fetch (max 5).")
async def recentvids(interaction: Interaction, amount: int):
    try:
        if amount > 5:
            await interaction.response.send_message("The maximum number of videos to return is 5!", ephemeral=True)
            return

        # convert channel ID (UC...) to uploads playlist ID (UU...)
        uploads_playlist_id = f"UU{SM_CH_ID[2:]}"

        # 2. Fetch the latest item from that playlist
        request = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part="snippet",
            maxResults=amount
        )
        response = request.execute()

        if not response['items']:
            await interaction.response.send_message("No videos found for this channel.")
            return
        else:
            await interaction.response.send_message(f"🎥 Recent {amount} videos from Shadow's YouTube channel:")
        
        for i in response['items']:
            video_data = i['snippet']
            video_title = video_data['title']
            video_id = video_data['resourceId']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            await interaction.followup.send(f"🎬 **{video_title}**\n{video_url}")

    except Exception as e:
        await interaction.response.send_message("❌ Error!")
        print(f"Error fetching latest video: {e}")

@client.tree.command(name='commands', description='View the current available commands of the bot')
async def commands_list(interaction: Interaction):
    """Sends a list of all available slash commands."""
    commands = client.tree.get_commands(guild=GUILD)
    command_list = "\n".join([f"`/{cmd.name}` - {cmd.description}" for cmd in commands])
    await interaction.response.send_message(f"### Current Commands:\n{command_list}")

if __name__ == "__main__":
    client.run(TOKEN)
