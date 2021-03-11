import discord
from discord import raw_models
from discord.ext import commands
from bot.helpers import tools
import asyncpg

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_all_records(self):
        return await self.bot.db.fetch('SELECT * FROM reaction_roles;')

    async def get_records_by_message_id(self, id):
        return await self.bot.db.fetch('SELECT * FROM reaction_roles WHERE message_id=$1;', str(id))
    
    async def get_records_by_server_id(self, id):
        return await self.bot.db.fetch('SELECT * FROM reaction_roles WHERE server_id=$1;', str(id))

    async def get_records_by_id(self, id):
        return await self.bot.db.fetchrow('SELECT * FROM reaction_roles WHERE id=$1;', str(id))

    async def add_record(self, server_id, message_id, role_id, emoji):
        return await self.bot.db.fetchrow('INSERT INTO reaction_roles (server_id, message_id, role_id, emoji) VALUES ($1, $2, $3, $4) RETURNING *;',
            server_id, message_id, role_id, emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.bot.user.id:
            record = await self.get_record_by_message_id(payload.message_id)
            if record:
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                role = guild.get_role(int(record['role_id']))
                await member.add_roles(role)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id != self.bot.user.id:
            record = await self.get_record_by_message_id(payload.message_id)
            if record:
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                role = guild.get_role(int(record['role_id']))
                await member.remove_roles(role)
        
    @commands.group()
    async def reactionroles(self, ctx):
        pass
    
    @reactionroles.command(
        name='add',
        brief='Add a new reaction!',
        help='help'
    )
    async def reactionrole_add(self, ctx):
        """Create a new reaction role.
        """
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        embed = tools.create_embed(ctx, "Reaction Role Setup 1/4", "Tag the channel that contains the message you want to be reacted to.")
        sent_msg = await ctx.send(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=60)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Reaction role add has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            channel_id = user_msg.raw_channel_mentions[0]

        embed = tools.create_embed(ctx, "Reaction Role Setup 2/4", "Paste the message ID of the message you want reacted to. Make sure the message is in the channel you provided in the previous step.")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=60)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Reaction role add has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            message_id = user_msg.content

        embed = tools.create_embed(ctx, "Reaction Role Setup 3/4", "Tag the role that you want added, or paste the role ID.")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=60)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Reaction role add has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            if user_msg.raw_role_mentions:
                role_id = user_msg.raw_role_mentions[0]
            else:
                role_id = user_msg.content

        embed = tools.create_embed(ctx, "Reaction Role Setup 4/4", "What emoji would you like to react with?")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=60)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Reaction role add has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            emoji = user_msg.content

        record = await self.add_record(str(ctx.guild.id), str(message_id), str(role_id), emoji)
        channel = self.bot.get_channel(int(channel_id))
        message = channel.get_partial_message(int(message_id))
        await message.add_reaction(emoji)

        embed = tools.create_embed(ctx, "Reaction Role", "Reaction role has been added successfully!")
        embed.add_field(name='Reaction Role ID', value=record['id'])
        embed.add_field(name='Channel ID', value=channel_id)
        embed.add_field(name='Message ID', value=message_id)
        embed.add_field(name='Role ID', value=role_id)
        embed.add_field(name='Emoji', value=emoji)

        await sent_msg.edit(embed=embed)
    
    @reactionroles.command(
        name='list',
        brief='Add a new reaction!',
        help='help'
    )
    async def reactionrole_list(self, ctx):
        """List reaction roles.
        """
        embed = tools.create_embed(ctx, "Reaction Roles List")
        records = await self.get_records_by_server_id(str(ctx.guild.id))
        for record in records:
            embed.add_field(name=record['id'], value=f'Message ID: {record["message_id"]} | Role: {ctx.guild.get_role(record["role_id"])} | Emoji: {record["emoji"]}')
        await ctx.send(embed=embed)

    @reactionroles.command(
        name='info',
        brief='Add a new reaction!',
        help='help'
    )
    async def reactionrole_info(self, ctx, id):
        """List reaction roles.
        """
        record = await self.get_record_by_id(str(ctx.guild.id))
        embed = tools.create_embed(ctx, "Reaction Role Info")
        embed.add_field(name='Reaction Role ID', value=record['id'])
        embed.add_field(name='Channel', value=ctx.guild.get_channel(record['channel_id']).mention)
        embed.add_field(name='Message ID', value=record['message_id'])
        embed.add_field(name='Role', value=ctx.guild.get_role(int(record['role_id'])).mention)
        embed.add_field(name='Emoji', value=record['emoji'])
        await ctx.send(embed=embed)