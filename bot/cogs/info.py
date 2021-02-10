import discord
from discord.ext import commands
from bot import tools
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
        author1 = await ctx.guild.fetch_member(688530998920871969)
        author2 = await ctx.guild.fetch_member(654874992672112650)
        embed.add_field(name='Authors', value=f'{author1.mention} and {author2.mention}', inline=False)
        embed.add_field(name='Language', value='Python', inline=False)
        embed.add_field(name='Version', value='1.0', inline=False)
        await ctx.send(embed=embed)