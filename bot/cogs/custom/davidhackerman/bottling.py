import random

import discord
from discord.ext import commands

from bot.helpers import tools


class Bottling(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message):
        if message.author.id != 796805491186597968:
            if random.randint(1, 300) == 1:
                await message.add_reaction("🍾")
                await message.channel.send(f"{message.author.mention} lol get bottled")
                await self.bot.process_commands(message)


def setup(bot: commands.Bot):
    bot.add_cog(Bottling(bot))
