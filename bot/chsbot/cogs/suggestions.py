import discord
from discord.ext import commands
from bot.helpers import tools
import asyncio

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.cooldown(1, 900, type=commands.BucketType.user)
    async def suggest(self, ctx):
        """Suggest something for the server. 
        Suggestions will go into #suggestions.
        The bot will prompt for the reason for the suggestion, then any notes.
        You may specify "none" for either the reason or the notes.
        """
        if ctx.invoked_subcommand is None:
            embed = tools.create_embed(ctx, 'Suggestion', desc=f'Please specify a category for your suggestion.\nThe available categories are `server`, `bot`, `movie`, and `rule`.\nThe command\'s usage is `{ctx.prefix}suggest <category> <suggestion>`')
            await ctx.send(embed=embed)
            self.suggest.reset_cooldown(ctx)

    @suggest.command(name='server')
    async def _server(self, ctx, *, suggestion):
        await self.create_suggestion(ctx, suggestion, 'Server Suggestion', color=discord.Color.gold())

    @suggest.command(name='movie')
    async def _movie(self, ctx, *, suggestion):
        await self.create_suggestion(ctx, suggestion, 'Movie Suggestion', color=discord.Color.green())

    @suggest.command(name='bot')
    async def _bot(self, ctx, *, suggestion):
        await self.create_suggestion(ctx, suggestion, 'Bot Suggestion', color=discord.Color.purple())

    @suggest.command(name='rule')
    async def _rule(self, ctx, *, suggestion):
        await self.create_suggestion(ctx, suggestion, 'Rule Suggestion', color=discord.Color.blue())

    async def create_suggestion(self, ctx, suggestion, title, color):
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        embed = tools.create_embed(ctx, "Suggestion Reason", "What is the reason for your suggestion?")
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check, timeout=30)
        if msg.content.lower() in ["none", "stop"]:
            reason = None
        else:
            reason = msg.content

        embed = tools.create_embed(ctx, "Suggestion Notes", "What else you would like to add? Type \"None\" if you don't have anything else.")
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check, timeout=30)
        if msg.content.lower() in ["none", "stop"]:
            notes = None
        else:
            notes = msg.content
        
        suggestions_channel = self.bot.get_channel(710959620667211817)
        embed = tools.create_embed(ctx, title, desc=suggestion, footer_enabled=False, color=color)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)
        msg = await suggestions_channel.send(embed=embed)
        await msg.add_reaction('<:upvote:711333713316937819>')
        await msg.add_reaction('<:downvote:711333713354686484>')

        embed = tools.create_embed(ctx, title, desc="Your suggestion has been submitted successfully!", color=color)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def removesuggestion(self, ctx, id: int):
        """This command allows for anyone with the "Manage Messages" 
        permission to remove a suggestion."""
        suggestions_channel = self.bot.get_channel(710959620667211817)
        msg = await suggestions_channel.fetch_message(id)
        await msg.delete()
        desc = f"Suggestion with ID {id} has been removed."
        embed = tools.create_embed(ctx, "Suggestion Removal", desc=desc)
        await ctx.send(embed=embed)