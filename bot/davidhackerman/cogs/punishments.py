import discord
from discord.ext import commands
from bot.helpers import tools
import datetime
import time

class Punishments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_all_records(self):
        return await self.bot.db.fetch('SELECT * FROM punishments;')

    async def get_record_by_id(self, pid):
        return await self.bot.db.fetchrow('SELECT * FROM punishments WHERE punishment_id=$1;', str(pid))

    async def add_record(self, server_id, type, user_id, punisher_id, reason):
        return await self.bot.db.fetchrow('INSERT INTO punishments (server_id, type, user_id, punisher_id, reason) VALUES ($1, $2, $3, $4, $5) RETURNING *;',
            server_id, type, user_id, punisher_id, reason)

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
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.User, *, reason=None):
        punishment_record = await self.add_record(str(ctx.guild.id), 'warn', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Warn', desc=f'{user} has been warned.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['punishment_id'], inline=False)
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.User, *, reason=None):
        await ctx.guild.kick(user, reason=reason)
        punishment_record = await self.add_record(str(ctx.guild.id), 'kick', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Kick', desc=f'{user} has been kicked.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['punishment_id'], inline=False)
        await ctx.send(embed=embed)
        
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason: str=None):
        await ctx.guild.ban(user, reason=reason)
        punishment_record = await self.add_record(str(ctx.guild.id), 'ban', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Ban', desc=f'{user} has been banned.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['punishment_id'],inline=False)
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def punishments(self, ctx):
        records = await self.get_all_records()
        embed = tools.create_embed(ctx, 'Server Punishments')
        for record in records:
            user = await self.bot.fetch_user(record["user_id"])
            val = f'User: {user.mention}\nType: {record["type"]}\nTimestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
            embed.add_field(name=f'PID: {record["punishment_id"]}', value=val)
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def punishmentinfo(self, ctx, id):
        record = await self.get_record_by_id(id)
        if not record:
            embed = tools.create_error_embed(ctx, 'Punishment not found. Please check the ID you gave.')
            await ctx.send(embed=embed)
        else:
            embed = tools.create_embed(ctx, 'Punishment Lookup')
            embed.add_field(name='PID', value=record['punishment_id'])
            embed.add_field(name='Type', value=record['type'])
            if record['duration']:
                embed.add_field(name='Duration', value=time.strftime('%Mm %Ss', time.gmtime(round(record['duration']))))
            embed.add_field(name='Offender', value=int(record['user_id']))
            embed.add_field(name='Punisher', value=int(record['punisher_id']))
            embed.add_field(name='Date', value=record['timestamp'].strftime('%b %-d %Y at %-I:%-M %p'))
            if record['reason']:
                embed.add_field(name='Reason', value=record['reason'])
            else:
                embed.add_field(name='Reason', value='None')
            await ctx.send(embed=embed)