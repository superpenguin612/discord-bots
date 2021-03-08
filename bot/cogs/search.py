import discord
from discord.ext import commands
from bot.helpers import tools
import dotenv
import json
import aiohttp
import random
import xmltodict

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print([c.qualified_name for c in self.walk_commands()])

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

    async def get_mv_list(self):
        async with aiohttp.ClientSession() as session:
            food_items = []
            search_url = "https://api.mealviewer.com/api/v4/school/CCHSFreshmanCenter/03-08-2021/03-08-2021/"
            async with session.get(search_url) as r:
                js = await r.json()
                food_items.append(js['menuSchedules'][0]['menuBlocks'][0]['cafeteriaLineList']['data'][0]['foodItemList']['data'])
            search_url = "https://api.mealviewer.com/api/v4/school/CCHSGreyhoundStation/03-08-2021/03-08-2021/"
            async with session.get(search_url) as r:
                js = await r.json()
                food_items.append(js['menuSchedules'][0]['menuBlocks'][0]['cafeteriaLineList']['data'][0]['foodItemList']['data'])
            search_url = "https://api.mealviewer.com/api/v4/school/CarmelHigh/03-08-2021/03-08-2021/"
            async with session.get(search_url) as r:
                js = await r.json()
                main_caf = []
                for item in js['menuSchedules'][0]['menuBlocks'][0]['cafeteriaLineList']['data']:
                    main_caf += item['foodItemList']['data']
                food_items.append(main_caf)
            return food_items

    @commands.group()
    async def mealviewer(self, ctx):
        if ctx.invoked_subcommand is None:
            async with aiohttp.ClientSession() as session:
                dotenv.load_dotenv()
                search_url = "https://api.mealviewer.com/api/v4/school/CCHSFreshmanCenter/03-09-2021/03-09-2021/"
                async with session.get(search_url) as r:
                    js = await r.json()
                    food_item = js['menuSchedules'][0]['menuBlocks'][0]['cafeteriaLineList']['data'][0]['foodItemList']['data'][num]
                    # js = xmltodict.parse(xml)
                    embed = tools.create_embed(ctx, 'MealViewer Item')
                    if food_item["imageFileName"]:
                        embed.set_image(url=f'https://appassets.mealviewer.com/fooditemimages/{food_item["imageFileName"]}')
                    embed.add_field(name='Name', value=food_item['item_Name'])
                    embed.add_field(name='Location', value=food_item['physical_Location_Name'])
                    embed.add_field(name='Calories', value=food_item['nutritionals'][0]['value'])
                    embed.add_field(name='Total Fat', value=food_item['nutritionals'][1]['value'])
                    embed.add_field(name='Protein', value=food_item['nutritionals'][5]['value'])
                    await ctx.send(embed=embed)

    @mealviewer.command(name='list')
    async def mealviewer_list(self, ctx):
        food_items = await self.get_mv_list()
        embed = tools.create_embed(ctx, 'MealViewer Items')
        embed.add_field(name='Freshmen Center', value='\n'.join([x['item_Name'] for x in food_items[0]]))
        embed.add_field(name='Greyhound Station', value='\n'.join([x['item_Name'] for x in food_items[1]]))
        embed.add_field(name='Main Cafeteria', value='\n'.join([x['item_Name'] for x in food_items[2]]))
        await ctx.send(embed=embed)
    
    @mealviewer.command(name='item')
    async def mealviewer_item(self, ctx, cafeteria:int, item_number:int):
        food_items = await self.get_mv_list()
        food_item = food_items[cafeteria][item_number]
        embed = tools.create_embed(ctx, 'MealViewer Item')
        if food_item["imageFileName"]:
            embed.set_image(url=f'https://appassets.mealviewer.com/fooditemimages/{food_item["imageFileName"]}')
        embed.add_field(name='Name', value=food_item['item_Name'])
        embed.add_field(name='Location', value=food_item['physical_Location_Name'])
        embed.add_field(name='Calories', value=food_item['nutritionals'][0]['value'])
        embed.add_field(name='Total Fat', value=food_item['nutritionals'][1]['value'])
        embed.add_field(name='Protein', value=food_item['nutritionals'][5]['value'])
        await ctx.send(embed=embed)