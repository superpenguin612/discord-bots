import random

import aiohttp
import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option

from bot.helpers import tools


class FunSlash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="hello", description="Greet the bot!")
    async def hello(self, ctx: commands.Context) -> None:
        embed = tools.create_embed(
            ctx, "Hello!", desc=f"How are you, {ctx.author.mention}?"
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="8ball",
        description="Ask the Magic 8 Ball a question.",
        options=[
            create_option(
                name="request",
                description="Your request for the 8 Ball.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
    )
    async def eightball(self, ctx: SlashContext, request: str) -> None:
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
                "🔴 Don’t count on it. 🔴",
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
        embed = tools.create_embed(ctx, "Magic 8 Ball")
        embed.add_field(name="Request", value=request, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="rng",
        description="Get a random number.",
        options=[
            create_option(
                name="min_num",
                description="Lower boundary for the random number to be in.",
                option_type=SlashCommandOptionType.INTEGER,
                required=True,
            ),
            create_option(
                name="max_num",
                description="Upper boundary for the random number to be in.",
                option_type=4,
                required=True,
            ),
        ],
    )
    # @commands.cooldown(1, 10)
    async def rng(self, ctx: SlashContext, min_num: int, max_num: int) -> None:
        embed = tools.create_embed(
            ctx, "Random Number", desc=f"`{random.randint(min_num, max_num)}`"
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="dog",
        description="Get a dog picture!",
    )
    # @commands.cooldown(1, 3)
    async def dog(self, ctx: SlashContext) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed(ctx, "Doggo!")
                    embed.set_image(url=js["message"])
                    await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="cat", description="Get a cat picture!")
    # @commands.cooldown(1, 3)
    async def cat(self, ctx: SlashContext) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://aws.random.cat/meow") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed(ctx, "Cat!")
                    embed.set_image(url=js["file"])
                    await ctx.send(embed=embed)


class Fun(FunSlash, commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(bot)

    @commands.command(name="hello", brief="Greet the bot!", aliases=["hi"])
    async def hello_legacy(self, ctx: commands.Context) -> None:
        """Greet the bot!
        **Usage**
        `_prefix_pic hello`
        **Parameters**
        None
        **Aliases**
        `_prefix_hi`
        **Cooldown**
        None
        **Permissions Required**
        None
        **Examples**
        `_prefix_pic hello`
        """
        embed = tools.create_embed(
            ctx, "Hello!", desc=f"How are you, {ctx.author.mention}?"
        )
        await ctx.send(embed=embed)

    @commands.command(name="8ball", brief="Ask the Magic 8 Ball a question.")
    async def eightball_legacy(self, ctx: commands.Context, *, request: str) -> None:
        """Ask the Magic 8 Ball a question.
        **Usage**
        `_prefix_8ball <request>`
        **Parameters**
        `<request>`: Your question for the 8 Ball.
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        None
        **Examples**
        `_prefix_8ball am i cool kid?`
        """
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
                "🔴 Don’t count on it. 🔴",
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
        embed = tools.create_embed(ctx, "Magic 8 Ball")
        embed.add_field(name="Request", value=request, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="rng", brief="Get a random number.")
    @commands.cooldown(1, 10)
    async def rng_legacy(self, ctx: commands.Context, minnum: int, maxnum: int) -> None:
        """Get a random number.
        **Usage**
        `_prefix_rng <minnum> <maxnum>`
        **Parameters**
        `<minnum>`: The lower boundary for the random number to be in.
        `<maxnum>`: The upper boundary for the random number to be in.
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        None
        **Examples**
        `_prefix_rng 1 6`
        """
        embed = tools.create_embed(
            ctx, "Random Number", desc=f"`{random.randint(minnum, maxnum)}`"
        )
        await ctx.send(embed=embed)

    @commands.command(name="dog", brief="Get a dog picture!")
    @commands.cooldown(1, 3)
    async def dog_legacy(self, ctx: commands.Context) -> None:
        """Get a dog picture!
        **Usage**
        `_prefix_dog`
        **Parameters**
        None
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        None
        **Examples**
        `_prefix_dog`
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed(ctx, "Doggo!")
                    embed.set_image(url=js["message"])
                    await ctx.send(embed=embed)

    @commands.command(name="cat", brief="Get a cat picture!")
    @commands.cooldown(1, 3)
    async def cat_legacy(self, ctx: commands.Context) -> None:
        """Get a cat picture!
        **Usage**
        `_prefix_cat`
        **Parameters**
        None
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        None
        **Examples**
        `_prefix_cat`
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("http://aws.random.cat/meow") as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed(ctx, "Cat!")
                    embed.set_image(url=js["file"])
                    await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Fun(bot))