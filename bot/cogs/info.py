import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
import random


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="ping",
        description="Get the latency of the connection between the bot and Discord.",
    )
    async def ping(self, ctx: SlashContext) -> None:
        embed = tools.create_embed(
            ctx, "Pong!", desc=f"`{round(self.bot.latency * 1000, 1)}ms`"
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="about",
        description="View information about the bot.",
    )
    async def about(self, ctx: SlashContext) -> None:
        embed = tools.create_embed(ctx, "About")
        author = await ctx.guild.fetch_member(688530998920871969)
        embed.add_field(name="Author", value=f"{author.mention}", inline=False)
        embed.add_field(name="Language", value="Python", inline=False)
        embed.add_field(name="Version", value="1.4", inline=False)
        embed.add_field(
            name="GitHub", value="https://github.com/davidracovan/discord-bots"
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="help",
        description="Get help for the bot.",
    )
    async def help(self, ctx: SlashContext) -> None:
        embed = tools.create_embed(
            ctx,
            "Bot Help",
            "Welcome to the Slash Commands module of CHS Bot! This is a new feature created by Discord allowing members to use bots more effectively. Thanks for using the bot!",
        )
        embed.add_field(
            name="How to Use",
            value="Slash Commands are simple to use! Just type a `/` to see a list of all CHS Bot commands.\n"
            "Press `Tab` whenever the `TAB` icon appears in the message bar to auto-complete the selected command and to complete a command parameter.\n"
            "Explanation text will show for each parameter for a command. If a parameter is optional, it will not appear by default. Press `Tab` when an optional parameter is highlighted to add a value for it.",
            inline=False,
        )
        embed.add_field(
            name='"This Interaction Failed"',
            value="If this message appears, it means that the bot is most likely offline. Commands will still appear when the bot is offline, but they won't be runnable. If the bot isn't offline, ping the Developer role for help.",
            inline=False,
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="server",
        base_desc="Get information related to the server.",
        name="info",
        description="Get server info.",
    )
    async def server_info(self, ctx: SlashContext) -> None:
        embed = tools.create_embed(ctx, "Server Info")
        embed.add_field(name="Name", value=ctx.guild.name, inline=False)
        embed.add_field(name="Owner", value=ctx.guild.owner)
        embed.add_field(name="Channels", value=len(ctx.guild.channels))
        embed.add_field(name="Roles", value=len(ctx.guild.roles))
        embed.add_field(name="Members", value=ctx.guild.member_count)
        embed.add_field(name="ID", value=ctx.guild.id)
        embed.set_thumbnail(url=str(ctx.guild.icon_url))
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="server",
        base_desc="Get information related to the server.",
        name="roles",
        description="Get server roles.",
    )
    async def server_roles(self, ctx: SlashContext) -> None:
        embed = tools.create_embed(
            ctx,
            "Server Roles",
            "\n".join(reversed([role.mention for role in ctx.guild.roles])),
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="server",
        base_desc="Get information related to the server.",
        name="channels",
        description="Get server channels.",
    )
    async def server_channels(self, ctx: SlashContext) -> None:
        embed = tools.create_embed(
            ctx,
            "Server Channels",
        )
        embed.add_field(
            name="Categories",
            value=len([category for category in ctx.guild.categories]),
        )
        embed.add_field(
            name="Text Channels",
            value=len([channel for channel in ctx.guild.text_channels])
            if ctx.guild.text_channels
            else None,
        )
        embed.add_field(
            name="Voice Channels",
            value=len([channel for channel in ctx.guild.voice_channels])
            if ctx.guild.voice_channels
            else None,
        )
        embed.add_field(
            name="Stage Channels",
            value=len([channel for channel in ctx.guild.stage_channels])
            if ctx.guild.stage_channels
            else None,
        )

        await ctx.send(embed=embed)

    # --------------------------------------------
    # LEGACY COMMANDS
    # --------------------------------------------

    @commands.command(name="ping")
    async def ping_legacy(self, ctx: commands.Context) -> None:
        """Get the latency of the connection between the bot and Discord."""
        embed = tools.create_embed(
            ctx, "Pong!", desc=f"`{round(self.bot.latency * 1000, 1)}ms`"
        )
        await ctx.send(embed=embed)

    @commands.command(name="about")
    async def about_legacy(self, ctx: commands.Context) -> None:
        """View information about the bot."""
        embed = tools.create_embed(ctx, "About")
        author = await ctx.guild.fetch_member(688530998920871969)
        embed.add_field(name="Author", value=f"{author.mention}", inline=False)
        embed.add_field(name="Language", value="Python", inline=False)
        embed.add_field(name="Version", value="1.4", inline=False)
        embed.add_field(
            name="GitHub", value="https://github.com/davidracovan/discord-bots"
        )
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
