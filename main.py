import dotenv
dotenv.load_dotenv()
import os
import discord

TOKEN = os.getenv('BOT_TOKEN')
DEV = os.getenv('DEV_NAME')
GUILD_OWNER = os.getenv('OWNER_NAME')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!devtest'):
        if message.author.name == DEV:
            await message.channel.send(f'devtest. Hello world! \n`Client connected to Discord Gateway & logged in as {client.user}.`')
        else:
            await message.channel.send('You do not have permission to use this command.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!am-i-shadow"):
        if message.author.name == GUILD_OWNER:
            await message.channel.send(f"Yes, you are {GUILD_OWNER}.")
        else:
            await message.channel.send(f"You ain't {GUILD_OWNER} :(")
client.run(TOKEN)
