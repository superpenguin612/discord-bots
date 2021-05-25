import discord
from discord.ext import commands
from discord_slash.model import SlashCommandOptionType
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import json
from enum import Enum


class Settings(commands.Cog, name="settings"):
    DEFAULT_SETTINGS = {
        "moderation": {
            "muted_role": None,
            "public_logs_channel": None,
            "mod_logs_channel": None,
        },
        "starboard": {
            "channel": None,
            "number_required": 3,
            "reaction": "⭐",
        },
        "suggestions": {
            "channel": None,
            "up_emoji": "<:upvote:818940395320639488>",
            "down_emoji": "<:downvote:818940394967924767>",
        },
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_record_by_server_id(self, server_id):
        return await self.bot.db.fetchrow(
            "SELECT * FROM settings WHERE server_id=$1;", str(server_id)
        )

    async def edit_record(self, server_id, json):
        return await self.bot.db.execute(
            "UPDATE settings SET json=$1 WHERE server_id=$2", json, server_id
        )

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        json_str = json.dumps(self.DEFAULT_SETTINGS)
        await self.bot.db.execute(
            "INSERT INTO settings (server_id, json) VALUES $1, $2", guild.id, json_str
        )

    @cog_ext.cog_slash(
        name="listsettings",
        description="Get the settings for the server.",
    )
    async def listsettings(self, ctx: SlashContext) -> None:
        record = await self.bot.db.fetchrow(
            "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
        )
        server_settings = json.loads(record["json"])
        embed = tools.create_embed(ctx, "Bot Settings")
        embed.add_field(
            name="Starboard",
            value=f'**Channel**: {ctx.bot.get_channel(server_settings["starboard"]["channel"])}'
            f'**Number Required**: {server_settings["starboard"]["number_required"]}'
            f'**Reaction**: {server_settings["starboard"]["reaction"]}',
        )
        embed.add_field(
            name="Suggestions",
            value=f'**Channel**: {ctx.bot.get_channel(server_settings["suggestions"]["channel"])}'
            f'**Up Emoji**: {server_settings["suggestions"]["up_emoji"]}'
            f'**Down Emoji**: {server_settings["suggestions"]["down_emoji"]}',
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="editsettings",
        base_desc="Edit the settings for the server.",
        subcommand_group="moderation",
        sub_group_desc="Edit moderation settings.",
        name="publiclogschannel",
        description="Edit the channel for public mod logs.",
        options=[
            create_option(
                name="channel",
                description="The new public logs channel.",
                option_type=SlashCommandOptionType.CHANNEL,
                required=True,
            ),
        ],
    )
    async def editsettings_moderation_publiclogschannel(
        self, ctx: SlashContext, channel: discord.TextChannel
    ) -> None:
        if type(channel) == discord.TextChannel:
            record = await self.bot.db.fetchrow(
                "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
            )
            server_settings = json.loads(record["json"])
            server_settings["moderation"]["public_logs_channel"] = channel.id
            await self.edit_record(ctx.guild.id, json.dumps(server_settings))
            embed = tools.create_embed(
                ctx,
                "Edit Settings",
                desc="The starboard channel has been updated successfully.",
            )
            await ctx.send(embed=embed)
        else:
            embed = tools.create_error_embed(ctx, "The channel must be a text channel.")
            await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="editsettings",
        base_desc="Edit the settings for the server.",
        subcommand_group="moderation",
        sub_group_desc="Edit moderation settings.",
        name="modlogschannel",
        description="Edit the starboard channel.",
        options=[
            create_option(
                name="channel",
                description="The new starboard channel.",
                option_type=SlashCommandOptionType.CHANNEL,
                required=True,
            ),
        ],
    )
    async def editsettings_starboard_modlogschannel(
        self, ctx: SlashContext, channel: discord.TextChannel
    ) -> None:
        if type(channel) == discord.TextChannel:
            record = await self.bot.db.fetchrow(
                "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
            )
            server_settings = json.loads(record["json"])
            server_settings["starboard"]["channel"] = channel.id
            await self.edit_record(ctx.guild.id, json.dumps(server_settings))
            embed = tools.create_embed(
                ctx,
                "Edit Settings",
                desc="The starboard channel has been updated successfully.",
            )
            await ctx.send(embed=embed)
        else:
            embed = tools.create_error_embed(ctx, "The channel must be a text channel.")
            await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="editsettings",
        base_desc="Edit the settings for the server.",
        subcommand_group="moderation",
        sub_group_desc="Edit moderation settings.",
        name="mutedrole",
        description="Edit the muted role.",
        options=[
            create_option(
                name="channel",
                description="The new starboard channel.",
                option_type=SlashCommandOptionType.CHANNEL,
                required=True,
            ),
        ],
    )
    async def editsettings_moderation_mutedrole(
        self, ctx: SlashContext, channel: discord.TextChannel
    ) -> None:
        if type(channel) == discord.TextChannel:
            record = await self.bot.db.fetchrow(
                "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
            )
            server_settings = json.loads(record["json"])
            server_settings["starboard"]["channel"] = channel.id
            await self.edit_record(ctx.guild.id, json.dumps(server_settings))
            embed = tools.create_embed(
                ctx,
                "Edit Settings",
                desc="The starboard channel has been updated successfully.",
            )
            await ctx.send(embed=embed)
        else:
            embed = tools.create_error_embed(ctx, "The channel must be a text channel.")
            await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="editsettings",
        base_desc="Edit the settings for the server.",
        subcommand_group="starboard",
        sub_group_desc="Edit the settings for the starboard.",
        name="channel",
        description="Edit the starboard channel.",
        options=[
            create_option(
                name="channel",
                description="The new starboard channel.",
                option_type=SlashCommandOptionType.CHANNEL,
                required=True,
            ),
        ],
    )
    async def editsettings_starboard_channel(
        self, ctx: SlashContext, channel: discord.TextChannel
    ) -> None:
        if type(channel) == discord.TextChannel:
            record = await self.bot.db.fetchrow(
                "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
            )
            server_settings = json.loads(record["json"])
            server_settings["starboard"]["channel"] = channel.id
            await self.edit_record(ctx.guild.id, json.dumps(server_settings))
            embed = tools.create_embed(
                ctx,
                "Edit Settings",
                desc="The starboard channel has been updated successfully.",
            )
            await ctx.send(embed=embed)
        else:
            embed = tools.create_error_embed(ctx, "The channel must be a text channel.")
            await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="editsettings",
        base_desc="Edit the settings for the server.",
        subcommand_group="starboard",
        sub_group_desc="Edit the settings for the starboard.",
        name="numberrequired",
        description="Edit the number of stars required to add a message to the starboard.",
        options=[
            create_option(
                name="number",
                description="The new number of stars required for the starboard.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
    )
    async def editsettings_starboard_numberrequired(
        self, ctx: SlashContext, number: int
    ) -> None:
        record = await self.bot.db.fetchrow(
                "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
            )
        server_settings = json.loads(record["json"])
        server_settings["starboard"]["number_required"] = number
        await self.edit_record(ctx.guild.id, json.dumps(server_settings))
        embed = tools.create_embed(
            ctx,
            "Edit Settings",
            desc="The number of stars required for the starboard has been updated successfully.",
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="editsettings",
        base_desc="Edit the settings for the server.",
        subcommand_group="starboard",
        sub_group_desc="Edit the settings for the starboard.",
        name="reaction",
        description="Edit the reaction to use for the starboard.",
        options=[
            create_option(
                name="emoji",
                description="The new reaction to use for the starboard.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
    )
    async def editsettings_starboard_reaction(
        self, ctx: SlashContext, emoji: str
    ) -> None:
        record = await self.bot.db.fetchrow(
                "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
        )
        server_settings = json.loads(record["json"])
        server_settings["starboard"]["reaction"] = emoji
        await self.edit_record(ctx.guild.id, json.dumps(server_settings))
        embed = tools.create_embed(
            ctx,
            "Edit Settings",
            desc="The reaction to use for the starboard has been updated successfully.",
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="editsettings",
        base_desc="Edit the settings for the server.",
        subcommand_group="suggestions",
        sub_group_desc="Edit the settings for suggestions.",
        name="channel",
        description="Edit the suggestions channel.",
        options=[
            create_option(
                name="channel",
                description="The new suggestions channel.",
                option_type=7,
                required=True,
            ),
        ],
    )
    async def editsettings_suggestions_channel(
        self, ctx: SlashContext, channel: discord.TextChannel
    ):
        if type(channel) == discord.channel.TextChannel:
            record = await self.bot.db.fetchrow(
                "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
            )
            server_settings = json.loads(record["json"])
            server_settings["suggestions"]["channel"] = channel.id
            await self.edit_record(ctx.guild.id, json.dumps(server_settings))
            embed = tools.create_embed(
                ctx,
                "Edit Settings",
                desc="The suggestions channel has been updated successfully.",
            )
            await ctx.send(embed=embed)
        else:
            embed = tools.create_error_embed(ctx, "The channel must be a text channel.")
            await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="editsettings",
        base_desc="Edit the settings for the server.",
        subcommand_group="suggestions",
        sub_group_desc="Edit the settings for suggestions.",
        name="upemoji",
        description="Edit the up emoji for suggestions.",
        options=[
            create_option(
                name="emoji",
                description="The new up emoji for suggestions.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
    )
    async def editsettings_suggestions_upemoji(self, ctx: SlashContext, emoji: str):
        record = await self.bot.db.fetchrow(
            "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
        )
        server_settings = json.loads(record["json"])
        server_settings["starboard"]["up_emoji"] = emoji
        await self.edit_record(ctx.guild.id, json.dumps(server_settings))
        embed = tools.create_embed(
            ctx,
            "Edit Settings",
            desc="The up emoji for suggestions has been updated successfully.",
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="editsettings",
        base_desc="Edit the settings for the server.",
        subcommand_group="suggestions",
        sub_group_desc="Edit the settings for the suggestions.",
        name="downemoji",
        description="Edit the down emoji for suggestions.",
        options=[
            create_option(
                name="emoji",
                description="The new down emoji for suggestions.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
    )
    async def editsettings_suggestions_downemoji(self, ctx: SlashContext, emoji: str):
        record = await self.bot.db.fetchrow(
            "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
        )
        server_settings = json.loads(record["json"])
        server_settings["starboard"]["down_emoji"] = emoji
        await self.edit_record(ctx.guild.id, json.dumps(server_settings))
        embed = tools.create_embed(
            ctx,
            "Edit Settings",
            desc="The down emoji for suggestions has been updated successfully.",
        )
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))
