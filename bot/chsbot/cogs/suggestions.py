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
                description='The reason for your suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
            create_option(
                name='notes',
                description='The notes you want to add to the suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
            create_option(
                name='image_url',
                description='The URL of the image to attach to the suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ],
        guild_ids=[704819543398285383]
    )
    async def _server(self, ctx, suggestion, reason=None, notes=None, image_url=None):
        await self.create_suggestion_slash(ctx, suggestion, reason, notes, image_url, 'Server Suggestion', color=discord.Color.gold())

    @cog_ext.cog_subcommand(
        base='suggest',
        base_desc='Create a suggestion.',
        name='movie',
        description='Create a movie suggestion.',
        options=[
            create_option(
                name='suggestion',
                description='The suggestion you want to make.',
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
            create_option(
                name='reason',
                description='The reason for your suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
            create_option(
                name='notes',
                description='The notes you want to add to the suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
            create_option(
                name='image_url',
                description='The URL of the image to attach to the suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ],
        guild_ids=[704819543398285383]
    )
    async def _movie(self, ctx, suggestion, reason=None, notes=None, image_url=None):
        await self.create_suggestion_slash(ctx, suggestion,  reason, notes, image_url, 'Movie Suggestion', color=discord.Color.green())

    @cog_ext.cog_subcommand(
        base='suggest',
        base_desc='Create a suggestion.',
        name='bot',
        description='Create a bot suggestion.',
        options=[
            create_option(
                name='suggestion',
                description='The suggestion you want to make.',
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
            create_option(
                name='reason',
                description='The reason for your suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
            create_option(
                name='notes',
                description='The notes you want to add to the suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
            create_option(
                name='image_url',
                description='The URL of the image to attach to the suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ],
        guild_ids=[704819543398285383]
    )
    async def _bot(self, ctx, suggestion, reason=None, notes=None, image_url=None):
        await self.create_suggestion_slash(ctx, suggestion,  reason, notes, image_url, 'Bot Suggestion', color=discord.Color.purple())

    @cog_ext.cog_subcommand(
        base='suggest',
        base_desc='Create a suggestion.',
        name='rule',
        description='Create a rule suggestion.',
        options=[
            create_option(
                name='suggestion',
                description='The suggestion you want to make.',
                option_type=SlashCommandOptionType.STRING,
                required=True
            ),
            create_option(
                name='reason',
                description='The reason for your suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
            create_option(
                name='notes',
                description='The notes you want to add to the suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
            create_option(
                name='image_url',
                description='The URL of the image to attach to the suggestion.',
                option_type=SlashCommandOptionType.STRING,
                required=False
            ),
        ],
        guild_ids=[704819543398285383]
    )
    async def _rule(self, ctx, suggestion, reason=None, notes=None, image_url=None):
        await self.create_suggestion_slash(ctx, suggestion,  reason, notes, image_url, 'Rule Suggestion', color=discord.Color.blue())

    async def create_suggestion_slash(self, ctx, suggestion, reason, notes, image_url, title, color, downvote=True):
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