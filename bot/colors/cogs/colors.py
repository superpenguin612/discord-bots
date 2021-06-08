import discord
from discord.ext import commands, tasks
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from bot.helpers import tools
from typing import Optional
import random
import aiohttp


class Colors(commands.Cog, name="colors"):
    COLORS = [
        (255, 62, 62),
        (255, 147, 62),
        (255, 215, 62),
        (133, 255, 62),
        (56, 255, 202),
        (56, 167, 255),
        (173, 56, 255),
        (243, 56, 255),
    ]

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.color = 0
        self.change_color.start()

    def get_rainbow_role(self, guild: discord.Guild) -> Optional[discord.Role]:
        rainbow_role = None
        for role in guild.roles:
            if role.name == "Rainbow":
                rainbow_role = role
        return rainbow_role

    @tasks.loop(seconds=60.0)
    async def change_color(self):
        for guild in self.bot.guilds:
            rainbow_role = self.get_rainbow_role(guild)
            if rainbow_role:
                await rainbow_role.edit(
                    colour=discord.Colour.from_rgb(
                        self.COLORS[self.color][0],
                        self.COLORS[self.color][1],
                        self.COLORS[self.color][2],
                    )
                )
        self.color = self.color + 1 if self.color + 1 <= 7 else 0

    @cog_ext.cog_slash(
        name="createrainbowrole",
        description="Create the rainbow role for the bot to use!",
    )
    @commands.has_permissions(manage_roles=True)
    async def createrainbowrole(self, ctx: SlashContext) -> None:
        rainbow_role = self.get_rainbow_role(ctx.guild)
        if rainbow_role:
            embed = tools.create_error_embed(
                ctx, desc="The rainbow role already exists."
            )
            await ctx.send(embed=embed)
            return

        try:
            await ctx.guild.create_role(
                name="Rainbow",
                colour=discord.Colour.from_rgb(
                    self.COLORS[self.color][0],
                    self.COLORS[self.color][1],
                    self.COLORS[self.color][2],
                ),
            )
        except:
            embed = tools.create_error_embed(ctx, "Could not create the rainbow role.")
            await ctx.send(embed=embed)
        else:
            embed = tools.create_embed(
                ctx,
                "Rainbow Role",
                desc='The rainbow role has been created. Do not rename or delete the role named "Rainbow". It will update every 30 seconds.\n**Make sure to move the bot\'s role above the rainbow role, otherwise it will not be able to change colors.**',
            )
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="deleterainbowrole",
        description="Delete the rainbow role for the server.",
    )
    @commands.has_permissions(manage_roles=True)
    async def deleterainbowrole(self, ctx: SlashContext) -> None:
        rainbow_role = self.get_rainbow_role(ctx.guild)
        if not rainbow_role:
            embed = tools.create_error_embed(ctx, "The rainbow role does not exist.")
            await ctx.send(embed=embed)
            return
        try:
            await rainbow_role.delete()
        except:
            embed = tools.create_error_embed(ctx, "Could not delete the rainbow role.")
            await ctx.send(embed=embed)
        else:
            embed = tools.create_embed(
                ctx,
                "Rainbow Role",
                desc="The rainbow role has been deleted.",
            )
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="botrainbowrole",
        description="Give the bot the rainbow role.",
    )
    @commands.has_permissions(manage_roles=True)
    async def botrole(self, ctx: SlashContext) -> None:
        rainbow_role = self.get_rainbow_role(ctx.guild)
        try:
            await ctx.guild.me.add_roles(rainbow_role)
        except:
            embed = tools.create_error_embed(
                ctx,
                desc="The bot could not be given the rainbow role.",
            )
            await ctx.send(embed=embed)
        else:
            embed = tools.create_embed(
                ctx,
                "Bot Rainbow",
                desc="The bot has been given the rainbow role.",
            )
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="giverainbowrole",
        description="Give yourself the rainbow role.",
    )
    async def giverainbowrole(self, ctx: SlashContext) -> None:
        rainbow_role = self.get_rainbow_role(ctx.guild)
        try:
            await ctx.author.add_roles(rainbow_role)
        except Exception as e:
            print(e)
            embed = tools.create_error_embed(
                ctx,
                desc="You could not be given the rainbow role.",
            )
            await ctx.send(embed=embed)
        else:
            embed = tools.create_embed(
                ctx,
                "User Rainbow",
                desc="You have been given the rainbow role.",
            )
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="removerainbowrole",
        description="Remove the rainbow role from yourself.",
    )
    async def removerainbowrole(self, ctx: SlashContext) -> None:
        rainbow_role = self.get_rainbow_role(ctx.guild)
        try:
            await ctx.author.remove_roles(rainbow_role)
        except:
            embed = tools.create_error_embed(
                ctx,
                desc="The rainbow role could not be removed from you.",
            )
            await ctx.send(embed=embed)
        else:
            embed = tools.create_embed(
                ctx,
                "User Rainbow",
                desc="The rainbow role has been removed from you.",
            )
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="invite",
        description="Invite the bot to another server!",
    )
    async def invite(self, ctx: SlashContext) -> None:
        embed = tools.create_embed(
            ctx,
            "Colors+ Invite",
            desc="Here's an invite for Colors+ (with slash commands and Manage Roles).",
        )
        await ctx.send(
            content="https://discord.com/api/oauth2/authorize?client_id=851852969770090516&permissions=268435456&scope=bot%20applications.commands",
            embed=embed,
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Colors(bot))
