import discord
from discord.ext import commands
import os
import dotenv
import random

from bot.cogs.events import Events
from bot.cogs.school import School
from bot.cogs.fun import Fun
from bot.cogs.help import HelpCommand
from bot.cogs.info import Info
from bot.cogs.search import Search
from bot.games.tictactoe import TicTacToe
from bot.davidhackerman.cogs.economy import Economy
from bot.davidhackerman.cogs.links import Links
from bot.cogs.punishments import Punishments
from bot.davidhackerman.cogs.bottling import Bottling

# https://discord.com/api/oauth2/authorize?client_id=796805491186597968&permissions=2147483639&scope=bot

def start():
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)
    bot.add_cog(Events(bot))
    bot.add_cog(School(bot))
    bot.add_cog(Fun(bot))
    bot.add_cog(Info(bot))
    bot.add_cog(Search(bot))
    bot.add_cog(Links(bot))
    bot.add_cog(Economy(bot))
    bot.add_cog(Punishments(bot))
    bot.add_cog(TicTacToe(bot))
    bot.add_cog(Bottling(bot))
    dotenv.load_dotenv()
    bot.AZURE_KEY = os.environ['AZURE_KEY']
    bot.help_command = HelpCommand()
    bot.run(os.environ['TOKEN']) # bot token

if __name__ == "__main__":
    start()