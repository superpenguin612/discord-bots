import discord
from discord.ext import commands, tasks
from bot.helpers import tools
from datetime import datetime, timedelta
import asyncpg
import json
from datetime import datetime, date
from .search import Search
import random


class Tasks(commands.Cog, name="tasks"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.daily_report.start()
        self.timed_unmute.start()
        self.ping_david.start()

    async def create_daily_report(self, guild: discord.Guild) -> discord.Embed:
        with open("bot/helpers/school_info.json") as f:
            self.SCHOOL_INFO_DICT = json.load(f)

        embed = discord.Embed(
            title="Daily Report",
            description="Good morning everyone! Here's your report for the day.",
        )
        school_day = self.SCHOOL_INFO_DICT["days"][datetime.now().strftime("%m/%d/%Y")]

        school_day_val = (
            f'Today is {datetime.now().strftime("%A, %B %d, %Y")}.\n'
            f"It's a {school_day} today.\n"
            "(To view more details, run `/schoolday` or `c?schoolday`)"
        )
        embed.add_field(name="School Day", value=school_day_val, inline=False)
        search = self.bot.get_cog("search")
        food_items = await search.get_mv_list(date.today().strftime("%m-%d-%Y"))
        lunch_menu_val_1 = "\n".join(
            [
                f'`{index}` - {val["item_Name"]}'
                for index, val in enumerate(food_items[0])
            ]
        )
        lunch_menu_val_3 = (
            "\n".join(
                [
                    f'`{index}` - {val["item_Name"]}'
                    for index, val in enumerate(food_items[2])
                ]
            )
            + "\n\n(To view more details, run `/mealviewer item <cafeteria> <item_id>`. The item ID is the number that appears to the right of the food item.)"
        )
        embed.add_field(
            name="Freshmen Center/Greyhound Station Lunch Menu",
            value=lunch_menu_val_1,
            inline=False,
        )
        embed.add_field(
            name="Main Cafeteria Lunch Menu", value=lunch_menu_val_3, inline=False
        )

        number_of_days = (
            datetime.strptime("05/26/2022", "%m/%d/%Y") - datetime.now()
        ).days + 1
        embed.add_field(name="Days Until The End of School", value=number_of_days)
        number_of_school_days = 0
        for day in range(number_of_days):
            day = self.SCHOOL_INFO_DICT["days"][
                (datetime.now() + timedelta(days=day)).strftime("%m/%d/%Y")
            ]
            if any([day_type in day.lower() for day_type in ["blue", "gold"]]):
                number_of_school_days += 1
        embed.add_field(
            name="School Days Until The End of School", value=number_of_school_days
        )

        embed.set_footer(
            text="Note: This report is for informational purposes only. Although we will try to make sure this report is up to date, we cannot guarantee it."
        )
        embed.set_thumbnail(
            url="https://resources.finalsite.net/images/f_auto,q_auto/v1540226230/ccsk12inus/awfkuopbc2f6uupyira9/CarmelHighSchoolLogo.jpg"
        )
        return embed

    # @commands.command()
    # @commands.has_permissions(administrator=True)
    # async def testdailyreport(self, ctx: commands.Context):
    #     embed = await self.create_daily_report(ctx.guild)
    #     await ctx.send(embed=embed)

    @tasks.loop(seconds=1.0)
    async def daily_report(self):
        if datetime.utcnow().strftime("%H:%M:%S") == "12:00:00":
            guild = self.bot.get_guild(809169133086048257)
            channel = guild.get_channel(819546169985597440)
            role = guild.get_role(821386697727410238)

            embed = await self.create_daily_report(guild)
            msg = await channel.send(content=role.mention, embed=embed)
            await msg.publish()

    @tasks.loop(seconds=1.0)
    async def ping_david(self):
        if datetime.utcnow().strftime("%H:%M:%S") == "1:11:00":
            guild = self.bot.get_guild(809169133086048257)
            channel = guild.get_channel(826458834989219870)
            msg = await channel.send("<@!688530998920871969>")

    @tasks.loop(seconds=1.0)
    async def timed_unmute(self):
        if hasattr(self.bot, "db"):
            records = await self.bot.db.fetch(
                "SELECT * FROM moderations WHERE type='mute' AND active"
            )
            for record in records:
                if datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") == (
                    record["timestamp"] + timedelta(seconds=record["duration"])
                ).strftime("%m/%d/%Y %H:%M:%S"):
                    guild = self.bot.get_guild(int(record["server_id"]))
                    role = guild.get_role(809169133232717890)
                    user = guild.get_member(int(record["user_id"]))
                    await user.remove_roles(role)
                    await self.bot.db.execute(
                        "UPDATE moderations SET active=FALSE WHERE id=$1", record["id"]
                    )

                    await self.bot.db.execute(
                        "INSERT INTO moderations (server_id, type, user_id, moderator_id, reason, duration) VALUES ($1, $2, $3, $4);",
                        record["server_id"],
                        "unmute",
                        record["user_id"],
                        str(self.bot.user.id),
                        "Automatic unmute by the bot.",
                    )

    @timed_unmute.before_loop
    async def before_timed_unmute(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(Tasks(bot))
