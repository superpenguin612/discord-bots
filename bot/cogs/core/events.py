import asyncio
import json
import logging
import os
import time

import asyncpg
import discord
from discord.ext import commands
from discord_slash.context import SlashContext

from bot.helpers import tools

clogger = logging.getLogger("command")


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        _logger = logging.getLogger(__name__)
        self.logger = logging.LoggerAdapter(_logger, {"botname": self.bot.name})
        self.clogger = logging.getLogger("commands")

    async def create_db_pool(self):
        DATABASE_URL = os.environ["DATABASE_URL"]
        return await asyncpg.create_pool(
            DATABASE_URL, min_size=1, max_size=2, ssl="require"
        )

    @commands.Cog.listener(name="on_ready")
    async def on_ready(self) -> None:

        self.logger.info(f"Bot is ready.")
        self.logger.info(f"User: {self.bot.user}")
        self.logger.info(f"ID: {self.bot.user.id}")

        if self.bot.user.id == 802211256383438861:  # chs bot
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name=f"Now with slash commands! Type / to test them out! | c?help",
                )
            )
        elif self.bot.user.id == 821888273936810014:  # chs bot beta
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing, name=f"beta pog | cc?help"
                )
            )
        elif self.bot.user.id == 796805491186597968:  # davidhackerman bot
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing, name="$help | this is a good bot"
                )
            )
        self.bot.db = await self.create_db_pool()

    @commands.Cog.listener(name="on_connect")
    async def on_connect(self) -> None:
        self.logger.info("Connected to Discord websocket.")

    @commands.Cog.listener(name="on_slash_command_error")
    async def on_slash_command_error(self, ctx: SlashContext, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            embed = tools.create_error_embed(
                ctx,
                f"This command has been rate-limited. Please try again in {time.strftime('%Mm %Ss', time.gmtime(round(error.retry_after, 1)))}.",
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = tools.create_error_embed(
                ctx,
                f"You do not have the required permissions to run this command.\nMissing permission(s): {','.join(error.missing_perms)}",
            )
        elif isinstance(error, asyncio.TimeoutError):
            embed = tools.create_error_embed(ctx, "You didn't respond in time!")
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = tools.create_error_embed(
                ctx,
                f"You are missing a required argument for the command. Please check the help text for the command in question.\nMissing argument: {error.param}",
            )
        elif isinstance(error, commands.BotMissingPermissions):
            embed = tools.create_error_embed(
                ctx,
                f"The bot does not have the required permissions to run this command.\nMissing permission(s): {','.join(error.missing_perms)}",
            )
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, asyncio.TimeoutError):
                embed = tools.create_error_embed(
                    ctx, "Sorry, you didn't respond in time!"
                )
            else:
                embed = tools.create_error_embed(
                    ctx,
                    f"Uh oh! Something went wrong, and this error wasn't anticipated. Sorry about that! I'll ping the owners of this bot to fix it.\nError: {error.__class__.__name__}",
                )
                await ctx.send(embed=embed)
                # author1 = await ctx.guild.fetch_member(688530998920871969)
                # await ctx.send(f"{author1.mention}")
            raise error
        else:
            embed = tools.create_error_embed(
                ctx,
                f"Uh oh! Something went wrong, and this error wasn't anticipated. Sorry about that! I'll ping the owners of this bot to fix it.\nError: {error.__class__.__name__}",
            )
            await ctx.send(embed=embed)
            # author1 = await ctx.guild.fetch_member(688530998920871969)
            # await ctx.send(f"{authorx1.mention}")
            raise error
        await ctx.send(embed=embed)

    @commands.Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        print(error)
        if isinstance(error, commands.CommandOnCooldown):
            embed = tools.create_error_embed(
                ctx,
                f"This command has been rate-limited. Please try again in {time.strftime('%Mm %Ss', time.gmtime(round(error.retry_after, 1)))}.",
            )
        elif isinstance(error, commands.MissingPermissions):
            embed = tools.create_error_embed(
                ctx,
                f"You do not have the required permissions to run this command.\nMissing permission(s): {','.join(error.missing_perms)}",
            )
        elif isinstance(error, asyncio.TimeoutError):
            embed = tools.create_error_embed(ctx, "You didn't respond in time!")
        elif isinstance(error, commands.CommandNotFound):
            embed = tools.create_error_embed(ctx, "Sorry, that command does not exist!")
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = tools.create_error_embed(
                ctx,
                f"You are missing a required argument for the command. Please check the help text for the command in question.\nMissing argument: {error.param}",
            )
        elif isinstance(error, commands.BotMissingPermissions):
            embed = tools.create_error_embed(
                ctx,
                f"The bot does not have the required permissions to run this command.\nMissing permission(s): {','.join(error.missing_perms)}",
            )
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, asyncio.TimeoutError):
                embed = tools.create_error_embed(
                    ctx, "Sorry, you didn't respond in time!"
                )
                ctx.command.reset_cooldown(ctx)
            else:
                embed = tools.create_error_embed(
                    ctx,
                    f"Uh oh! Something went wrong, and this error wasn't anticipated. Sorry about that! I'll ping the owners of this bot to fix it.\nError: {error.__class__.__name__}",
                )
                await ctx.send(embed=embed)
                # author1 = await ctx.guild.fetch_member(688530998920871969)
                # await ctx.send(f"{author1.mention}")
            raise error
        else:
            embed = tools.create_error_embed(
                ctx,
                f"Ok, something really went wrong. This error message isn't supposed to show up, so ig I messed up pretty badly lmao",
            )
            await ctx.send(embed=embed)
            # author1 = await ctx.guild.fetch_member(688530998920871969)
            # await ctx.send(f"{author1.mention}")
            raise error
        await ctx.send(embed=embed)
        # ctx.command.reset_cooldown(ctx)

    # @commands.Cog.listener()
    # async def on_command(self, ctx: commands.Context) -> None:
    #     self.clogger.info(
    #         "",
    #         extra={
    #             "botname": self.bot.name,
    #             "username": ctx.author.name,
    #             "userid": ctx.author.id,
    #             "guild": ctx.guild.name,
    #             "guildid": ctx.guild.id,
    #             "prefix": ctx.prefix,
    #             "command": ctx.command.qualified_name,
    #             "arguments": ctx.args,
    #             "full": ctx.message.content,
    #         },
    #     )

    # @commands.Cog.listener()
    # async def on_slash_command(self, ctx: SlashContext) -> None:
    #     self.clogger.info(
    #         "",
    #         extra={
    #             "botname": self.bot.name,
    #             "username": ctx.author.name,
    #             "userid": ctx.author.id,
    #             "guild": ctx.guild.name,
    #             "guildid": ctx.guild.id,
    #             "prefix": "/",
    #             "command": ctx.command.qualified_name,
    #             "arguments": ctx.args,
    #             "full": ctx.message.content,
    #         },
    #     )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Events(bot))
