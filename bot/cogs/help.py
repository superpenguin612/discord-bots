import discord
from discord.ext import commands
from bot.helpers import tools
import itertools
import re

class HelpCommand(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__()

    def create_help_embed(ctx, title, desc=None, url=None, color=None, footer_enabled=True):
        if not color:
            color = discord.Embed.Empty
        embed = discord.Embed(title=title, description=desc, url=url, color=color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        if footer_enabled:
            if ctx.channel.type is not discord.ChannelType.private:
                embed.set_footer(text=f'Server: {ctx.guild} | Command: {ctx.command}', icon_url=ctx.guild.icon_url)
            else:
                embed.set_footer(text=f'Server: DMs | Command: {ctx.command}')
        return embed

    async def send_pages(self, embed):
        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        embed = tools.create_embed(self.context, 'Bot Commands', desc=bot.description)

        note = self.get_opening_note()
        if note and embed.description:
            embed.description += '\n' + note
        elif note:
            embed.description == note

        for cog in list(bot.cogs.values()):
            joined = '\u2002'.join(c.name for c in cog.get_commands())
            embed.add_field(name=re.sub("_", " ", cog.qualified_name).title(), value=f'`{ctx.prefix}help {cog.qualified_name}`\n{joined}', inline=False)
        
        no_category_commands = []
        for command in bot.commands:
            if not command.cog:
                no_category_commands.append(command)
        if no_category_commands:
            joined = '\u2002'.join(c.name for c in no_category_commands)
            embed.add_field(name='No Category', value=joined)

        await self.send_pages(embed)

    async def send_cog_help(self, cog):
        ctx = self.context
        embed = tools.create_embed(self.context, f'Module: {re.sub("_", " ", cog.qualified_name).title()}', desc=cog.description)

        note = self.get_opening_note()
        if note:
            embed.description += '\n' + note

        for command in cog.walk_commands():
            value = command.short_doc if command.short_doc else 'No help text.'
            embed.add_field(name=f'{self.clean_prefix}{command.qualified_name}', value=value, inline=False)

        await self.send_pages(embed)

    async def send_group_help(self, group):
        ctx = self.context
        embed = tools.create_embed(self.context, f'Command Group: {ctx.prefix}{group.qualified_name}', desc=group.description)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        if filtered:
            note = self.get_opening_note()
            if note:
                embed.description += '\n' + note

            for command in filtered:
                value = command.short_doc if command.short_doc is not None else 'No help text.'
                embed.add_field(name=f'{self.clean_prefix}{command.qualified_name}', value=value, inline=False)

        await self.send_pages(embed)

    async def send_command_help(self, command):
        ctx = self.context
        embed = tools.create_embed(self.context, f'Command: {ctx.prefix}{command.qualified_name}', desc=command.description)

        note = self.get_opening_note()
        if note:
            embed.description += '\n' + note
        
        if command.help:
            prefixed_help = re.sub('_prefix_', ctx.prefix, command.help)
            embed.add_field(name='Help Text', value=prefixed_help)
        await self.send_pages(embed)