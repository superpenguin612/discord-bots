import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType
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
    
    # @commands.command()
    # async def register(self, ctx, blue_lunch, gold_lunch, cohort):
    #     """Example: `c?register B D greyhound`
    #     Allows you to register details with the bot to get personalized responses.
    #     All three values are required.
    #     Other commands will currently not work without registration.
    #     """
    #     await self.bot.db.execute('INSERT INTO registrations (user_id, blue_lunch, gold_lunch, cohort)'
    #         'VALUES ($1, $2, $3, $4)', str(ctx.author.id), blue_lunch.upper(), gold_lunch.upper(), cohort.lower())
    #     desc = f'{ctx.author.mention}, you have been registered.'
    #     embed = tools.create_embed(ctx, 'User Registration', desc=desc)
    #     embed.add_field(name='Blue Day Lunch', value=blue_lunch, inline=False)
    #     embed.add_field(name='Gold Day Lunch', value=gold_lunch, inline=False)
    #     embed.add_field(name='Cohort', value=cohort.title(), inline=False)
    #     await ctx.send(embed=embed)
        
    # @commands.command(name='registerclass')
    # async def register_class(self, ctx, class_type, class_name):
    #     self._register_class(ctx.author.id, class_type.lower(), class_name)
    #     desc = f'{ctx.author.mention}, you have been registered.'
    #     embed = tools.create_embed(ctx, 'Class Registration', desc=desc)
    #     embed.add_field(name=class_type, value=class_name, inline=False)
    #     await ctx.send(embed=embed)
        
    
    @cog_ext.cog_slash(
        name='schoolday',
        description='Get information about a specific school day. Defaults to today.',
        options=[
            create_option(
                name='cohort',
                description='The cohort to get the school day for.',
                option_type=SlashCommandOptionType.STRING,
                required=False,
                choices=[
                    create_choice(
                        name='carmel',
                        value='carmel'
                    ),
                    create_choice(
                        name='greyhound',
                        value='greyhound'
                    ),
                ]
            ),
            create_option(
                name='date',
                description='The optional date to look up. Must be in the form MM/DD/YYYY.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ],
    )
    async def schoolday(self, ctx, cohort=None, date=None):
        """Tells you information about today (Blue/Gold, In Person/Virtual, Late Start, weekends, breaks, etc.).
        The `all` argument is optional, and it will display information for both cohorts.
        """
        if cohort:
            if date:
                school_day = self.SCHOOL_INFO_DICT["days"][cohort][date]
            else:
                school_day = self.SCHOOL_INFO_DICT["days"][cohort][datetime.now().strftime("%m/%d/%Y")]
            desc = f'Today is {datetime.now().strftime("%A, %B %d, %Y")}.\n {cohort.upper()} Cohort: {school_day}'
            embed = tools.create_embed(ctx, 'School Day', desc)
            await ctx.send(embed=embed)
        else:
            if date:
                school_days = self.SCHOOL_INFO_DICT["days"]["carmel"][date], self.SCHOOL_INFO_DICT["days"]["greyhound"][date]
            else:
                school_days = self.SCHOOL_INFO_DICT["days"]["carmel"][datetime.now().strftime("%m/%d/%Y")], self.SCHOOL_INFO_DICT["days"]["greyhound"][datetime.now().strftime("%m/%d/%Y")]
            desc = f'Today is {datetime.now().strftime("%A, %B %d, %Y")}.'
            embed = tools.create_embed(ctx, 'School Day', desc)
            embed.add_field(name='Carmel', value=school_days[0])
            embed.add_field(name='Greyhound', value=school_days[1])
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='schoolweek',
        description='Get information for the rest of the school week.',
        options=[
            create_option(
                name='cohort',
                description='The cohort to get the information for.',
                option_type=SlashCommandOptionType.STRING,
                required=False,
                choices=[
                    create_choice(
                        name='carmel',
                        value='carmel'
                    ),
                    create_choice(
                        name='greyhound',
                        value='greyhound'
                    ),
                ]
            ),
        ],
    )
    async def schoolweek(self, ctx, cohort=None):
        """Tells you information about the next seven days.
        The `all` argument is optional, and it will display information for both cohorts.
        """
        if cohort:
            school_week = []
            for i in range (7):
                target_day = datetime.now() + timedelta(days = i + 1)
                school_week.append(target_day.strftime("%a, %b %d, %Y: ")
                    + self.SCHOOL_INFO_DICT["days"][cohort][target_day.strftime("%m/%d/%Y")])
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

    
    # --------------------------------------------
    # LEGACY COMMANDS
    # --------------------------------------------

    @commands.command()
    async def schoolday(self, ctx):
        """Tells you information about today (Blue/Gold, In Person/Virtual, Late Start, weekends, breaks, etc.).
        The `all` argument is optional, and it will display information for both cohorts.
        """
        school_days = self.SCHOOL_INFO_DICT["days"]["carmel"][datetime.now().strftime("%m/%d/%Y")], self.SCHOOL_INFO_DICT["days"]["greyhound"][datetime.now().strftime("%m/%d/%Y")]
        desc = f'Today is {datetime.now().strftime("%A, %B %d, %Y")}.'
        embed = tools.create_embed(ctx, 'School Day', desc)
        embed.add_field(name='Carmel', value=school_days[0])
        embed.add_field(name='Greyhound', value=school_days[1])
        await ctx.send(embed=embed)

    @commands.command()
    async def schoolweek(self, ctx):
        """Tells you information about the next seven days.
        The `all` argument is optional, and it will display information for both cohorts.
        """
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
    async def schooldate(self, ctx, date):
        """Tells you information about a specified date.
        The `date` argument is required, and must be in the form `mm/dd/yyyy`.
        The `all` argument is optional, and it will display information for both cohorts.
        """
        school_dates = self.SCHOOL_INFO_DICT["days"]["carmel"][date], self.SCHOOL_INFO_DICT["days"]["greyhound"][date]
        desc = f'Carmel Cohort: {school_dates[0]}\nGreyhound Cohort: {school_dates[1]}\n'
        embed = tools.create_embed(ctx, 'School Date', desc)
        embed.add_field(name='Carmel', value=school_dates[0])
        embed.add_field(name='Greyhound', value=school_dates[1])
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(School(bot))