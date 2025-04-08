import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load environment variables 
load_dotenv()

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

INITIAL_EXTENSIONS = [
    'cogs.music',
    'cogs.games',
    'cogs.moderation',
    'cogs.utils',
    'cogs.sort',
]


async def load_extensions():
    for extension in INITIAL_EXTENSIONS:
        try:
            await bot.load_extension(extension)
            print(f'Loaded extension {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}.\n{type(e).__name__}: {e}')

@bot.event
async def on_ready():
    await load_extensions()
    print(f'{bot.user} has connected to Discord!')

if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN is None:
        print("Please set up your DISCORD_TOKEN in .env file")
        exit(1)
    bot.run(TOKEN)
    