import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType
import asyncio

class Suggestions(commands.Cog, name='suggestions', description='A group of commands related to suggesting improvements for a server.'):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base='suggest',
        base_desc='Create a suggestion.',
        name='server',
        description='Create a server suggestion.',
        options=[
            create_option(
                name='suggestion',
                description='The suggestion you want to make.',
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
            create_option(
                name='reason',
                description='The suggestion you want to make.',
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
            create_option(
                name='notes',
                description='The suggestion you want to make.',
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
            create_option(
                name='suggestion',
                description='The suggestion you want to make.',
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
        ]
    )
    async def _server(self, ctx, *, suggestion):
        await self.create_suggestion(ctx, suggestion, 'Server Suggestion', color=discord.Color.gold())

    @cog_ext.cog_subcommand(
        base='suggest',
        base_desc='Create a suggestion.',
        name='movie',
        description='Create a movie suggestion.',
    )
    async def _movie(self, ctx, *, suggestion):
        await self.create_suggestion(ctx, suggestion, 'Movie Suggestion', color=discord.Color.green(), downvote=False)

    @cog_ext.cog_subcommand(
        base='suggest',
        base_desc='Create a suggestion.',
        name='bot',
        description='Create a bot suggestion.',
    )
    async def _bot(self, ctx, *, suggestion):
        await self.create_suggestion(ctx, suggestion, 'Bot Suggestion', color=discord.Color.purple())

    @cog_ext.cog_subcommand(
        base='suggest',
        base_desc='Create a suggestion.',
        name='rule',
        description='Create a rule suggestion.',
    )
    async def _rule(self, ctx, *, suggestion):
        await self.create_suggestion(ctx, suggestion, 'Rule Suggestion', color=discord.Color.blue())

    async def create_suggestion(self, ctx, suggestion, title, color, downvote=True):
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        embed = tools.create_embed(ctx, "Suggestion Reason", "What is the reason for your suggestion?")
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check, timeout=180)
        if msg.content.lower() == "none":
            reason = None
        elif msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Suggestion has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            reason = msg.content

        embed = tools.create_embed(ctx, "Suggestion Notes", "What else you would like to add? Type \"none\" if you don't have anything else.")
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check, timeout=180)
        if msg.content.lower() == "none":
            notes = None
        elif msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Suggestion has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            notes = msg.content
        
        embed = tools.create_embed(ctx, "Suggestion Image", "Do you have an image to attach to the suggestion? Reply with \"none\" if you don't.")
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check, timeout=180)
        if msg.content.lower() == "none":
            image_url = None
        elif msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Suggestion has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            image_url = msg.attachments[0].url
        
        suggestions_channel = self.bot.get_channel(710959620667211817)
        embed = tools.create_embed(ctx, title, desc=suggestion, footer_enabled=False, color=color)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        if notes:
            embed.add_field(name="Notes", value=notes, inline=False)
        if image_url:
            embed.set_image(url=image_url)
        msg = await suggestions_channel.send(embed=embed)
        await msg.add_reaction('<:upvote:711333713316937819>')
        if downvote:
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