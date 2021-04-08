import discord
from discord.ext import commands
from bot.helpers import tools
import json
import random


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _registration_checks(self, ctx):
        with open("bot/currency.json", "r") as f:
            currency = json.load(f)
        if str(ctx.author.id) not in currency:
            with open("bot/currency.json", "w") as f:
                currency[str(ctx.author.id)] = 0
                json.dump(currency, f)

    def _get_currency_dict(self, ctx):
        self._registration_checks(ctx)
        with open("bot/currency.json", "r") as f:
            currency = json.load(f)
        return currency

    def _set_currency_dict(self, ctx, currency):
        self._registration_checks(ctx)
        with open("bot/currency.json", "w") as f:
            json.dump(currency, f)

    def increment_coins(self, ctx, coins: int):
        currency = self._get_currency_dict(ctx)
        currency[str(ctx.author.id)] += coins
        self._set_currency_dict(ctx, currency)

    async def command_coins(self, ctx, max_coin_count: int = 5):
        if random.randint(0, 100) >= 80:
            coin_count = random.randint(2, max_coin_count)
            self.increment_coins(ctx, coin_count)
            color = discord.Color.green()
            embed = discord.Embed(
                title="Coins!",
                description=f"Nice! You got {coin_count} coins!",
                color=color,
            )
            await ctx.send(embed=embed)

    @commands.command(aliases=["bal"])
    async def balance(self, ctx):
        """Get your balance."""
        bal = self._get_currency_dict(ctx)
        embed = tools.create_embed(
            ctx, "Balance", f"You have {bal[str(ctx.author.id)]} coins."
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))
