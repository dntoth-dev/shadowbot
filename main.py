from calendar import c
import logging
import os
from dotenv import load_dotenv

import discord
from discord import Interaction, app_commands
from discord.ext import commands

load_dotenv()

# Required env vars
TOKEN = os.getenv("BOT_TOKEN")
DEV_ID = os.getenv("DEV_ID") or os.getenv("DEV") # numeric ID prioritized
DEV = os.getenv("DEV")
SHADOW_ID = os.getenv("SHADOW_ID") or os.getenv("SHADOW")
SHADOW = os.getenv("SHADOW")
SHADOW_GUILD = os.getenv("SHADOWS_COMMUNITY_GUILD_ID")

GUILD = discord.Object(id=SHADOW_GUILD)

if not TOKEN:
    raise SystemExit("BOT_TOKEN environment variable is required.")

class MyClient(discord.Client):
    user = discord.ClientUser

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
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await Interaction.response.send(f'Hello, {Interaction.user.mention}!')

@client.tree.command()
async def ping(interaction: discord.Interaction):
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


if __name__ == "__main__":
    client.run(TOKEN)
