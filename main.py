import asyncio
import logging
import logging.config
import os
import time
import sys
import signal

import discord
import dotenv
import yaml
from discord.ext import commands

from discord_slash import SlashCommand
from discord_components import DiscordComponents

CORE_EXTENSIONS = [
    "bot.cogs.core.events",
    "bot.cogs.core.help",
    "bot.cogs.core.info",
    "bot.cogs.core.owner",
    "bot.cogs.core.settings",
    "bot.cogs.core.tasks",
]

EXTENSIONS = [
    # "bot.cogs.colors",
    # "bot.cogs.economy",
    "bot.cogs.embeds",
    "bot.cogs.fun",
    "bot.cogs.games",
    # "bot.cogs.greetings",
    # "bot.cogs.links",
    "bot.cogs.math",
    "bot.cogs.moderation",
    # "bot.cogs.modlogs",
    "bot.cogs.reaction_roles",
    "bot.cogs.search",
    "bot.cogs.starboard",
    "bot.cogs.suggestions",
]


with open("logging.yml", "r") as f:
    logging.config.dictConfig(yaml.load(f, Loader=yaml.SafeLoader))


def main():
    logger = logging.getLogger(__name__)
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
    bots = []
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
                intents=discord.Intents.all()
                if botconf["gateway_intents"]
                else discord.Intents.default(),
                description=botconf["description"],
            )
            bot.name = botconf["name"]
            bot.token = (
                os.environ[botconf["token"]["name"]]
                if botconf["token"]["env"]
                else botconf["token"]["value"]
            )
            bot.AZURE_KEY = os.environ["AZURE_KEY"]
        except:
            adplogger.error(
                "Failed to create bot instance. Check your config.yml file."
            )
            sys.exit(1)

        adplogger.info(
            "Activating Discord interactions (slash commands, buttons, and selects)."
        )

        slash = SlashCommand(bot, sync_commands=True)
        # DiscordComponents(bot)

        adplogger.info("Loading extensions.")

        for extension in CORE_EXTENSIONS:
            bot.load_extension(extension)

        for extension in EXTENSIONS:
            bot.load_extension(extension)

        # if botconf["extensions"]["enabled"]:
        #     for extension in botconf["extensions"]["enabled"]:
        #         try:
        #             bot.load_extension(extension)
        #         except:
        #             adplogger.error(
        #                 f"Unable to load extension {extension}. Check if the file exists."
        #             )
        # if botconf["extensions"]["disabled"]:
        #     for extension in EXTENSIONS:
        #         if extension not in botconf["extensions"]["disabled"]:
        #             bot.load_extension(extension)

        # if botconf["extensions"]["custom"]:
        #     for extension in botconf["extensions"]["custom"]:
        #         try:
        #             bot.load_extension(extension)
        #         except:
        #             adplogger.error(
        #                 f"Unable to load extension {extension}. Check if the file exists.",
        #                 exc_info=True,
        #             )

        bots.append(bot)

    loop = asyncio.get_event_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
        loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
    except NotImplementedError:
        pass

    for bot in bots:
        logger.info("Starting bot.", extra={"botname": bot.name})
        loop.create_task(bot.start(bot.token))

    loop.run_forever()
    # except KeyboardInterrupt:
    #     logger.info("Received signal to shut down bots.", extra={"botname": "N/A"})
    #     loop.stop()
    # except Exception as e:
    #     print(e)


if __name__ == "__main__":
    main()
