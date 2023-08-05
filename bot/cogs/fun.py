import random

import aiohttp
import discord
import requests
import xkcd
from discord import app_commands
from discord.ext import commands
from thicc import thicc

from bot.helpers import tools


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Greet the bot!", aliases=["hi"])
    async def hello(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=tools.create_embed(
                "Hello!", desc=f"How are you, {ctx.author.mention}?"
            )
        )

    @commands.hybrid_command(description="Ask the ~~magic~~ 8 Ball a question.")
    async def eightball(self, ctx: commands.Context, *, request: str) -> None:
        responses = [
            [
                "🟢 As I see it, yes. 🟢",
                "🟢 It is certain. 🟢",
                "🟢 It is decidedly so. 🟢",
                "🟢 Most likely. 🟢",
                "🟢 Outlook good. 🟢",
                "🟢 Signs point to yes. 🟢",
                "🟢 Without a doubt. 🟢",
                "🟢 Yes. 🟢",
                "🟢 Yes, definitely. 🟢",
                "🟢 You may rely on it. 🟢",
            ],
            [
                "🔴 Very doubtful. 🔴",
                "🔴 My reply is no. 🔴",
                "🔴 My sources say no. 🔴",
                "🔴 Outlook not so good. 🔴",
                "🔴 Don't count on it. 🔴",
            ],
            [
                "🟡 Ask again later. 🟡",
                "🟡 Better not tell you now. 🟡",
                "🟡 Cannot predict now. 🟡",
                "🟡 Concentrate and ask again. 🟡",
                "🟡 Reply hazy, try again. 🟡",
            ],
        ]

        rand_int = random.randint(1, 5)
        if rand_int in [1, 2]:
            response_category = responses[0]
        elif rand_int in [3, 4]:
            response_category = responses[1]
        else:
            response_category = responses[2]

        if ("lying" in request.lower()) or ("lie" in request.lower()):
            response = (
                "🟢 🟡 🔴 How dare you! The magical 8 ball never lies! Shame on you! 🔴 🟡 🟢"
            )
        else:
            response = response_category[random.randint(0, len(response_category) - 1)]
        embed = tools.create_embed("Magic 8 Ball")
        embed.add_field(name="Request", value=request, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        description="Get a random number in a specified range (inclusive)."
    )
    @app_commands.describe(
        min_num="The minimum number in the range.",
        max_num="The maximum number in the range.",
    )
    @commands.cooldown(1, 10)
    async def rng(self, ctx: commands.Context, min_num: int, max_num: int) -> None:
        embed = tools.create_embed(
            "Random Number", desc=f"```{random.randint(min_num, max_num)}```"
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get a dog picture!")
    @commands.cooldown(1, 3)
    async def dog(self, ctx: commands.Context) -> None:
        """Get a dog picture!"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed("Doggo!")
                    embed.set_image(url=js["message"])
                    await ctx.send(embed=embed)

    @commands.hybrid_command(description="Get a cat picture!")
    @commands.cooldown(1, 3)
    async def cat(self, ctx: commands.Context) -> None:
        """Get a cat picture!"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search") as r:
                if r.status == 200:
                    json = await r.json()
                    embed = tools.create_embed("Cat!")
                    embed.set_image(url=json[0]["url"])
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name="xkcd", description="Launch an XKCD browser.")
    async def xkcd_(self, ctx: commands.Context, num: int | None = None) -> None:
        def callback(page: int) -> discord.Embed:
            comic = xkcd.getComic(page + 1)
            embed = tools.create_embed(f"XKCD {page+1}: {comic.getTitle()}")
            embed.set_image(url=comic.getImageLink())
            embed.add_field(name="Alt Text", value=comic.getAltText())
            return embed

        page_idx = num - 1 if num else xkcd.getLatestComicNum() - 1
        view = tools.EmbedButtonPaginator(
            ctx.author, [None] * xkcd.getLatestComicNum(), page_idx, callback
        )
        view.msg = await ctx.send(
            embed=callback(page_idx),
            view=view,
        )

    @commands.hybrid_command(description="Makes text look aesthetic.")
    @app_commands.describe(text="The text to make look aesthetic.")
    async def aes(self, ctx: commands.Context, *, text: str) -> None:
        await ctx.send(thicc.map_string(text))

    @commands.hybrid_command(
        description="Makes text look aesthetic but less cool than aes."
    )
    @app_commands.describe(text="The text to make look aesthetic.")
    async def pooraes(self, ctx: commands.Context, *, text: str) -> None:
        await ctx.send(" ".join(text))

    @commands.hybrid_command(description="Clapping.")
    @app_commands.describe(text="The text to clapify.")
    async def clap(self, ctx: commands.Context, *, text: str) -> None:
        await ctx.send("👏".join(text.split()) if len(text.split()) > 1 else f"👏{text}👏")

    @commands.hybrid_command(description="Clapping but with a custom separator.")
    @app_commands.describe(
        separator="The text to use instead of a clap.", text="The text to clapify."
    )
    async def clapwith(
        self, ctx: commands.Context, separator: str, *, text: str
    ) -> None:
        await ctx.send(
            separator.join(text.split())
            if len(text.split()) > 1
            else f"{separator}{text}{separator}"
        )

    @commands.hybrid_command(description="Get a dad joke.")
    async def dad(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=tools.create_embed(
                "~~bad~~ dad joke",
                desc=requests.get(
                    "https://icanhazdadjoke.com/", headers={"Accept": "text/plain"}
                ).content.decode(),
            )
        )

    @commands.hybrid_command(
        description="Make text dance. Text must be three characters long."
    )
    @app_commands.describe(
        text="The text to make dance. Must be three characters long."
    )
    async def dance(
        self, ctx: commands.Context, text: str = "uwu"
    ) -> None:  # TODO: make this work with other text lengths because why not
        arg = text if len(text) == 3 else "uwu"
        await ctx.send(f"{arg[0]}{arg[1]} {arg[2]}\n{arg[0]} {arg[1]}{arg[2]}\n" * 3)

    @commands.hybrid_command(description="Mock something.")
    @app_commands.describe(text="The text to mock.")
    async def mock(self, ctx: commands.Context, *, text: str) -> None:
        await ctx.send(
            "".join(
                [x.lower() if i % 2 == 0 else x.upper() for i, x in enumerate(text)]
            )
        )

    @commands.hybrid_command(description="Flip a coin!")
    async def coin(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=tools.create_embed("Coin Flip", random.choice(["Heads!", "Tails!"]))
        )

    @commands.hybrid_command(description="Where's my wago?")
    @app_commands.describe(member="The person to ping.")
    async def wago(
        self, ctx: commands.Context, member: discord.Member | None = None
    ) -> None:
        await ctx.send(
            (
                member.mention
                if member
                else random.choice(
                    [
                        member
                        for member in ctx.guild.members
                        if member.status == discord.Status.online
                    ]
                ).mention
            )
            + " Where's my wago?"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
