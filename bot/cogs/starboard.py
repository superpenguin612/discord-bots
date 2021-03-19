import discord
from discord.ext import commands
from bot.helpers import tools
import asyncio
import asyncpg

class Starboard(commands.Cog, name='starboard'):
    def __init__(self, bot):
        self.bot = bot

    async def get_all_records(self):
        return await self.bot.db.fetch('SELECT * FROM starboard;')

    async def get_records_by_message_id(self, message_id):
        return await self.bot.db.fetch('SELECT * FROM starboard WHERE message_id=$1;', str(message_id))
    
    async def get_records_by_server_id(self, server_id):
        return await self.bot.db.fetch('SELECT * FROM starboard WHERE server_id=$1;', str(server_id))

    async def get_record_by_id(self, id):
        return await self.bot.db.fetchrow('SELECT * FROM starboard WHERE id=$1;', str(id))

    async def add_record(self, server_id, channel_id, message_id, role_id, emoji):
        return await self.bot.db.fetchrow('INSERT INTO starboard (server_id, channel_id, message_id, role_id, emoji) VALUES ($1, $2, $3, $4, $5) RETURNING *;',
            server_id, channel_id, message_id, role_id, emoji)
    
    async def remove_record(self, id):
        return await self.bot.db.fetch('DELETE FROM reaction_roles WHERE id=$1', str(id))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.bot.user.id:
            records = await self.get_records_by_message_id(payload.message_id)
            if records:
                for record in records:
                    if record['emoji'] == str(payload.emoji):
                        guild = self.bot.get_guild(payload.guild_id)
                        channel = guild.get_channel(payload.channel_id)
                        member = guild.get_member(payload.user_id)
                        role = guild.get_role(int(record['role_id']))
                        await member.add_roles(role)
                        embed = discord.Embed(title='Reaction Role', description=f'{member.mention}, you have been given {role.mention}.')
                        msg = await channel.send(embed=embed)
                        await asyncio.sleep(2)
                        await msg.delete()

    async def add_to_starboard(self):
        pass