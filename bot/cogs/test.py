import asyncio
import random

import aiohttp
import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, InteractionType
from discord_slash import SlashContext, cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option

from bot.cogs.embeds import ButtonEmbedCreator
from bot.helpers import tools


class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def button(self, ctx: commands.Context) -> None:
        await ctx.send("Hello, World!", components=[Button(label="WOW button!")])

        interaction = await self.bot.wait_for(
            "button_click", check=lambda i: i.component.label.startswith("WOW")
        )
        await interaction.respond(content="Button clicked!")

    @commands.command()
    async def paginator(self, ctx: commands.Context) -> None:
        embeds = [
            discord.Embed(title="page1"),
            discord.Embed(title="page2"),
            discord.Embed(title="page3"),
        ]
        paginator = tools.EmbedButtonPaginator(self.bot, ctx, embeds)
        await paginator.run()

    @commands.command()
    async def sendembedtest(self, ctx: commands.Context) -> None:
        embedcreator = ButtonEmbedCreator(self.bot, ctx, ctx.channel.id)
        await embedcreator.run()

    @commands.command()
    async def nitro(self, ctx: commands.Context, user: discord.User = None) -> None:
        await ctx.message.delete()
        embed = discord.Embed(title="Nitro", description="Expires in 18 hours")
        embed.set_author(name="A WILD GIFT APPEARS!")
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/820637070317060116/856253399225729044/EmSIbDzXYAAb4R7.png"
        )
        EM4 = " "
        if user:
            destination = user
        else:
            destination = ctx

        message = await destination.send(
            embed=embed,
            components=[
                Button(
                    label=(27 * EM4) + "ACCEPT" + (27 * EM4),
                    style=ButtonStyle.green,
                    id="rickroll",
                )
            ],
        )
        while True:
            try:
                interaction = await self.bot.wait_for(
                    "button_click",
                    check=lambda i: i.message.id == message.id,
                    timeout=300.0,
                )

                embed = discord.Embed(
                    description="lol noob imagine getting rickrolled that would be kinda cringe ngl"
                )
                embed.set_image(
                    url="https://media1.tenor.com/images/8c409e6f39acc1bd796e8031747f19ad/tenor.gif"
                )
                await interaction.respond(
                    type=InteractionType.ChannelMessageWithSource,
                    ephemeral=True,
                    embed=embed,
                )

            except asyncio.TimeoutError:
                return


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Test(bot))