import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
import json


class Settings(commands.Cog, name="settings"):
    def __init__(self, bot):
        self.bot = bot

    async def get_all_records(self):
        return await self.bot.db.fetch("SELECT * FROM settings;")

    async def get_record_by_server_id(self, server_id):
        return await self.bot.db.fetchrow(
            "SELECT * FROM settings WHERE server_id=$1;", str(server_id)
        )

    async def add_record(self, server_id, json):
        return await self.bot.db.execute(
            "INSERT INTO settings (server_id, json) VALUES $1, $2", server_id, json
        )

    async def edit_record(self, server_id, json):
        return await self.bot.db.execute(
            "UPDATE settings SET json=$1 WHERE server_id=$2", json, server_id
        )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        default_settings = {
            "bot_messages": {
                "channel": 809169133635108882,
            },
            "moderation": {
                "muted_role": 809169133232717890,
                "mod_role": 818866766695890947,
            },
            "starboard": {
                "channel": 818915325646340126,
                "number_required": 5,
                "reaction": "⭐",
            },
            "daily_report": {"channel": 819546169985597440},
            "suggestions": {
                "channel": 818901195023843368,
                "up_emoji": "<:upvote:818940395320639488>",
                "down_emoji": "<:downvote:818940394967924767>",
            },
        }
        json_str = json.dumps(default_settings)
        print(json_str)
        await self.add_record(guild.id, json_str)

    @cog_ext.cog_slash(
        name="listsettings",
        description="Get the settings for the server.",
    )
    async def listsettings(self, ctx):
        record = await self.get_record_by_server_id(ctx.guild.id)
        print(record)
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
        subcommand_group="starboard",
        sub_group_desc="Edit the settings for the starboard.",
        name="channel",
        description="Edit the starboard channel.",
        options=[
            create_option(
                name="channel",
                description="The new starboard channel.",
                option_type=7,
                required=True,
            ),
        ],
    )
    async def editsettings_starboard_channel(self, ctx, channel):
        if type(channel) == discord.channel.TextChannel:
            record = await self.get_record_by_server_id(ctx.guild.id)
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
                option_type=4,
                required=True,
            ),
        ],
    )
    async def editsettings_starboard_numberrequired(self, ctx, number):
        record = await self.get_record_by_server_id(ctx.guild.id)
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
                option_type=3,
                required=True,
            ),
        ],
    )
    async def editsettings_starboard_reaction(self, ctx, emoji):
        record = await self.get_record_by_server_id(ctx.guild.id)
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
        subcommand_group="dailyreport",
        sub_group_desc="Edit the settings for the daily report.",
        name="channel",
        description="Edit the daily report channel.",
        options=[
            create_option(
                name="channel",
                description="The new daily report channel.",
                option_type=7,
                required=True,
            ),
        ],
    )
    async def editsettings_dailyreport_channel(self, ctx, channel):
        if type(channel) == discord.channel.TextChannel:
            record = await self.get_record_by_server_id(ctx.guild.id)
            server_settings = json.loads(record["json"])
            server_settings["starboard"]["channel"] = channel.id
            await self.edit_record(ctx.guild.id, json.dumps(server_settings))
            embed = tools.create_embed(
                ctx,
                "Edit Settings",
                desc="The daily report channel has been updated successfully.",
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
    async def editsettings_suggestions_channel(self, ctx, channel):
        if type(channel) == discord.channel.TextChannel:
            record = await self.get_record_by_server_id(ctx.guild.id)
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
                option_type=7,
                required=True,
            ),
        ],
    )
    async def editsettings_suggestions_upemoji(self, ctx, emoji):
        record = await self.get_record_by_server_id(ctx.guild.id)
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
                option_type=7,
                required=True,
            ),
        ],
    )
    async def editsettings_suggestions_downemoji(self, ctx, emoji):
        record = await self.get_record_by_server_id(ctx.guild.id)
        server_settings = json.loads(record["json"])
        server_settings["starboard"]["down_emoji"] = emoji
        await self.edit_record(ctx.guild.id, json.dumps(server_settings))
        embed = tools.create_embed(
            ctx,
            "Edit Settings",
            desc="The down emoji for suggestions has been updated successfully.",
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Settings(bot))
