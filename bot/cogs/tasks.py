import discord
from discord.ext import commands, tasks
from bot.helpers import tools
from datetime import datetime, timedelta
import asyncpg
import json
import datetime
from .search import Search

class Tasks(commands.Cog, name='tasks'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.daily_report.start()
        self.timed_unmute.start()

    async def create_daily_report(self):
        with open("bot/helpers/school_info.json") as f:
            self.SCHOOL_INFO_DICT = json.load(f)

        embed = discord.Embed(title='Daily Report', description='Good morning everyone! Here\'s your report for the day.')
        school_days = self.SCHOOL_INFO_DICT["days"]["carmel"][datetime.now().strftime("%m/%d/%Y")], self.SCHOOL_INFO_DICT["days"]["greyhound"][datetime.now().strftime("%m/%d/%Y")]
        
        school_day_val = (
            f'Today is {datetime.now().strftime("%A, %B %d, %Y")}.\n'
            f'It\'s a {school_days[0]} for the Carmel cohort, and a {school_days[1]} for the Greyhound cohort.'
            'To view more details, run `/schoolday` or `c?schoolday` (legacy command).'
        )
        embed.add_field(name='School Day', value=school_day_val)
        food_items = await Search.get_mv_list()
        lunch_menu_val = (
            '*Freshmen Center*\n' + 
            '\n'.join([f'{x} - {x["item_Name"]}' for x in food_items[0]]) +
            '\n*Greyhound Station*\n' + 
            '\n'.join([f'{x} - {x["item_Name"]}' for x in food_items[1]]) +
            '\n*Main Cafeteria*\n' +
            '\n'.join([f'{x} - {x["item_Name"]}' for x in food_items[2]]) 
        )
        embed.add_field(name='Lunch Menu', value=lunch_menu_val)
        return embed

    @tasks.loop(seconds=1.0)
    async def daily_report(self):
        if datetime.now().strftime("%H:%M:%S") == "07:00:00":
            guild = self.bot.get_guild(809169133086048257)
            channel = guild.get_channel(819546169985597440)
            role = guild.get_role(821386697727410238)

            embed = await self.create_daily_report()
            msg = await channel.send(content=role.mention, embed=embed)
            await msg.publish()

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