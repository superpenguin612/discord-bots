import asyncio
import math
import re
from typing import Union
from collections import OrderedDict

import discord
from discord.ext import commands

# from discord_components import Button, ButtonStyle, InteractionType
from discord_slash.context import ComponentContext, SlashContext
from discord_slash.utils.manage_components import (
    create_button,
    create_actionrow,
    create_select,
    create_select_option,
    wait_for_component,
)
from discord_slash.model import ButtonStyle
from bot.helpers import tools


class Help(commands.Cog, name="help"):
    """Group of help commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def create_bot_help(
        self, ctx: commands.Context
    ) -> OrderedDict[discord.Embed, list[commands.Cog]]:
        od = OrderedDict()
        number_of_embeds = math.ceil(
            len(self.bot.cogs.values()) / 5
        )  # Five cogs per page
        for i in range(number_of_embeds):
            embed = tools.create_embed(ctx, "Bot Commands", desc=self.bot.description)
            cogs = list(self.bot.cogs.values())[(i * 5) : ((i + 1) * 5)]
            for cog in cogs:
                if "slash" not in cog.qualified_name.lower():
                    embed.add_field(
                        name=f"{cog.qualified_name.title()} Commands",
                        # value=cog.description[2:],
                        value="hmmm",
                        inline=False,
                    )
            od[embed] = cogs

        return od

    def create_cog_help(
        self, ctx: commands.Context, cog: commands.Cog
    ) -> OrderedDict[discord.Embed, list[commands.Command]]:
        commands_list = [
            command
            for command in cog.walk_commands()
            if not isinstance(command, commands.Group)
        ]  # Variable name changed from commands to commands_list because of collision with discord.ext.commands
        od = OrderedDict()
        number_of_embeds = math.ceil(len(commands_list) / 5)  # Five commands per page
        for i in range(number_of_embeds):
            embed = tools.create_embed(
                ctx, f"{cog.qualified_name.title()} Commands", desc=cog.description[2:]
            )
            commands_list_section = list(
                commands_list[((i + 1) * 5) - 5 : ((i + 1) * 5) - 1]
            )
            for command in commands_list_section:
                if "slash" not in cog.qualified_name.lower():
                    embed.add_field(
                        name=f"{ctx.prefix}{command.qualified_name}",
                        value=command.short_doc
                        if command.short_doc
                        else "No help text.",
                        inline=False,
                    )
            od[embed] = commands_list_section
        return od

    # def create_command_help(
    #     self, ctx: commands.Context, command: commands.Command
    # ) -> discord.Embed:
    #     embed = tools.create_embed(
    #         ctx,
    #         f"{ctx.prefix}{command.qualified_name}{command.signature}",
    #         desc=command.description,
    #     )

    #     if command.help:
    #         prefixed_help = re.sub("_prefix_", ctx.prefix, command.help)
    #         embed.add_field(name="Help Text", value=prefixed_help)
    #     return embed

    @commands.command()
    async def help(self, ctx: commands.Context, *, query=None) -> None:
        cog_map = dict(self.bot.cogs)
        command_map = {command.name: command for command in self.bot.commands}

        embeds = []
        embeds.append({self.bot: self.create_bot_help(ctx)})
        embeds.append({})
        for cog in cog_map.values():
            embeds[1][cog] = self.create_cog_help(ctx, cog)

        # embeds.append({})
        # for command in command_map.values():
        #     embeds[2][command] = self.create_command_help(ctx, command)

        start_point = (
            self.bot
            if query == None
            else cog_map[query]
            if cog_map.get(query) != None
            else command_map[query]
            if command_map.get(query) != None
            else self.bot
        )

        help = HelpHandler(
            self.bot,
            ctx,
            embeds,
            # hierarchy,
            start_point,
            not_found=False if start_point != None else True,
        )
        await help.run()


class HelpHandler(tools.EmbedButtonPaginator):
    """Handles pagination around the help menu."""

    BOT_LEVEL = 0
    COG_LEVEL = 1
    # COMMAND_LEVEL = 2
    # LEVELS = {commands.Bot: 0, commands.Cog: 1, commands.Command: 2}

    def __init__(
        self,
        bot: commands.Bot,
        ctx: Union[commands.Context, SlashContext],
        bot_embed: discord.Embed,
        cog_embeds: dict[commands.Cog, discord.Embed],
        all_embed: discord.Embed,
        start_point: Union[commands.Bot, commands.Cog, commands.Command],
        not_found: bool = False,
    ):
        self.bot = bot
        self.ctx = ctx
        self.bot_embed = bot_embed
        self.cog_embeds = cog_embeds
        self.all_embeds = all_embed
        self.page_index = 0
        self.position = start_point
        self.not_found = not_found
        self.embed_pages = self.embeds[self.level][self.position]

    def create_buttons(self, disabled: bool = False) -> list[dict]:
        self.current_buttons = list(self.embeds[self.level][self.position].values())[
            self.page_index
        ]

        return (
            create_actionrow(
                create_select(
                    options=[],
                    custom_id="select",
                    placeholder="Select the category of commands you want to view.",
                    min_values=1,
                    max_values=1,
                )
            )
            + super().create_buttons(disabled=disabled)
            + [
                create_actionrow(
                    create_button(
                        label="Main Menu",
                        style=ButtonStyle.blue,
                        custom_id="menu",
                        disabled=disabled,
                    ),
                    create_button(
                        label="Back",
                        style=ButtonStyle.blue,
                        custom_id="back",
                        disabled=disabled,
                    ),
                ),
                create_actionrow(
                    *[  # * unpacks the list into the *components of create_actionrow
                        create_button(
                            label=item.qualified_name,
                            style=ButtonStyle.gray,
                            custom_id=f"c{index}",
                            disabled=disabled,
                        )
                        for index, item in enumerate(
                            list(self.embeds[self.level][self.position].values())[
                                self.page_index
                            ]
                        )
                    ]
                ),
            ]
        )

    async def pagination_events(self, component_ctx: ComponentContext):
        if component_ctx.custom_id == "first":
            self.page_index = 0
        elif component_ctx.custom_id == "prev":
            if self.page_index > 0:
                self.page_index -= 1
        elif component_ctx.custom_id == "next":
            if self.page_index < len(list(self.embed_pages)) - 1:
                self.page_index += 1

        elif component_ctx.custom_id == "last":
            self.page_index = len(list(self.embed_pages)) - 1

    async def menu_events(self, component_ctx: ComponentContext):
        if component_ctx.custom_id == "menu":
            self.position = self.bot
            self.page_index = 0
        elif component_ctx.custom_id == "back":
            self.page_index = 0
            self.level -= 1
        if component_ctx.custom_id.startswith("c"):
            self.level += 1
            self.position = self.current_buttons[int(component_ctx.custom_id[1])]
            self.page_index = 0
            self.embed_pages = list(self.embeds[self.level][self.position])

    async def run(self):
        self.message = await self.ctx.send(
            embed=list(self.embed_pages)[self.page_index],
            components=self.create_buttons(),
        )

        while True:
            try:
                component_ctx: ComponentContext = await wait_for_component(
                    self.bot,
                    messages=self.message,
                    timeout=180.0,
                )
                if component_ctx.author.id != self.ctx.author.id:
                    await component_ctx.send(
                        hidden=True,
                        embed=discord.Embed(
                            title="Error",
                            description="You can't control another member's buttons.",
                            colour=discord.Colour.red(),
                        ),
                    )
                else:
                    await self.pagination_events(component_ctx)
                    await self.menu_events(component_ctx)

                    await component_ctx.edit_origin(
                        embed=list(self.embed_pages)[self.page_index],
                        components=self.create_buttons(),
                    )

            except asyncio.TimeoutError:
                await self.message.edit(components=self.create_buttons(disabled=True))
                return


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Help(bot))
