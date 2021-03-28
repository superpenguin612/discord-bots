import discord
from discord.ext import commands, tasks
from bot.helpers import tools
from datetime import datetime, timedelta
import asyncpg
from bot.cogs.settings import Settings

class Tasks(commands.Cog, name='tasks'):
    def __init__(self, bot):
        self.bot = bot
        self.daily_report.start()
        self.timed_unmute.start()

    def create_daily_report():
        pass

    @tasks.loop(seconds=1.0)
    async def daily_report(self):
        if datetime.now().strftime("%H:%M:%S") == "07:00:00":
            pass

    @tasks.loop(seconds=1.0)
    async def timed_unmute(self):
        if hasattr(self.bot, 'db'):
            records = await self.bot.db.fetch('SELECT * FROM moderations WHERE type=\'mute\' AND active')
            for record in records:
                if datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") == (record['timestamp'] + timedelta(seconds=record['duration'])).strftime('%m/%d/%Y %H:%M:%S'):
                    guild = self.bot.get_guild(int(record['server_id']))
                    role = guild.get_role(809169133232717890)
                    user = guild.get_member(int(record['user_id']))
                    await user.remove_roles(role)
                    await self.bot.db.execute('UPDATE moderations SET active=FALSE WHERE id=$1', record['id'])
                    
                    moderation = self.bot.get_cog('moderation')
                    await moderation.add_record(record['server_id'], 'unmute', record['user_id'], str(self.bot.user.id), 'Auto unmute by CHS Bot.')

    @timed_unmute.before_loop
    async def before_timed_unmute(self):
        await self.bot.wait_until_ready()