# general.py
import os
from dotenv import load_dotenv
from discord.ext import commands
from cogs import general

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Change only the no_category default string
help_command = commands.DefaultHelpCommand(
    no_category='Help'
)

bot = commands.Bot(command_prefix='$', help_command=help_command)
general.setup(bot)
bot.run(TOKEN)
