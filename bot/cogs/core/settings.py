import json
from typing import Union
import asyncio

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_components import Button, ButtonStyle

from bot.helpers import tools


class SettingsHandler:
    def __init__(
        self,
        bot: commands.Bot,
        ctx: Union[commands.Context, SlashContext],
        embeds: list[
            discord.Embed,
            dict[commands.Cog, list[discord.Embed]],
            dict[commands.Command, list[discord.Embed]],
        ],
        hierarchy: dict[commands.Bot, dict[commands.Cog, commands.Command]],
    ):
        self.bot = bot
        self.ctx = ctx
        self.embeds = embeds
        self.page_index = 0

    def create_buttons(self, disabled: bool = False) -> list[list[Button]]:
        return [
            [
                Button(
                    label="Main Menu",
                    style=ButtonStyle.blue,
                    id="menu",
                    disabled=disabled,
                ),
                Button(
                    label="Back", style=ButtonStyle.blue, id="back", disabled=disabled
                ),
            ],
            [
                Button(
                    label=item.name,
                    style=ButtonStyle.gray,
                    id=f"c{index}",
                    disabled=disabled,
                )
                for index, item in enumerate([])
            ],
        ] + super().create_buttons(disabled=disabled)

    async def menu_events(self, interaction):
        if interaction.component.id == "menu":
            self.position = self.bot
            self.page_index = 0
        elif interaction.component.id == "back":
            self.page_index = 0

        if interaction.component.id.startswith("c"):
            self.page_index = 0

    async def run(self):
        self.message = await self.ctx.send(
            embed=self.embed_pages[self.page_index], components=self.create_buttons()
        )

        while True:
            try:
                interaction = await self.bot.wait_for(
                    "button_click",
                    check=lambda i: i.message == self.message,
                    timeout=180.0,
                )

                if interaction.author.id != self.ctx.author.id:
                    await interaction.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=True,
                        embed=discord.Embed(
                            title="Error",
                            description="You cannot control another user's buttons.",
                            colour=discord.Colour.red(),
                        ),
                    )
                else:
                    await self.pagination_events(interaction)
                    await self.menu_events(interaction)

            except asyncio.TimeoutError:
                await self.message.edit(components=self.create_buttons(disabled=True))
                return


