import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
import random

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name='ping',
        description='Get the latency of the connection between the bot and Discord.',
    )
    async def ping(self, ctx):
        embed = tools.create_embed(ctx, 'Pong!', desc=f'`{round(self.bot.latency * 1000, 1)}ms`')
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='about',
        description='View information about the bot.',
    )
    async def about(self, ctx):
        embed = tools.create_embed(ctx, 'About')
        author = await ctx.guild.fetch_member(688530998920871969)
        embed.add_field(name='Author', value=f'{author.mention}', inline=False)
        embed.add_field(name='Language', value='Python', inline=False)
        embed.add_field(name='Version', value='1.4', inline=False)
        embed.add_field(name='GitHub', value='https://github.com/davidracovan/discord-bots')
        await ctx.send(embed=embed)
    
    @cog_ext.cog_slash(
        name='help',
        description='Get help for the bot.',
    )
    async def help(self, ctx):
        embed = tools.create_embed(ctx, 'Bot Help', 'Welcome to the Slash Commands module of CHS Bot! This is a new feature created by Discord allowing members to use bots more effectively. Thanks for using the bot!')
        embed.add_field(name='How to Use', value='Slash Commands are simple to use! Just type a `/` to see a list of all CHS Bot commands.\n'
            'Press `Tab` whenever the `TAB` icon appears in the message bar to auto-complete the selected command and to complete a command parameter.\n'
            'Explanation text will show for each parameter for a command. If a parameter is optional, it will not appear by default. Press `Tab` when an optional parameter is highlighted to add a value for it.', inline=False)
        embed.add_field(name='"This Interaction Failed"', value='If this message appears, it means that the bot is most likely offline. Commands will still appear when the bot is offline, but they won\'t be runnable. If the bot isn\'t offline, ping the Developer role for help.', inline=False)
        await ctx.send(embed=embed)

    # --------------------------------------------
    # LEGACY COMMANDS
    # --------------------------------------------

    @commands.command()
    async def ping(self, ctx):
        """Get the latency of the connection between the bot and Discord."""
        embed = tools.create_embed(ctx, 'Pong!', desc=f'`{round(self.bot.latency * 1000, 1)}ms`')
        await ctx.send(embed=embed)

    @commands.command()
    async def about(self, ctx):
        """View information about the bot."""
        embed = tools.create_embed(ctx, 'About')
        author = await ctx.guild.fetch_member(688530998920871969)
        embed.add_field(name='Author', value=f'{author.mention}', inline=False)
        embed.add_field(name='Language', value='Python', inline=False)
        embed.add_field(name='Version', value='1.4', inline=False)
        embed.add_field(name='GitHub', value='https://github.com/davidracovan/discord-bots')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))