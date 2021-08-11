import string

import discord
from discord.ext import commands

from bot.helpers import tools


class Profanity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.profanity_wordlist = []
        with open("bot/helpers/wordlist.txt", "r") as f:
            self.profanity_wordlist = f.read().splitlines()

    @commands.Cog.listener()
    async def on_message(self, message):
        message_list = message.content.split(" ")
        censored_message_list = []
        profane_message = False
        for index, val in enumerate(message_list):
            if any(
                val.lower().translate(str.maketrans("", "", string.punctuation)) == item
                for item in self.profanity_wordlist
            ):
                profane_message = True
                censored_message_list.append(f"||{val}||")
            else:
                censored_message_list.append(f"{val}")
        if profane_message:
            censored_message = " ".join(censored_message_list)
            embed = discord.Embed(
                title="Profane Message",
                description=censored_message,
                color=discord.Color.orange(),
            )
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
            await message.delete()


def setup(bot):
    bot.add_cog(Profanity(bot))
