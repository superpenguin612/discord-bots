import discord
from discord.ext import commands
from bot import tools

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, num: int):
        msgs = []
        async for x in ctx.channel.history(limit=num):
            msgs.append(x)
        await ctx.channel.delete_messages(msgs)
        embed = tools.create_embed(ctx, 'Message Purge', f'{num} messages deleted.')
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.User, reason: str=None):
        await ctx.guild.kick(user, reason=reason)
        desc = f'{user} has been kicked.'
        if reason:
            desc += f'\nReason: {reason}'
        embed = tools.create_embed(ctx, 'User Kick', description=desc)
        await ctx.send(embed=embed)
        
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, reason: str=None):
        await ctx.guild.ban(user, reason=reason)
        desc = f'{user} has been banned.'
        if reason:
            desc += f'\nReason: {reason}'
        embed = tools.create_embed(ctx, 'User Ban', description=desc)
        await ctx.send(embed=embed)