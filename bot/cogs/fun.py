import discord
from discord.ext import commands
from bot.helpers import tools
import random
import aiohttp
import os
import dotenv
import json

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

    @commands.group()
    @commands.cooldown(1, 10)
    async def pic(self, ctx):
        """Get any picture!"""
        if ctx.invoked_subcommand is None:
            embed = tools.create_embed(ctx, 'Picture', desc=f'Please specify a category for your picture request.\nThe available categories are `top`, `random`, and `num`.\nThe command\'s usage is `{ctx.prefix}pic <category> <request>`')
            await ctx.send(embed=embed)
    
    @pic.command(name='top')
    async def pic_top(self, ctx, *, arg):
        """Get any picture!"""
        # url_req = f'https://customsearch.googleapis.com/customsearch/v1?q={"+".join(arg.split(" "))}&searchType=image&safe=active&cx=b56bd460ede944aef&key=AIzaSyATNnIQUjg9P4IYQJMs_QvWnMaaDVlT1PY'
        async with aiohttp.ClientSession() as session:
            dotenv.load_dotenv()
            mkt = 'en-US'
            params = {'q': '+'.join(arg.split(' ')), 'mkt': mkt, 'safeSearch': 'Strict'}
            headers = { 'Ocp-Apim-Subscription-Key': self.bot.AZURE_KEY }
            search_url = "https://api.bing.microsoft.com/v7.0/images/search"
            async with session.get(search_url, headers=headers, params=params) as r:
                js = await r.json()
                if not js['value']:
                    embed = tools.create_error_embed(ctx, 'No results.')
                else:
                    embed = tools.create_embed(ctx, 'Picture!')
                    url = js['value'][0]['contentUrl']
                    embed.set_image(url=url)
                await ctx.send(embed=embed)
    
    @pic.command(name='num')
    async def pic_num(self, ctx, num:int, *, arg):
        """Get any picture!"""
        # url_req = f'https://customsearch.googleapis.com/customsearch/v1?q={"+".join(arg.split(" "))}&searchType=image&safe=active&cx=b56bd460ede944aef&key=AIzaSyATNnIQUjg9P4IYQJMs_QvWnMaaDVlT1PY'
        async with aiohttp.ClientSession() as session:
            dotenv.load_dotenv()
            mkt = 'en-US'
            params = {'q': '+'.join(arg.split(' ')), 'mkt': mkt, 'safeSearch': 'Strict', 'count': 150}
            headers = { 'Ocp-Apim-Subscription-Key': self.bot.AZURE_KEY }
            search_url = "https://api.bing.microsoft.com/v7.0/images/search"
            async with session.get(search_url, headers=headers, params=params) as r:
                js = await r.json()
                with open('test.txt', 'w') as f:
                    json.dump(js, f)
                if not js['value']:
                    embed = tools.create_error_embed(ctx, 'No results.')
                else:
                    embed = tools.create_embed(ctx, 'Picture!')
                    url = js['value'][num]['contentUrl']
                    embed.set_image(url=url)
                await ctx.send(embed=embed)
    
    @pic.command(name='random')
    async def pic_rand(self, ctx, *, arg):
        """Get any picture!"""
        # url_req = f'https://customsearch.googleapis.com/customsearch/v1?q={"+".join(arg.split(" "))}&searchType=image&safe=active&cx=b56bd460ede944aef&key=AIzaSyATNnIQUjg9P4IYQJMs_QvWnMaaDVlT1PY'
        async with aiohttp.ClientSession() as session:
            dotenv.load_dotenv()
            mkt = 'en-US'
            params = {'q': '+'.join(arg.split(' ')), 'mkt': mkt, 'safeSearch': 'Strict'}
            headers = { 'Ocp-Apim-Subscription-Key': self.bot.AZURE_KEY }
            search_url = "https://api.bing.microsoft.com/v7.0/images/search"
            async with session.get(search_url, headers=headers, params=params) as r:
                js = await r.json()
                if not js['value']:
                    embed = tools.create_error_embed(ctx, 'No results.')
                else:
                    embed = tools.create_embed(ctx, 'Picture!')
                    url = js['value'][random.randint(0,34)]['contentUrl']
                    embed.set_image(url=url)
                await ctx.send(embed=embed)