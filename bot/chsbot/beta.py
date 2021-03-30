import discord
from discord.ext import commands
from discord_slash import SlashCommand
import os
import dotenv
import asyncpg

from bot.cogs.events import Events
from bot.cogs.school import School
from bot.cogs.fun import Fun
from bot.cogs.info import Info
from bot.cogs.search import Search
from bot.cogs.help import HelpCommand
from bot.cogs.reaction_roles import ReactionRoles
from bot.cogs.embeds import Embeds
from bot.cogs.moderation import Moderation
from bot.cogs.settings import Settings
from bot.cogs.games import Games
from bot.chsbot.cogs.suggestions import Suggestions
from bot.chsbot.cogs.profanity import Profanity

# https://discord.com/api/oauth2/authorize?client_id=796805491186597968&permissions=2147483639&scope=bot

@commands.command()
@commands.has_permissions(administrator=True)
async def runpayload(ctx):
    pass

def start():
    bot = commands.Bot(command_prefix='cc?', intents=discord.Intents.all(), help_command=None)
    slash = SlashCommand(bot, sync_commands=True)
    bot.description = f'Welcome to CHS Bot Beta! This is the bleeding edge of CHS Bot, so you can test features as they come out! Visit `{bot.command_prefix}help` for a list of commands and how to use them. Visit `{bot.command_prefix}about` to see more information about the bot.'
    bot.add_cog(Events(bot))
    bot.add_cog(Suggestions(bot))
    bot.add_cog(School(bot))
    bot.add_cog(Fun(bot))
    bot.add_cog(Info(bot))
    bot.add_cog(Games(bot))
    bot.add_cog(Profanity(bot))
    bot.add_cog(Search(bot))
    bot.add_cog(ReactionRoles(bot))
    bot.add_cog(Embeds(bot))
    bot.add_cog(Moderation(bot))
    bot.add_cog(Settings(bot))
    bot.add_command(runpayload)
    dotenv.load_dotenv()
    bot.AZURE_KEY = os.environ['AZURE_KEY']
    bot.run(os.environ['BETA_TOKEN']) # bot token

if __name__ == "__main__":
    start()