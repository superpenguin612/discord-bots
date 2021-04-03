import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType
import sympy
# import matplotlib.pyplot as plt
# import numpy as np

class Math(commands.Cog, name='math'):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name='latex',
        description='Compile LaTeX code and view a standalone output.',
        options=[
            create_option(
                name='tex',
                description='The TeX code to compile.',
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
            create_option(
                name='scale',
                description='The scale to render the LaTeX at. Default is 100.',
                option_type=SlashCommandOptionType.INTEGER,
                required=False
            ),
        ],
        guild_ids=[809169133086048257]
    )
    async def latex(self, ctx, tex, scale=100):
        try:
            sympy.preview(tex, viewer='file', euler=False, filename='texout.png', dvioptions=["-T", "bbox", "-z", "0", "--truecolor", f"-D {(scale/100)*600}", '-bg HTML 2f3136', '-fg gray 1.0'])
        except Exception as e:
            embed = tools.create_error_embed(ctx, 'Could not compile LaTeX. Check your code and try again.')
            await ctx.send(embed=embed)
            print(e)
            return
        
        embed = tools.create_embed(ctx, 'LaTeX')
        file = discord.File('texout.png', filename='texout.png')
        embed.set_image(url='attachment://texout.png')
        await ctx.send(file=file, embed=embed)

def setup(bot):
    bot.add_cog(Math(bot))