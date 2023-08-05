import asyncio
import logging
import logging.config
import os
import sys
import time

import discord
import dotenv
import yaml
from discord.ext import commands

from bot.helpers import tools

logger = logging.getLogger(__name__)

CORE_EXTENSIONS = [
    "bot.cogs.core.events",
    "bot.cogs.core.help",
    "bot.cogs.core.info",
    "bot.cogs.core.owner",
    "bot.cogs.core.settings",
    "bot.cogs.core.tasks",
]

EXTENSIONS = [
    "bot.cogs.embeds",
    "bot.cogs.fun",
    "bot.cogs.games",
    "bot.cogs.math",
    "bot.cogs.moderation",
    "bot.cogs.reaction_roles",
    "bot.cogs.search",
    "bot.cogs.starboard",
    "bot.cogs.suggestions",
]

with open("logging.yml", "r") as f:
    logging.config.dictConfig(yaml.load(f, Loader=yaml.SafeLoader))


async def main():
    dotenv.load_dotenv()
    try:
        with open("config.yml", "r") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        logger.critical(
            "No config.yml found. Please make sure it is in this directory.",
            extra={"botname": "N/A"},
        )
        sys.exit(1)

    logger.info("Parsing config.yml.", extra={"botname": "N/A"})
    bots: list[commands.Bot] = []
    for botconf in config["bots"]:
        adplogger = logging.LoggerAdapter(logger, extra={"botname": botconf["name"]})
        try:
            if not botconf["name"]:
                adplogger.error(
                    "Misconfigured config.yml file. You must set a name for each bot."
                )
            if not botconf["prefix"]:
                adplogger.error(
                    "Misconfigured config file. You must set a prefix for each bot."
                )
            if not botconf["token"]["value"] and not botconf["token"]["env"]:
                adplogger.error(
                    "Misconfigured config.yml file. You must set the bot's token either in config.yml or in your .env file."
                )
            if botconf["token"]["value"] and botconf["token"]["env"]:
                adplogger.error(
                    "Misconfigured config.yml file. You cannot have both value and env declared under token."
                )
        except KeyError:
            adplogger.error(
                "Invalid config.yml file. One or more keys are missing. Please use the template provided in the repository as well as the tutorial for configuring your bot.",
            )
            sys.exit(1)

        adplogger.info("Creating bot instance.")
        try:
            bot = commands.Bot(
                command_prefix=botconf["prefix"],
                help_command=commands.DefaultHelpCommand
                if botconf["use_default_help_command"]
                else None,
                intents=discord.Intents.all(),
                description=botconf["description"],
            )
            bot.owner_id = 688530998920871969
            bot.name = botconf["name"]
            bot.token = (
                os.environ[botconf["token"]["name"]]
                if botconf["token"]["env"]
                else botconf["token"]["value"]
            )
        except:
            adplogger.exception(
                "Failed to create bot instance. Check your config.yml file."
            )

            sys.exit(1)

        adplogger.info("Loading extensions.")

        for extension in botconf["extensions"]:
            await bot.load_extension(extension)

        bots.append(bot)

    for bot in bots:
        logger.info("Starting bot.", extra={"botname": bot.name})
        async with bot:
            await bot.start(bot.token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received signal to shut down.", extra={"botname": "N/A"})
        exit(0)
