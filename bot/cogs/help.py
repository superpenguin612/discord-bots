import discord
from discord.ext import commands
from bot.helpers import tools

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.group()
    # async def help(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         embed = tools.create_embed(ctx, 'Bot Commands', desc=f"Visit {ctx.prefix}about to see more information about the bot.")
    #         embed.add_field(name='Fun Commands', value=f'`{ctx.prefix}help fun`', inline=False)
    #         embed.add_field(name='Informational Commands', value=f'`{ctx.prefix}help info`', inline=False)
    #         embed.add_field(name='School Commands', value=f'`{ctx.prefix}help school`', inline=False)
    #         embed.add_field(name='Suggestions Commands', value=f'`{ctx.prefix}help suggestions`', inline=False)
    #         await ctx.send(embed=embed)

    # @help.command(name='fun')
    # async def _fun(self, ctx):
    #     embed = tools.create_embed(ctx, 'Fun Commands')
    #     for command in self.bot.get_cog('Fun').get_commands():
    #         embed.add_field(name=f'{ctx.prefix}{command.name} {command.signature}', value=command.help, inline=False)
    #     await ctx.send(embed=embed)

    # @help.command(name='info')
    # async def _info(self, ctx):
    #     embed = tools.create_embed(ctx, 'Informational Commands')
    #     for command in self.bot.get_cog('Info').get_commands():
    #         embed.add_field(name=f'{ctx.prefix}{command.name} {command.signature}', value=command.help, inline=False)
    #     await ctx.send(embed=embed)

    # @help.command(name='school')
    # async def _school(self, ctx):
    #     embed = tools.create_embed(ctx, 'School Commands')
    #     for command in self.bot.get_cog('School').get_commands():
    #         embed.add_field(name=f'{ctx.prefix}{command.name} {command.signature}', value=command.help, inline=False)
    #     await ctx.send(embed=embed)

    # @help.command(name='suggestions')
    # async def _suggestions(self, ctx):
    #     embed = tools.create_embed(ctx, 'Suggestions Commands')
    #     for command in self.bot.get_cog('Suggestions').get_commands():
    #         embed.add_field(name=f'{ctx.prefix}{command.name} {command.signature}', value=command.help, inline=False)
    #     await ctx.send(embed=embed)