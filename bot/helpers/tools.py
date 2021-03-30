import discord
import asyncio

def create_embed(ctx, title, desc='', url=None, color=None, footer_enabled=True):
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

def create_error_embed(ctx, desc):
    color = discord.Color.red()
    embed = discord.Embed(title="Error", description=desc, color=color)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    if ctx.channel.type is not discord.ChannelType.private:
            embed.set_footer(text=f'Server: {ctx.guild} | Command: {ctx.command}', icon_url=ctx.guild.icon_url)
    else:
        embed.set_footer(text=f'Server: DMs | Command: {ctx.command}')
    return embed


class EmbedPaginator:
    REACTIONS = {
        'first': '⏮', 
        'back': '◀️',
        'forward': '▶️',
        'last': '⏭',
        'stop': '⏹'
    }
    
    def __init__(self, bot, ctx, embed_pages):
        self.ctx = ctx
        self.bot = bot
        self.embed_pages = list(embed_pages)
        self.page_index = 0

    async def run(self):
        self.message = await self.ctx.send(embed=self.embed_pages[self.page_index])

        def check(reaction, user):
            return reaction.message.id == self.message.id and user.id == self.ctx.author.id
        
        for reaction in self.REACTIONS.values():
            await self.message.add_reaction(reaction)

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=180)
            except asyncio.TimeoutError:
                await self.message.clear_reactions()
                return
            
            if reaction.emoji == self.REACTIONS['first']:
                self.page_index = 0
            elif reaction.emoji == self.REACTIONS['back']:
                if self.page_index > 0:
                    self.page_index -= 1
            elif reaction.emoji == self.REACTIONS['forward']:
                if self.page_index < len(self.embed_pages) - 1:
                    self.page_index += 1
            elif reaction.emoji == self.REACTIONS['last']:
                self.page_index = len(self.embed_pages) - 1
            elif reaction.emoji == self.REACTIONS['stop']:
                await self.message.delete()
                return
            
            await self.message.edit(embed=self.embed_pages[self.page_index])
            await reaction.remove(user)