import discord
from discord.ext import commands
from bot.helpers import tools
import random
import aiohttp


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["hi"])
    async def hello(self, ctx):
        """Greet the bot!"""
        embed = tools.create_embed(ctx, 'Hello!', desc=f'How are you, {ctx.author.mention}?')
        await ctx.send(embed=embed)
    
    @commands.command(name='8ball')
    async def eightball(self, ctx, *, request):
        """Consult the Magic 8 Ball. It is never wrong!"""
        responses = [
            [
                '🟢 As I see it, yes. 🟢',
                '🟢 It is certain. 🟢',
                '🟢 It is decidedly so. 🟢',
                '🟢 Most likely. 🟢',
                '🟢 Outlook good. 🟢',
                '🟢 Signs point to yes. 🟢',
                '🟢 Without a doubt. 🟢',
                '🟢 Yes. 🟢',
                '🟢 Yes, definitely. 🟢',
                '🟢 You may rely on it. 🟢'
            ],
            [
                '🔴 Very doubtful. 🔴',
                '🔴 My reply is no. 🔴',
                '🔴 My sources say no. 🔴',
                '🔴 Outlook not so good. 🔴',
                '🔴 Don’t count on it. 🔴',
            ],
            [
                '🟡 Ask again later. 🟡',
                '🟡 Better not tell you now. 🟡',
                '🟡 Cannot predict now. 🟡',
                '🟡 Concentrate and ask again. 🟡',
                '🟡 Reply hazy, try again. 🟡',
            ],
        ]
        rand_int = random.randint(1,5)
        if rand_int in [1, 2]:
            response_category = responses[0]
        elif rand_int in [3, 4]:
            response_category = responses[1]
        else:
            response_category = responses[2]

        if ("lying" in request.lower()) or ("lie" in request.lower()):
            response = "🟢 🟡 🔴 How dare you! The magical 8 ball never lies! Shame on you! 🔴 🟡 🟢"
        else:
            response = response_category[random.randint(0, len(response_category)-1)]
        embed = tools.create_embed(ctx, 'Magic 8 Ball')
        embed.add_field(name='Request', value=request, inline=False)
        embed.add_field(name='Answer', value=response, inline=False)
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, 10)
    async def rng(self, ctx, minnum:int, maxnum: int):
        """Get a random number!"""
        embed = tools.create_embed(ctx, 'Random Number', desc=f'`{random.randint(minnum, maxnum)}`')
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, 3)
    async def dog(self, ctx):
        """Get a dog picture!"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dog.ceo/api/breeds/image/random') as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed(ctx, 'Doggo!')
                    embed.set_image(url=js['message'])
                    await ctx.send(embed=embed)
    
    @commands.command()
    @commands.cooldown(1, 3)
    async def cat(self, ctx):
        """Get a cat picture!"""
        async with aiohttp.ClientSession() as session:
            async with session.get('http://aws.random.cat/meow') as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed(ctx, 'Cat!')
                    embed.set_image(url=js['file'])
                    await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 1)
    async def pic(self, ctx, *, arg):
        """Get any picture!"""
        url_req = f'https://customsearch.googleapis.com/customsearch/v1?q={"+".join(arg.split(" "))}&searchtype=image&safe=active&cx=b56bd460ede944aef&key=AIzaSyATNnIQUjg9P4IYQJMs_QvWnMaaDVlT1PY'
        async with aiohttp.ClientSession() as session:
            async with session.get(url_req) as r:
                if r.status == 200:
                    js = await r.json()
                    embed = tools.create_embed(ctx, 'Picture!')
                    url = None
                    while not url:
                        try:
                            url=js['items'][random.randint(0,9)]['pagemap']['cse_image'][0]['src']
                        except KeyError:
                            pass
                    embed.set_image(url=url)
                    await ctx.send(embed=embed)
