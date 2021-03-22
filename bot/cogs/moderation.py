from itertools import accumulate
import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import datetime
import time

class Moderation(commands.Cog, name='moderation'):
    def __init__(self, bot):
        self.bot = bot

    async def get_records_by_server_id(self, server_id):
        return await self.bot.db.fetch('SELECT * FROM punishments WHERE server_id=$1', str(server_id))
    
    async def get_records_by_user_id(self, user_id):
        return await self.bot.db.fetch('SELECT * FROM punishments WHERE user_id=$1', str(user_id))

    async def get_record_by_id(self, id):
        return await self.bot.db.fetchrow('SELECT * FROM punishments WHERE id=$1;', str(id))

    async def add_record(self, server_id, type, user_id, punisher_id, reason, duration=None, active=None):
        return await self.bot.db.fetchrow('INSERT INTO punishments (server_id, type, user_id, punisher_id, reason, duration, active) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *;',
            server_id, type, user_id, punisher_id, reason, int(duration), active)

    @cog_ext.cog_subcommand(
        base='purge',
        base_desc='Purge messages from the channel.',
        name='all',
        description='Purge all types of messages.',
        options=[
            create_option(
                name='number',
                description='The number of messages to purge.',
                option_type=4,
                required=True
            )
        ],
        guild_ids=[801630163866746901]
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def _purge_all(self, ctx, num):
        msgs = []
        async for msg in ctx.channel.history(limit=num):
            msgs.append(msg)
        await ctx.channel.delete_messages(msgs)
        embed = tools.create_embed(ctx, 'Message Purge (All)', f'{num} messages deleted.')
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base='purge',
        base_desc='Purge messages from the channel.',
        name='bots',
        description='Purge messages sent by bots.',
        options=[
            create_option(
                name='number',
                description='The number of messages to purge.',
                option_type=4,
                required=True
            )
        ],
        guild_ids=[801630163866746901]
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def _purge_bots(self, ctx, num):
        msgs = []
        async for msg in ctx.channel.history(limit=num):
            if msg.author.bot:
                msgs.append(msg)
        await ctx.channel.delete_messages(msgs)
        embed = tools.create_embed(ctx, 'Message Purge (Bots)', f'{num} messages deleted.')
        await ctx.send(embed=embed)
    
    @cog_ext.cog_subcommand(
        base='purge',
        base_desc='Purge messages from the channel.',
        name='humans',
        description='Purge messages sent by humans.',
        options=[
            create_option(
                name='number',
                description='The number of messages to purge.',
                option_type=4,
                required=True
            )
        ],
        guild_ids=[801630163866746901]
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def _purge_bots(self, ctx, num):
        msgs = []
        async for msg in ctx.channel.history(limit=num):
            if not msg.author.bot:
                msgs.append(msg)
        await ctx.channel.delete_messages(msgs)
        embed = tools.create_embed(ctx, 'Message Purge (Humans)', f'{num} messages deleted.')
        await ctx.send(embed=embed)
 
    @cog_ext.cog_slash(
        name='warn',
        description="Warn a member of the server.",
        options=[
            create_option(
                name='user',
                description="The member to warn.",
                option_type=6,
                required=True
            ),
            create_option(
                name='reason',
                description='The reason for the member\'s warn (Optional).',
                option_type=3,
                required=False
            )
        ],
        guild_ids=[801630163866746901]
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def warn(self, ctx, user, reason=None):
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
    
    @cog_ext.cog_slash(
        name='kick',
        description="Kick a member from the server.",
        options=[
            create_option(
                name='user',
                description="The member to kick.",
                option_type=6,
                required=True
            ),
            create_option(
                name='reason',
                description='The reason for the member\'s kick (Optional).',
                option_type=3,
                required=False
            )
        ],
        guild_ids=[801630163866746901, 809169133086048257]
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user, reason=None):
        await ctx.guild.kick(user, reason=reason)
        punishment_record = await self.add_record(str(ctx.guild.id), 'kick', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Kick', desc=f'{user} has been kicked.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'], inline=False)
        await ctx.send(embed=embed)
        
    @cog_ext.cog_slash(
        name='ban',
        description="Ban a member from the server.",
        options=[
            create_option(
                name='user',
                description="The member to ban.",
                option_type=6,
                required=True
            ),
            create_option(
                name='reason',
                description='The reason for the member\'s ban. (Optional)',
                option_type=3,
                required=False
            )
        ],
        guild_ids=[801630163866746901]
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user, reason=None):
        await ctx.guild.ban(user, reason=reason)
        punishment_record = await self.add_record(str(ctx.guild.id), 'ban', str(user.id), str(ctx.author.id), reason)
        embed = tools.create_embed(ctx, 'User Ban', desc=f'{user} has been banned.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'],inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='mute',
        description="Mute a user from the server.",
        options=[
            create_option(
                name='user',
                description="The user to mute.",
                option_type=6,
                required=True
            ),
            create_option(
                name='duration',
                description="The duration of the mute. Use 0 for a manual unmute.",
                option_type=4,
                required=True
            ),
            create_option(
                name='duration_unit',
                description="The unit of time for the duration.",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name='days',
                        value='days'
                    ),
                    create_choice(
                        name='hours',
                        value='hours'
                    ),
                    create_choice(
                        name='minutes',
                        value='minutes'
                    ),
                    create_choice(
                        name='seconds',
                        value='seconds'
                    )
                ]
            ),
            create_option(
                name='reason',
                description='The reason for the member\'s mute. (Optional)',
                option_type=3,
                required=False
            )
        ],
        guild_ids=[801630163866746901, 809169133086048257]
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, user, duration, duration_unit, reason=None):
        await ctx.respond()
        await user.add_roles(ctx.guild.get_role(809169133232717890))
        duration_adjustments = {
            'days': 1*60*60*24,
            'hours': 1*60*60,
            'minutes': 1*60,
            'seconds': 1
        }
        adjusted_duration = duration * duration_adjustments[duration_unit]
        punishment_record = await self.add_record(str(ctx.guild.id), 'mute', str(user.id), str(ctx.author.id), reason, duration=adjusted_duration, active=True)
        embed = tools.create_embed(ctx, 'User Mute', desc=f'{user} has been muted.')
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Punishment ID', value=punishment_record['id'],inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='unmute',
        description="Unmute a member from the server.",
        options=[
            create_option(
                name='member',
                description="The member to unmute.",
                option_type=6,
                required=True
            )
        ],
        guild_ids=[801630163866746901]
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, user):
        await user.remove_roles(ctx.guild.get_role(809169133232717890))
        embed = tools.create_embed(ctx, 'User Unmute', desc=f'{user} has been unmuted.')
        await ctx.send(embed=embed)
    
    @cog_ext.cog_subcommand(
        base='punishments',
        base_description='Get a list of punishments registered with the bot.',
        name='server',
        description='Get a list of punishments in the server.',
        guild_ids=[801630163866746901]
    )
    @commands.has_permissions(manage_messages=True)
    async def punishments_server(self, ctx):
        records = await self.get_records_by_server_id(str(ctx.guild.id))
        embed = tools.create_embed(ctx, 'Server Punishments')
        for record in records:
            user = await self.bot.fetch_user(record["user_id"])
            val = f'User: {user.mention} | Type: {record["type"]} | Timestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
            embed.add_field(name=record["id"], value=val)
        await ctx.send(embed=embed)
    
    @cog_ext.cog_subcommand(
        base='punishments',
        base_description='Get a list of punishments registered with the bot.',
        name='user',
        description='Get a list of punishments for a member.',
        options=[
            create_option(
                name='member',
                description='The member to get the punishments of.',
                option_type=6,
                required=True
            )
        ],
        guild_ids=[801630163866746901]
    )
    @commands.has_permissions(manage_messages=True)
    async def punishments_user(self, ctx, member):
        records = await self.get_records_by_user_id(str(member.id))
        embed = tools.create_embed(ctx, 'Server Punishments')
        for record in records:
            user = await self.bot.fetch_user(record['user_id'])
            val = f'User: {user.mention} | Type: {record["type"]} | Timestamp: {record["timestamp"].strftime("%b %-d %Y at %-I:%-M %p")}'
            embed.add_field(name=record["id"], value=val)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='punishmentinfo',
        description='View info about a specific punishment by unique ID.',
        options=[
            create_option(
                name='id',
                description='The unique ID associated with the punishment.',
                option_type=3,
                required=True
            )
        ],
        guild_ids=[801630163866746901]
    )
    @commands.has_permissions(manage_messages=True)
    async def punishmentinfo(self, ctx, id):
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