class Settings(commands.Cog, name="settings"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.bot.db.execute(
            "INSERT INTO settings (guild_id) VALUES ($1)",
            guild.id,
        )

    @cog_ext.cog_slash(
        name="settings",
        description="View and edit the settings for the server.",
    )
    async def settings(self, ctx: SlashContext):
        handler = SettingsHandler(ctx)
        handler.run()

    @commands.command(name="settings")
    async def settings_legacy(self, ctx: commands.Context):
        handler = SettingsHandler(ctx)
        handler.run()

    # @cog_ext.cog_slash(
    #     name="listsettings",
    #     description="Get the settings for the server.",
    # )
    # async def listsettings(self, ctx):
    #     record = await self.bot.db.fetchrow(
    #         "SELECT * FROM settings WHERE server_id=$1;", str(ctx.guild.id)
    #     )
    #     server_settings = json.loads(record["json"])
    #     embed = tools.create_embed(ctx, "Bot Settings")
    #     embed.add_field(
    #         name="Starboard",
    #         value=f'**Channel**: {ctx.bot.get_channel(server_settings["starboard"]["channel"])}'
    #         f'**Number Required**: {server_settings["starboard"]["number_required"]}'
    #         f'**Reaction**: {server_settings["starboard"]["reaction"]}',
    #     )
    #     embed.add_field(
    #         name="Suggestions",
    #         value=f'**Channel**: {ctx.bot.get_channel(server_settings["suggestions"]["channel"])}'
    #         f'**Up Emoji**: {server_settings["suggestions"]["up_emoji"]}'
    #         f'**Down Emoji**: {server_settings["suggestions"]["down_emoji"]}',
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="editsettings",
    #     base_desc="Edit the settings for the server.",
    #     subcommand_group="starboard",
    #     sub_group_desc="Edit the settings for the starboard.",
    #     name="channel",
    #     description="Edit the starboard channel.",
    #     options=[
    #         create_option(
    #             name="channel",
    #             description="The new starboard channel.",
    #             option_type=7,
    #             required=True,
    #         ),
    #     ],
    # )
    # async def editsettings_starboard_channel(self, ctx, channel):
    #     if type(channel) == discord.channel.TextChannel:
    #         record = await self.get_record_by_server_id(ctx.guild.id)
    #         server_settings = json.loads(record["json"])
    #         server_settings["starboard"]["channel"] = channel.id
    #         await self.edit_record(ctx.guild.id, json.dumps(server_settings))
    #         embed = tools.create_embed(
    #             ctx,
    #             "Edit Settings",
    #             desc="The starboard channel has been updated successfully.",
    #         )
    #         await ctx.send(embed=embed)
    #     else:
    #         embed = tools.create_error_embed(ctx, "The channel must be a text channel.")
    #         await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="editsettings",
    #     base_desc="Edit the settings for the server.",
    #     subcommand_group="starboard",
    #     sub_group_desc="Edit the settings for the starboard.",
    #     name="numberrequired",
    #     description="Edit the number of stars required to add a message to the starboard.",
    #     options=[
    #         create_option(
    #             name="number",
    #             description="The new number of stars required for the starboard.",
    #             option_type=4,
    #             required=True,
    #         ),
    #     ],
    # )
    # async def editsettings_starboard_numberrequired(self, ctx, number):
    #     record = await self.get_record_by_server_id(ctx.guild.id)
    #     server_settings = json.loads(record["json"])
    #     server_settings["starboard"]["number_required"] = number
    #     await self.edit_record(ctx.guild.id, json.dumps(server_settings))
    #     embed = tools.create_embed(
    #         ctx,
    #         "Edit Settings",
    #         desc="The number of stars required for the starboard has been updated successfully.",
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="editsettings",
    #     base_desc="Edit the settings for the server.",
    #     subcommand_group="starboard",
    #     sub_group_desc="Edit the settings for the starboard.",
    #     name="reaction",
    #     description="Edit the reaction to use for the starboard.",
    #     options=[
    #         create_option(
    #             name="emoji",
    #             description="The new reaction to use for the starboard.",
    #             option_type=3,
    #             required=True,
    #         ),
    #     ],
    # )
    # async def editsettings_starboard_reaction(self, ctx, emoji):
    #     record = await self.get_record_by_server_id(ctx.guild.id)
    #     server_settings = json.loads(record["json"])
    #     server_settings["starboard"]["reaction"] = emoji
    #     await self.edit_record(ctx.guild.id, json.dumps(server_settings))
    #     embed = tools.create_embed(
    #         ctx,
    #         "Edit Settings",
    #         desc="The reaction to use for the starboard has been updated successfully.",
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="editsettings",
    #     base_desc="Edit the settings for the server.",
    #     subcommand_group="dailyreport",
    #     sub_group_desc="Edit the settings for the daily report.",
    #     name="channel",
    #     description="Edit the daily report channel.",
    #     options=[
    #         create_option(
    #             name="channel",
    #             description="The new daily report channel.",
    #             option_type=7,
    #             required=True,
    #         ),
    #     ],
    # )
    # async def editsettings_dailyreport_channel(self, ctx, channel):
    #     if type(channel) == discord.channel.TextChannel:
    #         record = await self.get_record_by_server_id(ctx.guild.id)
    #         server_settings = json.loads(record["json"])
    #         server_settings["starboard"]["channel"] = channel.id
    #         await self.edit_record(ctx.guild.id, json.dumps(server_settings))
    #         embed = tools.create_embed(
    #             ctx,
    #             "Edit Settings",
    #             desc="The daily report channel has been updated successfully.",
    #         )
    #         await ctx.send(embed=embed)
    #     else:
    #         embed = tools.create_error_embed(ctx, "The channel must be a text channel.")
    #         await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="editsettings",
    #     base_desc="Edit the settings for the server.",
    #     subcommand_group="suggestions",
    #     sub_group_desc="Edit the settings for suggestions.",
    #     name="channel",
    #     description="Edit the suggestions channel.",
    #     options=[
    #         create_option(
    #             name="channel",
    #             description="The new suggestions channel.",
    #             option_type=7,
    #             required=True,
    #         ),
    #     ],
    # )
    # async def editsettings_suggestions_channel(self, ctx, channel):
    #     if type(channel) == discord.channel.TextChannel:
    #         record = await self.get_record_by_server_id(ctx.guild.id)
    #         server_settings = json.loads(record["json"])
    #         server_settings["suggestions"]["channel"] = channel.id
    #         await self.edit_record(ctx.guild.id, json.dumps(server_settings))
    #         embed = tools.create_embed(
    #             ctx,
    #             "Edit Settings",
    #             desc="The suggestions channel has been updated successfully.",
    #         )
    #         await ctx.send(embed=embed)
    #     else:
    #         embed = tools.create_error_embed(ctx, "The channel must be a text channel.")
    #         await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="editsettings",
    #     base_desc="Edit the settings for the server.",
    #     subcommand_group="suggestions",
    #     sub_group_desc="Edit the settings for suggestions.",
    #     name="upemoji",
    #     description="Edit the up emoji for suggestions.",
    #     options=[
    #         create_option(
    #             name="emoji",
    #             description="The new up emoji for suggestions.",
    #             option_type=7,
    #             required=True,
    #         ),
    #     ],
    # )
    # async def editsettings_suggestions_upemoji(self, ctx, emoji):
    #     record = await self.get_record_by_server_id(ctx.guild.id)
    #     server_settings = json.loads(record["json"])
    #     server_settings["starboard"]["up_emoji"] = emoji
    #     await self.edit_record(ctx.guild.id, json.dumps(server_settings))
    #     embed = tools.create_embed(
    #         ctx,
    #         "Edit Settings",
    #         desc="The up emoji for suggestions has been updated successfully.",
    #     )
    #     await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="editsettings",
    #     base_desc="Edit the settings for the server.",
    #     subcommand_group="suggestions",
    #     sub_group_desc="Edit the settings for the suggestions.",
    #     name="downemoji",
    #     description="Edit the down emoji for suggestions.",
    #     options=[
    #         create_option(
    #             name="emoji",
    #             description="The new down emoji for suggestions.",
    #             option_type=7,
    #             required=True,
    #         ),
    #     ],
    # )
    # async def editsettings_suggestions_downemoji(self, ctx, emoji):
    #     record = await self.get_record_by_server_id(ctx.guild.id)
    #     server_settings = json.loads(record["json"])
    #     server_settings["starboard"]["down_emoji"] = emoji
    #     await self.edit_record(ctx.guild.id, json.dumps(server_settings))
    #     embed = tools.create_embed(
    #         ctx,
    #         "Edit Settings",
    #         desc="The down emoji for suggestions has been updated successfully.",
    #     )
    #     await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))
