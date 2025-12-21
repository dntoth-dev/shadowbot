import logging
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

load_dotenv()

# Required env vars
TOKEN = os.getenv("BOT_TOKEN")
DEV_ID = os.getenv("DEV_ID") or os.getenv("DEV") # numeric ID
DEV = os.getenv("DEV")
SHADOW_ID = os.getenv("SHADOW_ID") or os.getenv("SHADOW")
SHADOW = os.getenv("SHADOW")

if not TOKEN:
    raise SystemExit("Missing BOT_TOKEN in environment (.env)")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shadowbot")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


def _matches_identity(member: discord.Member, identity: str | None) -> bool:
    """
    Compare a member to an identity value. If the identity looks like an integer,
    compare against the member's ID. Otherwise compare against the member name.
    """
    if not identity:
        return False

    try:
        identity_id = int(identity)
    except ValueError:
        identity_id = None

    if identity_id is not None:
        return member.id == identity_id

    # fallback: compare username (not ideal since names can change)
    return member.name == identity


@bot.event
async def on_ready():
    logger.info("Logged in as %s (id=%s)", bot.user, bot.user.id)


@bot.command(name="devtest")
async def devtest(ctx: commands.Context):
    """Dev-only test command."""
    if _matches_identity(ctx.author, DEV_ID):
        await ctx.send(
            "devtest. Hello world!\n"
            f"`Client connected to Discord Gateway & logged in as {bot.user}.`"
        )
    else:
        await ctx.send("You do not have permission to use this command.")


@bot.command(name="am-i-shadow", description="Predicts if the message author is Shadow or not.")
async def am_i_shadow(ctx: commands.Context):
    """Check if the invoking user is the configured guild owner."""
    if _matches_identity(ctx.author, SHADOW_ID):
        await ctx.send(f"Yes, you are {SHADOW}.")
    else:
        await ctx.send(f"You ain't {SHADOW} :(")


@bot.command(name="pingsb")
async def pingsb(ctx: commands.Context):
    await ctx.send("Pong!")


if __name__ == "__main__":
    bot.run(TOKEN)