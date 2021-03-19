import discord
from discord.ext import commands
from bot.helpers import tools
import asyncio
import asyncpg

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        name='sendembed',
        brief='Send an embed message from the bot.',
    )
    @commands.has_permissions(administrator=True)
    async def sendembed(self, ctx):
        """Send an embed message from the bot. 
        This is a "setup" command, so no arguments are passed when you run it. 
        The setup instructions will start after the command is run. 
        You have 3 minutes to reply to each step in the setup process.
        **Usage**
        `_prefix_sendembed`
        **Parameters**
        None
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Administrator
        **Examples**
        `_prefix_sendembed`
        """
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        embed = discord.Embed(title='Title', description='Description')
        embed.set_footer(text='Footer')
        example_embed = await ctx.send('Here is an example embed.',embed=embed)

        embed = tools.create_embed(ctx, "Embed Setup 1/4", "Tag the channel where you want to send the embed.")
        sent_msg = await ctx.send(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=180)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Embed creation has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            channel = user_msg.channel_mentions[0]

        embed = tools.create_embed(ctx, "Embed Setup 2/4", "Send the title of the embed.")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=180)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Embed creation has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            title = user_msg.content

        embed = tools.create_embed(ctx, "Embed Setup 3/4", "Send the description of the embed.")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=180)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Embed creation has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            description = user_msg.content

        embed = tools.create_embed(ctx, "Embed Setup 4/4", "Send the footer of the embed.")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=180)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Embed creation has been aborted.")
            await ctx.send(embed=embed)
            return
        elif user_msg.content.lower() == "none":
            footer = None
        else:
            footer = user_msg.content
            embed.set_footer(text=footer)

        embed = discord.Embed(title=title, description=description)
        await channel.send(embed=embed)

        await example_embed.delete()

        embed = tools.create_embed(ctx, "Embed", "Embed has been created successfully!!")
        await sent_msg.edit(embed=embed)
    
    @commands.command(
        name='editembed',
        brief='Edit an embed message sent by the bot.',
    )
    async def editembed(self, ctx):
        """Edit an embed message sent by the bot. 
        This is a "setup" command, so no arguments are passed when you run it. 
        The setup instructions will start after the command is run. 
        You have 3 minutes to reply to each step in the setup process.
        NOTE: This command is in beta at the moment and will be overhauled soon.
        **Usage**
        `_prefix_editembed`
        **Parameters**
        None
        **Aliases**
        None
        **Cooldown**
        None
        **Permissions Required**
        Administrator
        **Examples**
        `_prefix_editembed`
        """
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        embed = discord.Embed(title='Title', description='Description')
        embed.set_footer(text='Footer')
        example_embed = await ctx.send('Here is an example embed.',embed=embed)

        embed = tools.create_embed(ctx, "Embed Edit 1/5", "Tag the channel where the embed currently is.")
        sent_msg = await ctx.send(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=180)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Embed creation has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            message_id = user_msg.content
        
        embed = tools.create_embed(ctx, "Embed Edit 2/5", "Send the message ID of the message containing the embed.")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=180)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Embed creation has been aborted.")
            await sent_msg.edit(embed=embed)
            return
        else:
            channel = user_msg.channel_mentions[0]
        
        try:
            embed_message = channel.get_partial_message()
        except:
            embed = tools.create_error_embed(ctx, "That message does not exist. Make sure the message is in the channel you tagged in the previous step.")
            await sent_msg.edit(embed=embed)
            return
        
        if not (embed_message.author.id == self.bot.user.id):
            embed = tools.create_error_embed(ctx, "That message was not sent by the bot.")
            await ctx.send(embed=embed)
            return

        embed = tools.create_embed(ctx, "Embed Edit 3/5", "Send the title of the embed.")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=180)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Embed creation has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            title = user_msg.content

        embed = tools.create_embed(ctx, "Embed Edit 4/5", "Send the description of the embed.")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=180)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Embed creation has been aborted.")
            await ctx.send(embed=embed)
            return
        else:
            description = user_msg.content

        embed = tools.create_embed(ctx, "Embed Edit 5/5", "Send the footer of the embed.")
        await sent_msg.edit(embed=embed)
        user_msg = await self.bot.wait_for("message", check=check, timeout=180)
        await user_msg.delete()
        if user_msg.content.lower() == "stop":
            embed = tools.create_error_embed(ctx, "Embed creation has been aborted.")
            await ctx.send(embed=embed)
            return
        elif user_msg.content.lower() == "none":
            footer = None
        else:
            footer = user_msg.content
        embed = discord.Embed(title=title, description=description)
        embed.set_footer(text=footer)
        await channel.send(embed=embed)

        await example_embed.delete()

        embed = tools.create_embed(ctx, "Embed", "Embed has been edited successfully!!")
        await sent_msg.edit(embed=embed)