import discord
from discord.ext import commands
from bot.helpers import tools
import profanity_check

class Profanity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        message_list = message.content.split(" ")
        message_check = profanity_check.predict_prob(message_list)
        if all(i >= 0.7 for i in message_check):
            censored_message_list = []
            for index, val in enumerate(message_check):
                if val >= 0.7:
                    censored_message_list.append(f'||{message_list[index]}||')
                else:
                    censored_message_list.append(f'{message_list[index]}')
            censored_message = " ".join(censored_message_list)
            embed = discord.Embed(title='Profane Message', description=censored_message, color=discord.Color.orange())
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
            await message.delete()