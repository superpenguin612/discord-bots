import discord
from discord.ext import commands
from bot.helpers import tools
import datetime
import time

class Moderation(commands.Cog, name='moderation'):
    def __init__(self, bot):
        self.bot = bot

    async def get_records_by_server_id(self, server_id):
        return await self.bot.db.fetch('SELECT * FROM punishments WHERE server_id=$1', str(server_id))

    async def get_record_by_id(self, id):
        return await self.bot.db.fetchrow('SELECT * FROM punishments WHERE id=$1;', str(id))

    async def add_record(self, server_id, type, user_id, punisher_id, reason):
        return await self.bot.db.fetchrow('INSERT INTO punishments (server_id, type, user_id, punisher_id, reason) VALUES ($1, $2, $3, $4, $5) RETURNING *;',
            server_id, type, user_id, punisher_id, reason)

    @commands.command(
        name='purge',
        brief='Purge messages from the current channel.'
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, num: int):
        """Purge messages from the current channel.
        **Usage**
        `_prefix_purge <num>`
        **Parameters**
        `<num>`: The number of messages to purge.
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Manage Messages
        **Examples**
        `_prefix_warn @superpenguin612 stop being so bad smh`
        `_prefix_warn @superpenguin612 hehe admin abuse`
        `_prefix_ban 688530998920871969 bruh`
        """
        msgs = []
        async for x in ctx.channel.history(limit=num):
            msgs.append(x)
        await ctx.channel.delete_messages(msgs)
        embed = tools.create_embed(ctx, 'Message Purge', f'{num} messages deleted.')
        await ctx.send(embed=embed)
 
    @commands.command(
        name='warn',
        brief='Warn a user.'
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.User, *, reason=None):
        """Warn a user. This will get logged as a `warn`.
        **Usage**
        `_prefix_warn <user> [reason]`
        **Parameters**
        `<user>`: A user mention or their ID.
        `[reason]`: The reason for their warn.
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Manage Messages
        **Examples**
        `_prefix_warn @superpenguin612 stop being so bad smh`
        `_prefix_warn @superpenguin612 hehe admin abuse`
        `_prefix_ban 688530998920871969 bruh`
        """
        punishment_record = await self.add_record(str(ctx.guild.id), 'warn', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Warn', desc=f'{user} has been warned.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'], inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(
        name='kick',
        brief='Kick a user from the server.'
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.User, *, reason=None):
        """Kick a user from the server. This will get logged as a `kick` in punishment logs.
        **Usage**
        `_prefix_kick <user> [reason]`
        **Parameters**
        `<user>`: A user mention or their ID.
        `[reason]`: The reason for their kick.
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Kick Members
        **Examples**
        `_prefix_kick @superpenguin612 so bad`
        `_prefix_kick @superpenguin612 stop spamming gnoob`
        `_prefix_kick 688530998920871969 nerd`
        """
        await ctx.guild.kick(user, reason=reason)
        punishment_record = await self.add_record(str(ctx.guild.id), 'kick', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Kick', desc=f'{user} has been kicked.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'], inline=False)
        await ctx.send(embed=embed)
        
    @commands.command(
        name='ban',
        brief='Ban a user from the server.'
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=None):
        """Ban a user from the server. This command also acts as a hackban (you can ban after the user leaves the guild). 
        This will get logged as a `ban` in punishment logs.
        **Usage**
        `_prefix_ban <user> [reason]`
        **Parameters**
        `<user>`: A user mention or their ID.
        `[reason]`: The reason for their ban.
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Ban Members
        **Examples**
        `_prefix_ban @superpenguin612 git gud n00b`
        `_prefix_ban @superpenguin612 being better than the owner`
        `_prefix_ban 688530998920871969 oh so you left the server before i could ban you? get banned anyway :)`
        """
        await ctx.guild.ban(user, reason=reason)
        punishment_record = await self.add_record(str(ctx.guild.id), 'ban', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Ban', desc=f'{user} has been banned.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'],inline=False)
        await ctx.send(embed=embed)

    @commands.command(
        name='mute', 
        brief='Mute a member.'
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, user: discord.Member, time, *, reason=None):
        """Give a user the role selected in settings as the muted role. 
        By default, this restricts the user from typing in channels and adding reactions
        but still allows them to view messages. This will get logged as a `mute` in the punishment logs.
        **Usage**
        `_prefix_mute <user> <time> [reason]`
        **Parameters**
        `<user>`: A user mention or their ID.
        `<time>`: The amount of time the mute should last. Acceptable units of time are `d` (days), `h` (hours), `m` (minutes), `s` (seconds). If you do not provide a unit, this will default to minutes. For a manual mute, use 0 as time.
        `[reason]`: The reason for their mute.
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Manage Roles
        **Examples**
        `_prefix_mute @superpenguin612 5m being too cool`
        `_prefix_mute @superpenguin612 0 get muted lol`
        `_prefix_mute @superpenguin612 5d spamming`
        """
        await user.add_roles(ctx.guild.get_role(809169133232717890))
        punishment_record = await self.add_record(str(ctx.guild.id), 'mute', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Mute', desc=f'{user} has been muted.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'],inline=False)
        await ctx.send(embed=embed)

    @commands.command(
        name='unmute',
        brief='Unmute a member.'
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, user: discord.Member):
        """Unmute a member. This removes the role selected as the muted role. 
        If the original mute had a time attached, this will override that.
        **Usage**
        `_prefix_unmute <user>`
        **Parameters**
        `<user>`: A user mention or their ID.
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Manage Roles
        **Examples**
        `_prefix_unmute @superpenguin612`
        `_prefix_unmute 688530998920871969`
        """
        await user.remove_roles(ctx.guild.get_role(809169133232717890))
        embed = tools.create_embed(ctx, 'User Unmute', desc=f'{user} has been unmuted.')
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def punishments(self, ctx):
        """Lists all the punishments in the server, with IDs for each.
        These include bans, warns, kicks, and mutes.
        **Usage**
        `_prefix_punishments`
        **Parameters**
        None
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Manage Messages
        **Examples**
        `_prefix_punishments`
        """
        records = await self.get_records_by_server_id(str(ctx.guild.id))
        embed = tools.create_embed(ctx, 'Server Punishments')
        for record in records:
            user = await self.bot.fetch_user(record["user_id"])
            val = f'User: {user.mention} | Type: {record["type"]} | Timestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
            embed.add_field(name=record["id"], value=val)
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def punishmentinfo(self, ctx, id):
        """View info about a specific punishment by unique ID.
        **Usage**
        `_prefix_punishmentinfo <id>`
        **Parameters**
        `<id>`: The unique ID associated with the punishment.
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Manage Messages
        **Examples**
        `_prefix_unmute @superpenguin612`
        `_prefix_unmute 688530998920871969`
        """
        record = await self.get_record_by_id(id)
        if not record:
            embed = tools.create_error_embed(ctx, 'Punishment not found. Please check the ID you gave.')
            await ctx.send(embed=embed)
        else:
            embed = tools.create_embed(ctx, 'Punishment Lookup')
            embed.add_field(name='ID', value=record['id'])
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