import discord
from discord.ext import commands
from bot.helpers import tools


class Links(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def safety(self, ctx):
        """Links to Safety Dance."""
        embed = tools.create_embed(
            ctx, "Safety Dance", url="https://www.youtube.com/watch?v=AjPau5QYtYs"
        )
        await ctx.send(embed=embed)
        await self.bot.get_cog("Economy").command_coins(ctx)

    @commands.command()
    async def tainted(self, ctx):
        """Links to Tainted Love."""
        embed = tools.create_embed(
            ctx, "Tainted Love", url="https://www.youtube.com/watch?v=ZcyCQLewj10"
        )
        await ctx.send(embed=embed)
        await self.bot.get_cog("Economy").command_coins(ctx)

    @commands.command()
    async def goldenhair(self, ctx):
        """Links to Sister Golden Hair."""
        embed = tools.create_embed(
            ctx, "Sister Golden Hair", url="https://www.youtube.com/watch?v=XIycEe59Auc"
        )
        await ctx.send(embed=embed)
        await self.bot.get_cog("Economy").command_coins(ctx)


def setup(bot):
    bot.add_cog(Links(bot))
