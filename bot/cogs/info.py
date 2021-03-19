import discord
from discord.ext import commands
from bot.helpers import tools
import random

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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