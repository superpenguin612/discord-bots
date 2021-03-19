import discord
from discord.ext import commands
from bot.helpers import tools
import json

class Settings(commands.Cog, name='settings'):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_all_records(self):
        return await self.bot.db.fetch('SELECT * FROM settings;')
    
    async def get_record_by_server_id(self, server_id):
        return await self.bot.db.fetchrow('SELECT * FROM settings WHERE server_id=$1;', str(server_id))

    async def add_record(self, server_id, json):
        return await self.bot.db.fetchrow('INSERT INTO settings (server_id, json) RETURNING *;',
            server_id, json)
    
    async def remove_record(self, id):
        return await self.bot.db.fetch('DELETE FROM reaction_roles WHERE server_id=$1', str(id))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        default_settings = {
            "moderation": {
                "muted_role": 809169133232717890,
                "mod_role": 818866766695890947
            },
            "starboard": {
                "channel": 818915325646340126,
                "number_required": 5,
                "reaction": "⭐"
            },
            "daily_report": {
                "channel": 819546169985597440
            },
            "suggestions": {
                "channel": 818901195023843368,
                "up_emoji": "<:upvote:818940395320639488>",
                "down_emoji": "<:downvote:818940394967924767>"
            }
        }
        json_str = json.dumps(default_settings)
        await self.add_record(guild.id, json_str)

    @commands.command(
        name='settings',
        brief='Get a list settings for the server.'
    )
    async def settings(self, ctx):
        record = await self.get_record_by_server_id(ctx.guild.id)
        print(record)
        server_settings = json.loads(record['json'])
        embed = tools.create_embed(ctx, 'Bot Settings')
        embed.add_field(
            name='Starboard', 
            value=f'**Channel**: {ctx.bot.get_channel(server_settings["starboard"]["channel"])}' \
                  f'**Number Required**: {server_settings["starboard"]["number_required"]}' \
                  f'**Reaction**: {server_settings["starboard"]["reaction"]}'
        )
        embed.add_field(
            name='Suggestions', 
            value=f'**Channel**: {ctx.bot.get_channel(server_settings["suggestions"]["channel"])}' \
                  f'**Up Emoji**: {server_settings["suggestions"]["up_emoji"]}' \
                  f'**Down Emoji**: {server_settings["suggestions"]["down_emoji"]}'
        )
        await ctx.send(embed=embed)