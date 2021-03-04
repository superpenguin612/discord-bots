import discord
from discord.ext import commands
from bot.helpers import tools
import dotenv
import json
import aiohttp
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.group()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def pic(self, ctx):
        """Get any picture!"""
        if ctx.invoked_subcommand is None:
            embed = tools.create_embed(ctx, 'Picture', desc=f'Please specify a category for your picture request.\nThe available categories are `top`, `random`, and `num`.\nThe command\'s usage is `{ctx.prefix}pic <category> <request>`')
            await ctx.send(embed=embed)
    
    @pic.command(name='top')
    async def pic_top(self, ctx, *, arg):
        """Get any picture!"""
        async with aiohttp.ClientSession() as session:
            dotenv.load_dotenv()
            mkt = 'en-US'
            params = {'q': '+'.join(arg.split(' ')), 'mkt': mkt, 'safeSearch': 'Strict'}
            headers = { 'Ocp-Apim-Subscription-Key': self.bot.AZURE_KEY }
            search_url = "https://api.bing.microsoft.com/v7.0/images/search"
            async with session.get(search_url, headers=headers, params=params) as r:
                js = await r.json()
                print(js)
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
                with open('test.json', 'w') as f:
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