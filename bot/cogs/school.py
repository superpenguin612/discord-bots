import discord
from discord.ext import commands
from bot.helpers import tools
import json
from datetime import date,datetime,time,timedelta

class School(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("bot/helpers/school_info.json") as f:
            self.SCHOOL_INFO_DICT = json.load(f)

    # def _register_class(self, user_id, class_type: str, class_name):
    #     with open('bot/helpers/school.json', 'r') as f:
    #         school_dict = json.load(f)
    #     if str(user_id) not in school_dict:
    #         with open('bot/helpers/school.json', 'w') as f:
    #             if not school_dict[str(user_id)]['classes']:
    #                 school_dict[str(user_id)]['classes'] = {}
    #             school_dict[str(user_id)]['classes'][class_type] = class_name
    #             json.dump(school_dict, f)

    async def get_record(self, user_id):
        return await self.bot.db.fetchrow('SELECT * FROM registrations WHERE user_id=$1', str(user_id))
    
    @commands.command()
    async def register(self, ctx, blue_lunch, gold_lunch, cohort):
        """Example: `c?register B D greyhound`
        Allows you to register details with the bot to get personalized responses.
        All three values are required.
        Other commands will currently not work without registration.
        """
        await self.bot.db.execute('INSERT INTO registrations (user_id, blue_lunch, gold_lunch, cohort)'
            'VALUES ($1, $2, $3, $4)', str(ctx.author.id), blue_lunch.upper(), gold_lunch.upper(), cohort.lower())
        desc = f'{ctx.author.mention}, you have been registered.'
        embed = tools.create_embed(ctx, 'User Registration', desc=desc)
        embed.add_field(name='Blue Day Lunch', value=blue_lunch, inline=False)
        embed.add_field(name='Gold Day Lunch', value=gold_lunch, inline=False)
        embed.add_field(name='Cohort', value=cohort.title(), inline=False)
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
            user_info = await self.get_record(ctx.author.id)
            if not user_info:
                embed = tools.create_error_embed(ctx, "You must be registered to use this command. Try appending `all` to the command, or registering.")
                await ctx.send(embed=embed)
                return
            school_day = self.SCHOOL_INFO_DICT["days"][user_info["cohort"]][datetime.now().strftime("%m/%d/%Y")]
            desc = f'Today is {datetime.now().strftime("%A, %B %d, %Y")}.\nYour Cohort ({user_info["cohort"].title()}): {school_day}'
            embed = tools.create_embed(ctx, 'School Day', desc)
            await ctx.send(embed=embed)
        else:
            school_days = self.SCHOOL_INFO_DICT["days"]["carmel"][datetime.now().strftime("%m/%d/%Y")], self.SCHOOL_INFO_DICT["days"]["greyhound"][datetime.now().strftime("%m/%d/%Y")]
            desc = f'Today is {datetime.now().strftime("%A, %B %d, %Y")}.'
            embed = tools.create_embed(ctx, 'School Day', desc)
            embed.add_field(name='Carmel', value=school_days[0])
            embed.add_field(name='Greyhound', value=school_days[1])
            await ctx.send(embed=embed)

    @commands.command()
    async def schoolweek(self, ctx, all=None):
        """Tells you information about the next seven days.
        The `all` argument is optional, and it will display information for both cohorts.
        """
        if all != 'all':
            user_info = await self.get_record(ctx.author.id)
            if not user_info:
                embed = tools.create_embed(ctx, 'Error', desc="You must be registered to use this command. Try appending `all` to the command, or registering.")
                await ctx.send(embed=embed)
                return
            school_week = []
            for i in range (7):
                target_day = datetime.now() + timedelta(days = i + 1)
                school_week.append(target_day.strftime("%a, %b %d, %Y: ")
                    + self.SCHOOL_INFO_DICT["days"][user_info["cohort"]][target_day.strftime("%m/%d/%Y")])
            desc = '\n'.join(school_week)
            embed = tools.create_embed(ctx, 'School Week', desc)
            await ctx.send(embed=embed)
        else:
            school_weeks = [[],[]]
            for i in range (7):
                target_day = datetime.now() + timedelta(days = i + 1)
                school_weeks[0].append(target_day.strftime("%a, %b %d, %Y: ")
                    + self.SCHOOL_INFO_DICT["days"]['carmel'][target_day.strftime("%m/%d/%Y")])
                school_weeks[1].append(target_day.strftime("%a, %b %d, %Y: ")
                    + self.SCHOOL_INFO_DICT["days"]['greyhound'][target_day.strftime("%m/%d/%Y")])
            embed = tools.create_embed(ctx, 'School Week')
            embed.add_field(name='Carmel Cohort', value='\n'.join(school_weeks[0]))
            embed.add_field(name='Greyhound Cohort', value='\n'.join(school_weeks[1]))
            await ctx.send(embed=embed)
        
    @commands.command()
    async def schooldate(self, ctx, date, all=None):
        """Tells you information about a specified date.
        The `date` argument is required, and must be in the form `mm/dd/yyyy`.
        The `all` argument is optional, and it will display information for both cohorts.
        """
        if all != 'all':
            user_info = await self.get_record(ctx.author.id)
            if not user_info:
                embed = tools.create_embed(ctx, 'Error', desc="You must be registered to use this command. Try appending `all` to the command, or registering.")
                await ctx.send(embed=embed)
                return
            school_date = self.SCHOOL_INFO_DICT["days"][user_info["cohort"]][date]
            desc = f'Your Cohort ({user_info["cohort"].title()}): {school_date}'
            embed = tools.create_embed(ctx, 'School Day', desc)
            await ctx.send(embed=embed)
        else:
            school_dates = self.SCHOOL_INFO_DICT["days"]["carmel"][date], self.SCHOOL_INFO_DICT["days"]["greyhound"][date]
            desc = f'Carmel Cohort: {school_dates[0]}\nGreyhound Cohort: {school_dates[1]}\n'
            embed = tools.create_embed(ctx, 'School Date', desc)
            embed.add_field(name='Carmel', value=school_dates[0])
            embed.add_field(name='Greyhound', value=school_dates[1])
            await ctx.send(embed=embed)