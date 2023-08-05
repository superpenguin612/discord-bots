import asyncio
import logging
import time

import discord
from discord.ext import commands
from bot.cogs.custom.chsbot import create_persistent_role_selector

from bot.helpers import tools

clogger = logging.getLogger("command")


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        _logger = logging.getLogger(__name__)
        self.logger = logging.LoggerAdapter(_logger, {"botname": self.bot.name})
        self.clogger = logging.getLogger("commands")

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self) -> None:
        self.logger.info("Syncing commands")
        await self.bot.tree.sync()

        self.logger.info(f"Bot is ready.")
        self.logger.info(f"User: {self.bot.user}")
        self.logger.info(f"ID: {self.bot.user.id}")

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"the Unofficial CHS Discord!",
            )
        )

        self.bot.add_view(
            create_persistent_role_selector(self.bot.get_guild(704819543398285383))
        )

    @commands.Cog.listener(name="on_connect")
    async def on_connect(self) -> None:
        self.logger.info("Connected to Discord websocket.")

    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        error = getattr(error, "original", error)
        if isinstance(error, commands.CommandOnCooldown):
            embed = tools.create_error_embed(
                f"This command has been rate-limited. Please try again in {time.strftime('%Mm %Ss', time.gmtime(round(error.retry_after, 3)))}.",
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = tools.create_error_embed(
                f"You do not have the required permissions to run this command.\nMissing permission(s): {','.join(error.missing_perms)}",
            )
        elif isinstance(error, commands.NotOwner):
            embed = tools.create_error_embed("You cannot run this command.")
        elif isinstance(error, asyncio.TimeoutError):
            embed = tools.create_error_embed("You didn't respond in time!")
        elif isinstance(error, commands.CommandNotFound):
            embed = tools.create_error_embed("Sorry, that command does not exist!")
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = tools.create_error_embed(
                f"You are missing a required argument for the command. Please check the help text for the command in question.\nMissing argument: {error.param}",
            )
        elif isinstance(error, commands.BotMissingPermissions):
            embed = tools.create_error_embed(
                f"The bot does not have the required permissions to run this command.\nMissing permission(s): {','.join(error.missing_perms)}",
            )
        elif isinstance(error, commands.BadArgument):
            embed = tools.create_error_embed(
                f"An argument for the command was of incorrect type. Please check the help text for the command in question.\nError: {error.args[0]}",
            )
        else:
            embed = tools.create_error_embed(
                f"Uh oh! Something went wrong, and this error wasn't anticipated. Sorry about that!\nError: {error.__class__.__name__}",
            )
            await ctx.send(embed=embed)
            raise error
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        extra = {
            "botname": self.bot.name,
            "username": ctx.author.name,
            "userid": ctx.author.id,
            "guild": ctx.guild.name,
            "guildid": ctx.guild.id,
            "prefix": ctx.prefix,
            "command": ctx.command.qualified_name,
            "arguments": ctx.message.content.split()[1:],
            "full": ctx.message.content,
        }

        self.clogger.info(
            "Command",
            extra=extra,
        )

    # @commands.Cog.listener()
    # async def on_member_join(self, member: discord.Member) -> None:
    #     channel = member.guild.get_channel(451027883054465055)
    #     embed = discord.Embed(
    #         description=f"Welcome to the TechHOUNDS Discord, {member.name}.\nPlease read the <#994706215462523010>.\nTo enter the server, please go to <#993980468934488074> to set your division, name, and pronouns."
    #     )
    #     await channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Events(bot))
