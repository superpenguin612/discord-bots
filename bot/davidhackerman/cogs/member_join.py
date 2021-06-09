import discord
from discord.ext import commands
from bot.helpers import tools


class MemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        print("bru")
        guild = member.guild
        if guild.id == 852039928589713429:
            role = guild.get_role(852047902024400957)
            try:
                await member.add_roles(role)
            except:
                pass


def setup(bot: commands.Bot):
    bot.add_cog(MemberJoin(bot))
