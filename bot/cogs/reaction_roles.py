import asyncio

from typing import Union
import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import (
    create_option,
    create_choice,
    SlashCommandOptionType,
)

from bot.helpers import tools


class ReactionRolesSlash(commands.Cog, name="reactionroles"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id != self.bot.user.id:
            records = await self.bot.db.fetch(
                "SELECT * FROM reaction_roles WHERE message_id=$1;", payload.message_id
            )
            if records:
                for record in records:
                    if record["emoji"] == str(payload.emoji):
                        guild = self.bot.get_guild(payload.guild_id)
                        member = guild.get_member(payload.user_id)
                        role = guild.get_role(int(record["role_id"]))
                        await member.add_roles(role)

                        embed = discord.Embed(
                            title="Reaction Role",
                            description=f"{member.mention}, you have been given {role.mention}.",
                        )
                        if record["response_message"] == "dm":
                            await member.send(embed=embed)
                        elif record["response_message"] == "rrch":
                            channel = guild.get_channel(payload.channel_id)
                            msg = await channel.send(embed=embed)
                            await asyncio.sleep(2)
                            await msg.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id != self.bot.user.id:
            records = await self.bot.db.fetch(
                "SELECT * FROM reaction_roles WHERE message_id=$1;", payload.message_id
            )
            if records:
                for record in records:
                    if record["emoji"] == str(payload.emoji):
                        guild = self.bot.get_guild(payload.guild_id)
                        member = guild.get_member(payload.user_id)
                        role = guild.get_role(int(record["role_id"]))
                        await member.remove_roles(role)
                        embed = discord.Embed(
                            title="Reaction Role",
                            description=f"{member.mention}, you have lost {role.mention}.",
                        )

                        if record["response_message"] == "dm":
                            await member.send(embed=embed)
                        elif record["response_message"] == "rrch":
                            channel = guild.get_channel(payload.channel_id)
                            msg = await channel.send(embed=embed)
                            await asyncio.sleep(2)
                            await msg.delete()

    @cog_ext.cog_subcommand(
        base="reactionroles",
        base_desc="Add, edit, delete, or get info on a reaction role.",
        name="add",
        description="Create a new reaction role. This is a multi-step command, so there are no parameters passed.",
        options=[
            create_option(
                name="channel",
                description="The channel that contains the message you want to be reacted to.",
                option_type=SlashCommandOptionType.CHANNEL,
                required=True,
            ),
            create_option(
                name="message_id",
                description="The ID of the message you want reacted to.",
                option_type=SlashCommandOptionType.INTEGER,
                required=True,
            ),
            create_option(
                name="role",
                description="The role you want to be given.",
                option_type=SlashCommandOptionType.ROLE,
                required=True,
            ),
            create_option(
                name="emoji",
                description="The emoji you want as the reaction.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="response_message",
                description="Whether or not you want the bot to respond with a message when a role is added or removed.",
                option_type=SlashCommandOptionType.STRING,
                choices=[
                    create_choice(name="In DMs", value="dm"),
                    create_choice(name="In reaction role channel", value="rrch"),
                    create_choice(name="Off", value="off"),
                ],
                required=True,
            ),
        ],
    )
    @commands.has_permissions(manage_messages=True)
    async def reactionroles_add(
        self,
        ctx: SlashContext,
        channel: discord.TextChannel,
        message_id: int,
        role: discord.Role,
        emoji: str,
        response_message: str,
    ):
        record = await self.bot.db.fetchrow(
            "INSERT INTO reaction_roles (server_id, channel_id, message_id, role_id, emoji, response_message) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *;",
            ctx.guild.id,
            channel.id,
            message_id,
            role.id,
            emoji,
            response_message,
        )
        channel = self.bot.get_channel(channel.id)
        message = channel.get_partial_message(message_id)
        await message.add_reaction(emoji)

        embed = tools.create_embed(
            ctx, "Reaction Role", "Reaction role has been added successfully!"
        )
        embed.add_field(name="Reaction Role ID", value=record["id"])
        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(name="Message ID", value=message_id)
        embed.add_field(name="Role", value=role.mention)
        embed.add_field(name="Emoji", value=emoji)

        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="reactionroles",
        base_desc="Add, edit, delete, or get info on a reaction role.",
        name="info",
        description="Get info about a specific reaction role by ID.",
        options=[
            create_option(
                name="id",
                description="The ID of the reaction role. Get this with /listreactions.",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def reactionroles_info(self, ctx: SlashContext, id: str):
        record = await self.bot.db.fetchrow(
            "SELECT * FROM reaction_roles WHERE id=$1;", id
        )
        embed = tools.create_embed(ctx, "Reaction Role Info")
        embed.add_field(name="Reaction Role ID", value=record["id"], inline=False)
        embed.add_field(
            name="Channel",
            value=ctx.guild.get_channel(record["channel_id"]).mention,
            inline=False,
        )
        embed.add_field(name="Message ID", value=record["message_id"], inline=False)
        embed.add_field(
            name="Role", value=ctx.guild.get_role(record["role_id"]).mention
        )
        embed.add_field(name="Emoji", value=record["emoji"])
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="reactionroles",
        base_desc="Add, edit, delete, or get info on a reaction role.",
        name="list",
        description="List reaction roles in the server.",
    )
    async def reactionroles_list(self, ctx: SlashContext):
        embed = tools.create_embed(ctx, "Reaction Roles List")
        records = await self.bot.db.fetch(
            "SELECT * FROM reaction_roles WHERE server_id=$1;", ctx.guild.id
        )
        for record in records:
            embed.add_field(
                name=record["id"],
                value=f'Message ID: {record["message_id"]} | Role: {ctx.guild.get_role(int(record["role_id"])).mention} | Emoji: {record["emoji"]}',
                inline=False,
            )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="reactionroles",
        base_desc="Add, edit, delete, or get info on a reaction role.",
        name="delete",
        description="Delete a reaction role.",
        options=[
            create_option(
                name="id",
                description="The ID of the reaction role. Get this with /listreactions.",
                option_type=3,
                required=True,
            ),
        ],
    )
    @commands.has_permissions(manage_messages=True)
    async def reactionroles_delete(self, ctx: SlashContext, id: str) -> None:
        record = await self.bot.db.fetch(
            "SELECT * FROM reaction_roles WHERE id=$1;", str(id)
        )
        if record["server_id"] != ctx.guild.id:
            embed = tools.create_error_embed(
                ctx, "You cannot delete another server's reaction role!"
            )
            await ctx.send(embed)
            return

        await self.bot.db.fetch("DELETE FROM reaction_roles WHERE id=$1", str(id))

        embed = tools.create_embed(
            ctx,
            "Reaction Role Deleted",
            f"The reaction role with ID {id} was deleted successfully.",
        )
        await ctx.send(embed=embed)


class ReactionRoles(ReactionRolesSlash, commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(bot)

    @commands.group(name="reactionroles")
    async def reactionroles_legacy(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @reactionroles_legacy.command(name="add")
    async def reactionroles_add_legacy(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        message_id: int,
        role: discord.Role,
        emoji: str,
    ):
        pass

    @commands.command(name="addreaction", brief="Add a new reaction!", help="help")
    @commands.has_permissions(manage_messages=True)
    async def addreaction(self, ctx: commands.Context):
        """Create a new reaction role.
        Reaction roles have a UUID that is created each time one is registered.
        This UUID is used to edit and view information about the reaction.
        """
        gs = [
            [
                "Tag the channel that contains the message you want to be reacted to.",
            ],
            [
                "Paste the message ID of the message you want reacted to. Make sure the message is in the channel you provided in the previous step.",
            ],
            [
                "Tag the role that you want added, or paste the role ID.",
            ],
            [
                "What emoji would you like to react with?",
            ],
        ]

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        embed = tools.create_embed(
            ctx,
            "Reaction Role Setup 1/4",
            "Tag the channel that contains the message you want to be reacted to.",
        )
        sent_msg = await ctx.send(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=60)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Reaction role add has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            channel_id = user_msg.raw_channel_mentions[0]

        embed = tools.create_embed(
            ctx,
            "Reaction Role Setup 2/4",
            "Paste the message ID of the message you want reacted to. Make sure the message is in the channel you provided in the previous step.",
        )
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=60)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Reaction role add has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            message_id = user_msg.content

        embed = tools.create_embed(
            ctx,
            "Reaction Role Setup 3/4",
            "Tag the role that you want added, or paste the role ID.",
        )
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

        embed = tools.create_embed(
            ctx, "Reaction Role Setup 4/4", "What emoji would you like to react with?"
        )
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=60)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Reaction role add has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            emoji = user_msg.content

        record = await self.add_record(
            str(ctx.guild.id), str(channel_id), str(message_id), str(role_id), emoji
        )
        channel = self.bot.get_channel(int(channel_id))
        message = channel.get_partial_message(int(message_id))
        await message.add_reaction(emoji)

        embed = tools.create_embed(
            ctx, "Reaction Role", "Reaction role has been added successfully!"
        )
        embed.add_field(name="Reaction Role ID", value=record["id"])
        embed.add_field(name="Channel ID", value=channel_id)
        embed.add_field(name="Message ID", value=message_id)
        embed.add_field(name="Role ID", value=role_id)
        embed.add_field(name="Emoji", value=emoji)

        await sent_msg.edit(embed=embed)

    @commands.command(
        name="reactioninfo",
        brief="Get info about a specific reaction role by ID.",
    )
    async def reactioninfo(self, ctx: commands.Context, *, id: str):
        """Get info about a specific reaction role by ID."""
        record = await self.bot.db.fetchrow(
            "SELECT * FROM reaction_roles WHERE id=$1;", id
        )
        embed = tools.create_embed(ctx, "Reaction Role Info")
        embed.add_field(name="Reaction Role ID", value=record["id"], inline=False)
        embed.add_field(
            name="Channel",
            value=ctx.guild.get_channel(int(record["channel_id"])).mention,
            inline=False,
        )
        embed.add_field(name="Message ID", value=record["message_id"], inline=False)
        embed.add_field(
            name="Role", value=ctx.guild.get_role(int(record["role_id"])).mention
        )
        embed.add_field(name="Emoji", value=record["emoji"])
        await ctx.send(embed=embed)

    @commands.command(
        name="listreactions",
        brief="List reaction roles in the server",
    )
    async def listreactions(self, ctx: commands.Context):
        """List reaction roles."""
        embed = tools.create_embed(ctx, "Reaction Roles List")
        records = await self.bot.db.fetch(
            "SELECT * FROM reaction_roles WHERE server_id=$1;", ctx.guild.id
        )
        for record in records:
            embed.add_field(
                name=record["id"],
                value=f'Message ID: {record["message_id"]} | Role: {ctx.guild.get_role(int(record["role_id"])).mention} | Emoji: {record["emoji"]}',
            )
        await ctx.send(embed=embed)

    @commands.command(
        name="deletereaction",
        brief="Delete a reaction role.",
    )
    async def deletereaction(self, ctx: commands.Context, id: str):
        """Delete a reacion by ID."""
        await ctx.send("This command has not been created yet.")


def setup(bot: commands.Bot):
    bot.add_cog(ReactionRoles(bot))
