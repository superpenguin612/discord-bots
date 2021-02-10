import discord
from discord.ext import commands
from bot.helpers import tools
import json
from datetime import date,datetime,time,timedelta
from bot.helpers import classschedule

class School(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _register(self, user: str, blue_day_lunch, gold_day_lunch, cohort):
        with open('bot/helpers/school.json', 'r') as f:
            school_dict = json.load(f)
        if user not in school_dict:
            with open('bot/helpers/school.json', 'w') as f:
                school_dict[user] = {
                    'blue_day_lunch': blue_day_lunch.upper(),
                    'gold_day_lunch': gold_day_lunch.upper(),
                    'cohort': cohort.lower()
                }
                json.dump(school_dict, f)

    def _register_class(self, user_id, class_type: str, class_name):
        with open('bot/helpers/school.json', 'r') as f:
            school_dict = json.load(f)
        if str(user_id) not in school_dict:
            with open('bot/helpers/school.json', 'w') as f:
                if not school_dict[str(user_id)]['classes']:
                    school_dict[str(user_id)]['classes'] = {}
                school_dict[str(user_id)]['classes'][class_type] = class_name
                json.dump(school_dict, f)

    def _registration_checks(self, ctx):
        with open('bot/helpers/school.json', 'r') as f:
            school_dict = json.load(f)
        return str(ctx.author.id) in school_dict
    
    def _class_registration_checks(self, ctx, class_type):
        with open('bot/helpers/school.json', 'r') as f:
            school_dict = json.load(f)
        return str(ctx.author.id) in school_dict

    def _get_users_dict(self):
        with open('bot/helpers/school.json', 'r') as f: 
            school_dict = json.load(f)
        return school_dict

    def _get_user_info(self, user: str):
        with open('bot/helpers/school.json', 'r') as f: 
            school_dict = json.load(f)
        return school_dict[user]
    
    def _set_users_dict(self, school_dict):
        with open('bot/helpers/school.json', 'w') as f:
            json.dump(school_dict, f)
    
    @commands.command()
    async def register(self, ctx, blue_day_lunch, gold_day_lunch, cohort):
        """Example: `c?register B D greyhound`
        Allows you to register details with the bot to get personalized responses.
        All three values are required.
        Other commands will currently not work without registration.
        """
        self._register(ctx.author.id, blue_day_lunch, gold_day_lunch, cohort)
        desc = f'{ctx.author.mention}, you have been registered.'
        embed = tools.create_embed(ctx, 'User Registration', desc=desc)
        embed.add_field(name='Blue Day Lunch', value=blue_day_lunch, inline=False)
        embed.add_field(name='Gold Day Lunch', value=gold_day_lunch, inline=False)
        embed.add_field(name='Cohort', value=cohort, inline=False)
        await ctx.send(embed=embed)
        
    # @commands.command(name='registerclass')
    # async def register_class(self, ctx, class_type, class_name):
    #     self._register_class(ctx.author.id, class_type.lower(), class_name)
    #     desc = f'{ctx.author.mention}, you have been registered.'
    #     embed = tools.create_embed(ctx, 'Class Registration', desc=desc)
    #     embed.add_field(name=class_type, value=class_name, inline=False)
    #     await ctx.send(embed=embed)
        
    @commands.command()
    async def schoolday(self, ctx, all=None):
        """Tells you information about today (Blue/Gold, In Person/Virtual, Late Start, weekends, breaks, etc.).
        The `all` argument is optional, and it will display information for both cohorts.
        """
        if all != 'all':
            if not self._registration_checks(ctx):
                embed = tools.create_embed(ctx, 'Error', desc="You must be registered to use this command. Try appending `all` to the command, or registering.")
                await ctx.send(embed=embed)
                return
            user_info = self._get_user_info(str(ctx.author.id))
            school_day = classschedule.get_current_day(user_info)
            desc = f'Today is {datetime.now().strftime("%A, %B %d, %Y")}.\nYour Cohort ({user_info["cohort"].title()}): {school_day}'
            embed = tools.create_embed(ctx, 'School Day', desc)
            await ctx.send(embed=embed)
        else:
            school_day = classschedule.get_current_day()
            desc = f'Today is {datetime.now().strftime("%A, %B %d, %Y")}.\nCarmel Cohort: {school_day[0]}.\nGreyhound Cohort: {school_day[1]}.\n'
            embed = tools.create_embed(ctx, 'School Day', desc)
            await ctx.send(embed=embed)

    @commands.command()
    async def schoolweek(self, ctx, all=None):
        """Tells you information about the next seven days.
        The `all` argument is optional, and it will display information for both cohorts.
        """
        if all != 'all':
            if not self._registration_checks(ctx):
                embed = tools.create_embed(ctx, 'Error', desc="You must be registered to use this command. Try appending `all` to the command, or registering.")
                await ctx.send(embed=embed)
                return
            user_info = self._get_user_info(str(ctx.author.id))
            school_week = classschedule.get_week(user_info)
            desc = '\n'.join(school_week)
            embed = tools.create_embed(ctx, 'School Week', desc)
            await ctx.send(embed=embed)
        else:
            school_weeks = classschedule.get_week()
            embed = tools.create_embed(ctx, 'School Week')
            value1='\n'.join(school_weeks[0])
            embed.add_field(name='Carmel Cohort', value=value1)
            value2='\n'.join(school_weeks[1])
            embed.add_field(name='Greyhound Cohort', value=value2)
            await ctx.send(embed=embed)
        
    @commands.command()
    async def schooldate(self, ctx, date, all=None):
        """Tells you information about a specified date.
        The `date` argument is required, and must be in the form `mm/dd/yyyy`.
        The `all` argument is optional, and it will display information for both cohorts.
        """
        if all != 'all':
            if not self._registration_checks(ctx):
                embed = tools.create_embed(ctx, 'Error', desc="You must be registered to use this command. Try appending `all` to the command, or registering.")
                await ctx.send(embed=embed)
                return
            user_info = self._get_user_info(str(ctx.author.id))
            school_day = classschedule.get_day(date, user_info)
            desc = f'Your Cohort ({user_info["cohort"].title()}): {school_day}'
            embed = tools.create_embed(ctx, 'School Day', desc)
            await ctx.send(embed=embed)
        else:
            school_day = classschedule.get_day(date)
            desc = f'Carmel Cohort: {school_day[0]}\nGreyhound Cohort: {school_day[1]}\n'
            embed = tools.create_embed(ctx, 'School Day', desc)
            await ctx.send(embed=embed)