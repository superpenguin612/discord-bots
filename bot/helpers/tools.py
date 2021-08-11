import asyncio
from typing import Union

import discord
from discord.ext import commands
from discord_slash.context import ComponentContext, SlashContext
from discord_slash.utils.manage_components import (
    create_button,
    create_actionrow,
    create_select,
    create_select_option,
    wait_for_component,
)
from discord_slash.model import ButtonStyle, ComponentType


def create_embed(
    ctx: Union[commands.Context, SlashContext],
    title: str,
    desc: str = "",
    url: str = None,
    color: discord.Colour = None,
    footer_enabled: bool = True,
) -> discord.Embed:
    if not color:
        color = discord.Embed.Empty
    embed = discord.Embed(title=title, description=desc, color=color)
    if url:
        embed.url = url
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    if footer_enabled:
        if ctx.channel.type is not discord.ChannelType.private:
            embed.set_footer(
                text=f"Server: {ctx.guild} | Command: {ctx.command}",
                icon_url=ctx.guild.icon_url,
            )
        else:
            embed.set_footer(text=f"Server: DMs | Command: {ctx.command}")
    return embed


def create_error_embed(
    ctx: Union[commands.Context, SlashContext], desc: str
) -> discord.Embed:
    color = discord.Color.red()
    embed = discord.Embed(title="Error", description=desc, color=color)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    if ctx.channel.type is not discord.ChannelType.private:
        embed.set_footer(
            text=f"Server: {ctx.guild} | Command: {ctx.command}",
            icon_url=ctx.guild.icon_url,
        )
    else:
        embed.set_footer(text=f"Server: DMs | Command: {ctx.command}")
    return embed


class EmbedReactionPaginator:
    REACTIONS = {"first": "⏮", "back": "◀️", "forward": "▶️", "last": "⏭", "stop": "⏹"}

    def __init__(
        self,
        bot: commands.Bot,
        ctx: Union[commands.Context, SlashContext],
        embeds: list,
    ):
        self.ctx = ctx
        self.bot = bot
        self.embed_pages = embeds
        self.page_index = 0

    async def run(self):
        self.message = await self.ctx.send(embed=self.embed_pages[self.page_index])

        def check(reaction, user):
            return (
                reaction.message.id == self.message.id and user.id == self.ctx.author.id
            )

        for reaction in self.REACTIONS.values():
            await self.message.add_reaction(reaction)

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=180
                )
            except asyncio.TimeoutError:
                await self.message.clear_reactions()
                return

            if reaction.emoji == self.REACTIONS["first"]:
                self.page_index = 0
            elif reaction.emoji == self.REACTIONS["back"]:
                if self.page_index > 0:
                    self.page_index -= 1
            elif reaction.emoji == self.REACTIONS["forward"]:
                if self.page_index < len(self.embed_pages) - 1:
                    self.page_index += 1
            elif reaction.emoji == self.REACTIONS["last"]:
                self.page_index = len(self.embed_pages) - 1
            elif reaction.emoji == self.REACTIONS["stop"]:
                await self.message.delete()
                return

            await self.message.edit(embed=self.embed_pages[self.page_index])
            await reaction.remove(user)


class EmbedButtonPaginator:
    def __init__(
        self,
        bot: commands.Bot,
        ctx: Union[commands.Context, SlashContext],
        embeds: list[discord.Embed],
    ):
        self.bot = bot
        self.ctx = ctx
        self.embed_pages = embeds
        self.page_index = 0

    def create_buttons(self, disabled: bool = False) -> list[dict]:
        return [
            create_actionrow(
                create_button(
                    label="First",
                    style=ButtonStyle.green,
                    custom_id="first",
                    disabled=disabled,
                ),
                create_button(
                    label="Prev",
                    style=ButtonStyle.blue,
                    custom_id="prev",
                    disabled=disabled,
                ),
                create_button(
                    label=f"Page {self.page_index+1}/{len(self.embed_pages)}",
                    style=ButtonStyle.gray,
                    custom_id="pagenum",
                    disabled=True,
                ),
                create_button(
                    label="Next",
                    style=ButtonStyle.blue,
                    custom_id="next",
                    disabled=disabled,
                ),
                create_button(
                    label="Last",
                    style=ButtonStyle.green,
                    custom_id="last",
                    disabled=disabled,
                ),
            ),
        ]

    async def pagination_events(self, component_ctx: ComponentContext):
        if component_ctx.custom_id == "first":
            self.page_index = 0
        elif component_ctx.custom_id == "prev":
            if self.page_index > 0:
                self.page_index -= 1
        elif component_ctx.custom_id == "next":
            if self.page_index < len(self.embed_pages) - 1:
                self.page_index += 1
        elif component_ctx.custom_id == "last":
            self.page_index = len(self.embed_pages) - 1

    async def run(self):
        self.message = await self.ctx.send(
            embed=self.embed_pages[self.page_index], components=self.create_buttons()
        )

        while True:
            try:
                component_ctx: ComponentContext = await wait_for_component(
                    self.bot,
                    messages=self.message,
                    components=["first", "prev", "next", "last", "stop"],
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

                await component_ctx.edit_origin(
                    embed=self.embed_pages[self.page_index],
                    components=self.create_buttons(),
                )

            except asyncio.TimeoutError:
                await self.message.edit(components=self.create_buttons(disabled=True))
                return
