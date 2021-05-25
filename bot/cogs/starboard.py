import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import asyncio
import asyncpg
import json
from datetime import datetime


class Starboard(commands.Cog, name="starboard"):
    STAR_THRESHOLD = 3

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_all_records(self):
        return await self.bot.db.fetch("SELECT * FROM starboard;")

    async def get_record_by_message_id(self, message_id):
        return await self.bot.db.fetchrow(
            "SELECT * FROM starboard WHERE message_id=$1;", str(message_id)
        )

    async def get_records_by_server_id(self, server_id):
        return await self.bot.db.fetch(
            "SELECT * FROM starboard WHERE server_id=$1;", str(server_id)
        )

    # async def add_record(
    #     self,
    #     server_id,
    #     channel_id,
    #     message_id,
    #     star_number,
    #     starboard_message_id,
    #     starred_users,
    #     forced,
    #     locked,
    #     removed,
    # ):
    #     return await self.bot.db.fetchrow(
    #         "INSERT INTO starboard (server_id, channel_id, message_id, star_number, starboard_message_id, starred_users, forced, locked, removed) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING *;",
    #         str(server_id),
    #         str(channel_id),
    #         str(message_id),
    #         int(star_number),
    #         str(starboard_message_id),
    #         [str(user) for user in starred_users],
    #         bool(forced),
    #         bool(locked),
    #         bool(removed),
    #     )

    # async def update_record(self, message_id, star_number, starred_users):
    #     return await self.bot.db.fetchrow(
    #         "UPDATE starboard SET star_number = $1, starred_users = $2 WHERE message_id=$3",
    #         star_number,
    #         starred_users,
    #         str(message_id),
    #     )

    async def remove_record(self, id):
        return await self.bot.db.fetch("DELETE FROM starboard WHERE id=$1", str(id))

    async def add_message_to_starboard(self, message, payload):
        star_number = self.STAR_THRESHOLD

        embed = discord.Embed(
            title=f"{star_number} ⭐️",
            description=message.content,
            color=discord.Color.gold(),
        )
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name="Source", value=f"[Jump to message!]({message.jump_url})")
        embed.set_footer(
            text=f'Message ID: {message.id} | Date: {datetime.now().strftime("%m/%d/%Y")}'
        )
        if message.guild.id == 621878393465733120:
            channel = message.guild.get_channel(840287267029123103)
        else:
            channel = message.guild.get_channel(818915325646340126)

        starboard_message = await channel.send(embed=embed)

        starred_users = [str(payload.user_id)]
        await self.bot.db.execute(
            "INSERT INTO starboard (server_id, channel_id, message_id, star_number, starboard_message_id, starred_users, forced, locked, removed) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);",
            str(message.guild.id),
            str(message.channel.id),
            str(message.id),
            star_number,
            str(starboard_message.id),
            starred_users,
            False,
            False,
            False,
        )

    async def add_star(self, payload, record):
        star_number = record["star_number"] + 1
        guild = self.bot.get_guild(int(record["server_id"]))
        if guild.id == 621878393465733120:
            channel = guild.get_channel(840287267029123103)
        else:
            channel = guild.get_channel(818915325646340126)
        starboard_message = await channel.fetch_message(
            int(record["starboard_message_id"])
        )

        embed = starboard_message.embeds[0]
        embed.title = f"{star_number} ⭐️"
        await starboard_message.edit(embed=embed)
        starred_users = record["starred_users"]
        starred_users.append(str(payload.user_id))
        await self.bot.db.execute(
            "UPDATE starboard SET star_number = $1, starred_users = $2 WHERE message_id=$3",
            star_number,
            starred_users,
            str(payload.message_id),
        )

    async def remove_star(self, payload, record):
        star_number = record["star_number"] - 1
        guild = self.bot.get_guild(int(record["server_id"]))
        if guild.id == 621878393465733120:
            channel = guild.get_channel(840287267029123103)
        else:
            channel = guild.get_channel(818915325646340126)
        starboard_message = await channel.fetch_message(
            int(record["starboard_message_id"])
        )

        embed = starboard_message.embeds[0]
        embed.title = f"{star_number} ⭐️"
        await starboard_message.edit(embed=embed)
        starred_users = record["starred_users"]
        starred_users.remove(str(payload.user_id))
        await self.bot.db.execute(
            "UPDATE starboard SET star_number = $1, starred_users = $2 WHERE message_id=$3",
            star_number,
            starred_users,
            str(payload.message_id),
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.bot.user.id and payload.emoji.name == "⭐":
            record = await self.get_record_by_message_id(payload.message_id)
            if record:
                await self.add_star(payload, record)
            else:
                guild = self.bot.get_guild(payload.guild_id)
                channel = guild.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                for reaction in message.reactions:
                    if reaction.emoji == "⭐" and reaction.count >= self.STAR_THRESHOLD:
                        await self.add_message_to_starboard(message, payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id != self.bot.user.id and payload.emoji.name == "⭐":
            record = await self.get_record_by_message_id(payload.message_id)
            if record:
                await self.remove_star(payload, record)

    @cog_ext.cog_subcommand(
        base="starboard",
        base_desc="Force, lock, or remove a starboard message.",
        name="force",
        description="Force a message to starboard.",
        options=[
            create_option(
                name="message_id",
                description="The ID of the message to force to starboard.",
                option_type=4,
                required=True,
            ),
        ],
    )
    async def starboard_force(self, ctx, message_id):
        pass

    @cog_ext.cog_subcommand(
        base="starboard",
        base_desc="Force, lock, or remove a starboard message.",
        name="lock",
        description="Lock a message on the starboard. This prevents it from getting or losing stars.",
        options=[
            create_option(
                name="message_id",
                description="The ID of the message to lock on the starboard.",
                option_type=4,
                required=True,
            ),
        ],
    )
    async def starboard_lock(self, ctx, message_id):
        pass

    @cog_ext.cog_subcommand(
        base="starboard",
        base_desc="Force, lock, or remove a starboard message.",
        name="remove",
        description="Remove a starboard message. This prevents it from coming back to the starboard.",
        options=[
            create_option(
                name="message_id",
                description="The ID of the message to delete from the starboard.",
                option_type=4,
                required=True,
            ),
        ],
    )
    async def starboard_remove(self, ctx, message_id):
        pass


def setup(bot: commands.Bot):
    bot.add_cog(Starboard(bot))
