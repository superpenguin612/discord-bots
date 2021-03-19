import discord
from discord.ext import commands, tasks
from bot.helpers import tools
from datetime import datetime

class Tasks(commands.Cog, name='tasks'):
    def __init__(self, bot):
        self.bot = bot

    def create_daily_report():
        pass

    @tasks.loop(seconds=1.0)
    async def daily_report(self):
        if datetime.now().strftime("%H:%M:%S") == "07:00:00":
            pass