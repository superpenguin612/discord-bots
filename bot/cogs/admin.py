import logging
import subprocess

import discord
from discord.ext import commands

import bot.cogs.techhounds
import bot.cogs.custom.chsbot
from bot.helpers import tools


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.LoggerAdapter(
            logging.getLogger(__name__), {"botname": self.bot.name}
        )

    def admin_access(ctx: commands.Context) -> bool:
        # superpenguin612#4406, acr#7356
        return ctx.author.id in [688530998920871969, 321378326273064961]

    @commands.command()
    @commands.check(admin_access)
    async def prepareroleselector(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> None:
        embed = discord.Embed(
            description="\n".join(
                [
                    "## Get your desired roles here!",
                    "### <@&705065841737072740>",
                    "- You will be pinged for important school notices, news, emails, etc in <#707967554169208873>.\n"
                    "### <@&713502413335822336>",
                    "- You will be pinged for major server updates/changes in <#710521718334161057>\n"
                    "### <@&710957162167402558>",
                    "- Access to homework help channel, where you may ask your fellow peers for help.\n",
                ]
            ),
            colour=discord.Colour.from_str("#FBBF05"),
        )

        await channel.send(
            embed=embed,
            view=bot.cogs.custom.chsbot.create_persistent_role_selector(
                self.bot.get_guild(704819543398285383)
            ),
        )

    # @commands.command()
    # @commands.check(admin_access)
    # async def preparename(
    #     self, ctx: commands.Context, channel: discord.TextChannel
    # ) -> None:
    #     embed = discord.Embed(
    #         title="Nickname",
    #         description="Please press the button below to set your nickname.",
    #         colour=discord.Colour.from_str("#FBBF05"),
    #     )

    # await channel.send(embed=embed, view=bot.cogs.techhounds.NameView())

    # @commands.command()
    # @commands.check(admin_access)
    # async def preparepronoun(
    #     self, ctx: commands.Context, channel: discord.TextChannel
    # ) -> None:
    #     embed = discord.Embed(
    #         title="Pronouns",
    #         description="Please select your pronouns if you feel comfortable doing so.",
    #         colour=discord.Colour.from_str("#FBBF05"),
    #     )

    #     await channel.send(
    #         embed=embed,
    #         view=bot.cogs.techhounds.create_persistent_pronoun_selector(
    #             self.bot.get_guild(403364109409845248)
    #         ),
    #     )

    # @commands.command()
    # @commands.check(admin_access)
    # async def preparegradelevel(
    #     self, ctx: commands.Context, channel: discord.TextChannel
    # ) -> None:
    #     embed = discord.Embed(
    #         title="Grade Level",
    #         description="Please select your grade level.",
    #         colour=discord.Colour.from_str("#FBBF05"),
    #     )

    #     await channel.send(
    #         embed=embed,
    #         view=bot.cogs.techhounds.create_persistent_grade_level_selector(
    #             self.bot.get_guild(403364109409845248)
    #         ),
    #     )

    @commands.command()
    @commands.check(admin_access)
    async def eval(self, ctx: commands.Context, *, arg: str) -> None:
        await ctx.send(eval(arg))

    @commands.command()
    @commands.check(admin_access)
    async def sync(self, ctx: commands.Context) -> None:
        await self.bot.tree.sync()
        await ctx.send("Synced application commands.")

    @commands.command()
    @commands.check(admin_access)
    async def gitpull(self, ctx: commands.Context) -> None:
        await ctx.send("Pulling from Git.")
        await ctx.send(
            subprocess.run(
                "git pull", shell=True, text=True, capture_output=True
            ).stdout
        )

    @commands.command()
    @commands.check(admin_access)
    async def reload(self, ctx: commands.Context) -> None:
        await ctx.send("Reloading bot.")
        self.logger.info("Reloading bot.")
        extensions = [name for name, extension in self.bot.extensions.items()]
        for extension in extensions:
            self.logger.info(f"Reloading {extension}.")
            await self.bot.reload_extension(extension)

        await ctx.send("Reloading complete.")

    @commands.command()
    @commands.check(admin_access)
    async def update(self, ctx: commands.Context) -> None:
        await self.gitpull(ctx)
        await self.reload(ctx)

    @commands.command()
    @commands.check(admin_access)
    async def updatewebsite(self, ctx: commands.Context) -> None:
        await ctx.send("Pulling from Git.")
        await ctx.send(
            subprocess.run(
                "git pull",
                shell=True,
                text=True,
                capture_output=True,
                cwd="/opt/website",
            ).stdout
        )

        await ctx.send("Deploying to /var/www/html.")
        subprocess.run(
            "./deploy.sh",
            shell=True,
            text=True,
            capture_output=True,
            cwd="/home/dr",
        )
        await ctx.send("Deployed.")

    @commands.command()
    @commands.check(admin_access)
    async def sync(self, ctx: commands.Context) -> None:
        await self.bot.tree.sync()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
