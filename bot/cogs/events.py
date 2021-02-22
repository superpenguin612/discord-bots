import discord
from discord.ext import commands
from bot.helpers import tools
import asyncio
import time
import asyncpg
import os

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_db_pool(self):
        DATABASE_URL = os.environ['DATABASE_URL']
        return await asyncpg.connect(DATABASE_URL, ssl='require')

    @commands.Cog.listener(name='on_ready')
    async def on_ready(self):
        print(f'Logged in.\nUser: {self.bot.user}\nID: {self.bot.user.id}\n----------------------')
        if self.bot.user.id == 802211256383438861: # chs bot
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='be my valentine? | c?help'))
        elif self.bot.user.id == 796805491186597968: # davidhackerman bot
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='$help | this is a good bot'))
        self.bot.db = await self.create_db_pool()
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = tools.create_error_embed(ctx, f"This command has been rate-limited. Please try again in {time.strftime('%Mm %Ss', time.gmtime(round(error.retry_after, 1)))}.")
        elif isinstance(error, commands.MissingPermissions):
            embed = tools.create_error_embed(ctx, f"You do not have the required permissions to run this command.\nMissing permission(s): {','.join(error.missing_perms)}")
        elif isinstance(error, asyncio.TimeoutError):
            embed = tools.create_error_embed(ctx, "You didn't respond in time!")
        elif isinstance(error, commands.CommandNotFound):
            embed = tools.create_error_embed(ctx, "Sorry, that command does not exist!")
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = tools.create_error_embed(ctx, f"You are missing a required argument for the command. Please check the help text for the command in question.\nMissing argument: {error.param}")
        elif isinstance(error, commands.BotMissingPermissions):
            embed = tools.create_error_embed(ctx, f"The bot does not have the required permissions to run this command.\nMissing permission(s): {','.join(error.missing_perms)}")
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, asyncio.TimeoutError):
                embed = tools.create_error_embed(ctx, "Sorry, you didn't respond in time!")
            else:
                embed = tools.create_error_embed(ctx, f"Uh oh! Something went wrong, and this error wasn't anticipated. Sorry about that! I'll ping the owners of this bot to fix it.\nError: {error.__class__.__name__}")
                author1 = await ctx.guild.fetch_member(688530998920871969)
                await ctx.send(embed=embed)
                await ctx.send(f"{author1.mention}")
                raise error
        else:
            embed = tools.create_error_embed(ctx, f"Ok, something really went wrong. This error message isn't supposed to show up, so we messed up pretty badly lmfao")
            await ctx.send(embed=embed)
            raise error
        await ctx.send(embed=embed)