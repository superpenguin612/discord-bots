import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from bot.helpers import tools
import dotenv
import json
import aiohttp
import random
import xmltodict

class Search(commands.Cog, name='search'):
    def __init__(self, bot):
        self.bot = bot
    
    @cog_ext.cog_subcommand(
        base='picture',
        base_desc='Search Bing for a picture.',
        name='top',
        description='Search Bing for a picture and return the top result.',
        options=[
            create_option(
                name='search_term',
                description='The search term.',
                option_type=3,
                required=True
            )
        ],
        guild_ids=[801630163866746901]
    )
    async def _picture_top(self, ctx, search_term):
        await ctx.respond()
        async with aiohttp.ClientSession() as session:
            dotenv.load_dotenv()
            mkt = 'en-US'
            params = {'q': '+'.join(search_term.split(' ')), 'mkt': mkt, 'safeSearch': 'Strict'}
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
    
    @cog_ext.cog_subcommand(
        base='picture',
        base_desc='Search Bing for a picture.',
        name='num',
        description='Search Bing for a picture and return the result at a certain rank.',
        options=[
            create_option(
                name='number',
                description='The number at which the search is located (1 is 1st, 2 is 2nd). The maximum value is 150.',
                option_type=4,
                required=True
            ),
            create_option(
                name='search_term',
                description='The search term.',
                option_type=3,
                required=True
            )
        ],
        guild_ids=[801630163866746901]
    )
    async def _picture_num(self, ctx, num, search_term):
        await ctx.respond()
        async with aiohttp.ClientSession() as session:
            dotenv.load_dotenv()
            mkt = 'en-US'
            params = {'q': '+'.join(search_term.split(' ')), 'mkt': mkt, 'safeSearch': 'Strict', 'count': 150}
            headers = { 'Ocp-Apim-Subscription-Key': self.bot.AZURE_KEY }
            search_url = "https://api.bing.microsoft.com/v7.0/images/search"
            async with session.get(search_url, headers=headers, params=params) as r:
                js = await r.json()
                if not js['value']:
                    embed = tools.create_error_embed(ctx, 'No results.')
                else:
                    embed = tools.create_embed(ctx, 'Picture!')
                    url = js['value'][num-1]['contentUrl']
                    embed.set_image(url=url)
                await ctx.send(embed=embed)
    
    @cog_ext.cog_subcommand(
        base='picture',
        base_desc='Search Bing for a picture.',
        name='random',
        description='Search Bing for a picture and return the result at a random rank.',
        options=[
            create_option(
                name='search_term',
                description='The search term.',
                option_type=3,
                required=True
            )
        ],
        guild_ids=[801630163866746901]
    )
    async def _picture_random(self, ctx, search_term):
        await ctx.respond()
        async with aiohttp.ClientSession() as session:
            dotenv.load_dotenv()
            mkt = 'en-US'
            params = {'q': '+'.join(search_term.split(' ')), 'mkt': mkt, 'safeSearch': 'Strict'}
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