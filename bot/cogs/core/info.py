import discord
from discord.ext import commands

from bot.helpers import tools


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        description="Get the latency of the connection between the bot and Discord."
    )
    async def ping(self, ctx: commands.Context) -> None:
        """Get the latency of the connection between the bot and Discord."""
        await ctx.send(
            embed=tools.create_embed(
                "Pong!", desc=f"```{round(self.bot.latency * 1000, 1)}ms```"
            )
        )

    @commands.hybrid_command(description="Get info about the server.")
    async def serverinfo(self, ctx: commands.Context) -> None:
        embed = tools.create_embed("Server Info")
        embed.add_field(name="Name", value=ctx.guild.name, inline=False)
        embed.add_field(name="Owner", value=ctx.guild.owner)
        embed.add_field(name="Channels", value=len(ctx.guild.channels))
        embed.add_field(name="Roles", value=len(ctx.guild.roles))
        embed.add_field(name="Members", value=ctx.guild.member_count)
        embed.add_field(name="ID", value=ctx.guild.id)
        try:
            embed.set_thumbnail(url=str(ctx.guild.icon.url))
        except:
            pass
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get help for the bot.")
    async def help(self, ctx: commands.Context) -> None:
        embeds = []
        commands_list = [
            command
            for command in sorted(
                list(self.bot.walk_commands()), key=lambda command: command.name
            )
            if command.cog_name != "Admin"
        ]
        for commands in [
            commands_list[i : i + 8] for i in range(0, len(commands_list), 8)
        ]:  # splits the commands into groups of 8
            embed = tools.create_embed(title="Bot Commands")
            for command in commands:
                usage = [";" + command.name]
                for name, param in command.params.items():
                    usage += [f"<{name}>" if param.required else f"[{name}]"]
                usage = " ".join(usage)
                embed.add_field(
                    name=usage,
                    value=command.description if command.description else "None",
                    inline=False,
                )
            embeds += [embed]
        view = tools.EmbedButtonPaginator(ctx.author, embeds)
        view.msg = await ctx.send(embed=embeds[0], view=view)

    @commands.hybrid_command(description="Get the link for the repo.")
    async def repo(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=tools.create_embed(
                "Flick's repo", "https://github.com/frc868/flick.py"
            )
        )


async def setup(bot) -> None:
    await bot.add_cog(Info(bot))
