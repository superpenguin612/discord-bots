import discord

def create_embed(ctx, title, desc=None, url=None, color=None, footer_enabled=True):
    if not color:
        color = discord.Embed.Empty
    embed = discord.Embed(title=title, description=desc, url=url, color=color)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    if footer_enabled:
        embed.set_footer(text=f'Server: {ctx.guild} | Command: {ctx.command}', icon_url=ctx.guild.icon_url)
    return embed

def create_error_embed(ctx, desc):
    color = discord.Color.red()
    embed = discord.Embed(title="Error", description=desc, color=color)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    embed.set_footer(text=f'Server: {ctx.guild} | Command: {ctx.command}', icon_url=ctx.guild.icon_url)
    return embed

def log_command(ctx):
    print(f'{ctx.author} ran {ctx.message.content}.')