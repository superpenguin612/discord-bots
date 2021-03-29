import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from bot.helpers import tools
import dotenv
import json
import aiohttp
import random
import xmltodict
import datetime

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
            ),
        ],
    )
    async def picture_top(self, ctx, search_term):
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
            ),
        ],
    )
    async def picture_num(self, ctx, num, search_term):
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
            ),
        ],
    )
    async def picture_random(self, ctx, search_term):
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

    async def get_mv_list(self, date):
        async with aiohttp.ClientSession() as session:
            food_items = []
            search_url = f"https://api.mealviewer.com/api/v4/school/CCHSFreshmanCenter/{date}/{date}/"
            async with session.get(search_url) as r:
                js = await r.json()
                food_items.append(js['menuSchedules'][0]['menuBlocks'][0]['cafeteriaLineList']['data'][0]['foodItemList']['data'])
            search_url = f"https://api.mealviewer.com/api/v4/school/CCHSGreyhoundStation/{date}/{date}/"
            async with session.get(search_url) as r:
                js = await r.json()
                food_items.append(js['menuSchedules'][0]['menuBlocks'][0]['cafeteriaLineList']['data'][0]['foodItemList']['data'])
            search_url = f"https://api.mealviewer.com/api/v4/school/CarmelHigh/{date}/{date}/"
            async with session.get(search_url) as r:
                js = await r.json()
                main_caf = []
                for item in js['menuSchedules'][0]['menuBlocks'][0]['cafeteriaLineList']['data']:
                    main_caf += item['foodItemList']['data']
                food_items.append(main_caf)
            return food_items

    @cog_ext.cog_subcommand(
        base='mealviewer',
        base_desc='Use the bot\'s MealViewer integration.',
        name='list',
        description='Get the lunch menu for today.',
        options=[
            create_option(
                name='date',
                description='The optional date to look up. Must be in the form MM/DD/YYYY.',
                option_type=3,
                required=False
            ),
        ],
    )    
    async def mealviewer_list(self, ctx, date=None):
        date = date.strptime('%m/%d/%Y').strftime('%m-%d-%Y') if date else datetime.date.today().strftime('%m-%d-%Y')
        food_items = await self.get_mv_list(date)
        embed = tools.create_embed(ctx, 'MealViewer Items')
        embed.add_field(name='Freshman Center', value='\n'.join([f'`{index}` - {val["item_Name"]}' for index, val in enumerate(food_items[0])]))
        embed.add_field(name='Greyhound Station', value='\n'.join([f'`{index}` - {val["item_Name"]}' for index, val in enumerate(food_items[1])]))
        embed.add_field(name='Main Cafeteria', value='\n'.join([f'`{index}` - {val["item_Name"]}' for index, val in enumerate(food_items[2])]))
        await ctx.send(embed=embed)
    
    @cog_ext.cog_subcommand(
        base='mealviewer',
        base_desc='Use the bot\'s MealViewer integration.',
        name='item',
        description='Search Bing for a picture and return the result at a random rank.',
        options=[
            create_option(
                name='cafeteria',
                description='The cafeteria to return the item number for.',
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name='Freshman Center',
                        value='0'
                    ),
                    create_choice(
                        name='Greyhound Station',
                        value='1'
                    ),
                    create_choice(
                        name='Main Cafeteria',
                        value='2'
                    ),
                ]
            ),
            create_option(
                name='item_number',
                description='The item number, returned from /mealviewer item.',
                option_type=4,
                required=True,
            ),
            create_option(
                name='date',
                description='The optional date to look up. Must be in the form MM/DD/YYYY.',
                option_type=3,
                required=False,
            )
        ],
    )
    async def mealviewer_item(self, ctx, cafeteria, item_number, date=None):
        date = date.strptime('%m/%d/%Y').strftime('%m-%d-%Y') if date else datetime.date.today().strftime('%m-%d-%Y')
        food_items = await self.get_mv_list(date)
        food_item = food_items[int(cafeteria)][item_number]
        embed = tools.create_embed(ctx, 'MealViewer Item')
        if food_item["imageFileName"]:
            embed.set_image(url=f'https://appassets.mealviewer.com/fooditemimages/{food_item["imageFileName"]}')
        embed.add_field(name='Name', value=food_item['item_Name'])
        embed.add_field(name='Location', value=food_item['physical_Location_Name'])
        embed.add_field(name='Calories', value=food_item['nutritionals'][0]['value'])
        embed.add_field(name='Total Fat', value=food_item['nutritionals'][1]['value'])
        embed.add_field(name='Protein', value=food_item['nutritionals'][5]['value'])
        await ctx.send(embed=embed)