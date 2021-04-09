import discord
from discord.ext import commands
from discord_slash import SlashCommand
import os
import dotenv
import asyncpg

from bot.cogs.help import HelpCommand

# ----------------
# All perms
# https://discord.com/api/oauth2/authorize?client_id=796805491186597968&permissions=4294967295&scope=bot%20applications.commands
# All but admin perms
# https://discord.com/api/oauth2/authorize?client_id=796805491186597968&permissions=4294967287&scope=bot%20applications.commands
# Moderation perms
# https://discord.com/api/oauth2/authorize?client_id=796805491186597968&permissions=2146823287&scope=bot%20applications.commands
# Basic perms
# https://discord.com/api/oauth2/authorize?client_id=796805491186597968&permissions=37080128&scope=bot%20applications.commands
# No slash perms
# https://discord.com/api/oauth2/authorize?client_id=796805491186597968&permissions=379968&scope=bot%20applications.commands
# ----------------

EXTENSIONS = [
    "bot.cogs.events",
    "bot.cogs.school",
    "bot.cogs.fun",
    "bot.cogs.info",
    "bot.cogs.search",
    "bot.cogs.reaction_roles",
    "bot.cogs.moderation",
    "bot.cogs.settings",
    "bot.cogs.games",
    "bot.cogs.tasks",
    "bot.cogs.starboard",
    "bot.cogs.logging",
    "bot.davidhackerman.cogs.bottling",
    "bot.davidhackerman.cogs.links",
]

bot = commands.Bot(
    command_prefix="$",
    intents=discord.Intents.all(),
    max_messages=10000,
    allowed_mentions=discord.AllowedMentions(everyone=False),
)
slash = SlashCommand(bot, sync_commands=True)
bot.description = f"Welcome to davidhackerman! Visit `{bot.command_prefix}help` for a list of commands and how to use them. Visit `{bot.command_prefix}about` to see more information about the bot."
bot.help_command = HelpCommand()
dotenv.load_dotenv()
bot.AZURE_KEY = os.environ["AZURE_KEY"]


def start():
    for extension in EXTENSIONS:
        bot.load_extension(extension)
    bot.run(os.environ["TOKEN"])  # bot token


if __name__ == "__main__":
    start()
