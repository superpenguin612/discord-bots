import discord
from discord.ext import commands
from bot.helpers import tools
import random

class Bottling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name='on_message')
    async def on_message(self, message):
        if message.author.id != 796805491186597968:
            if random.randint(1,1) == 1:
                await message.add_reaction('🍾')
                await message.channel.send(f'{message.author.mention} lol get bottled')
                await self.bot.process_commands(message)