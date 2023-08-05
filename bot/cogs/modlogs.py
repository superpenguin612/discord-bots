# doesn't work yet

import json

import discord
from discord.ext import commands


class ModLogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log_channel_id = 1016517257624567848

    @commands.Cog.listener(name="on_raw_message_edit")
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent) -> None:
        if "author" in payload.data:
            if payload.data["author"]["id"] != self.bot.user.id:
                guild = self.bot.get_guild(int(payload.data["guild_id"]))
                log_channel = guild.get_channel(self.log_channel_id)

                message_channel = guild.get_channel(payload.channel_id)
                message_author = guild.get_member(int(payload.data["author"]["id"]))

                embed = discord.Embed(title=f"Message Edit", color=discord.Color.blue())
                embed.set_author(
                    name=message_author, icon_url=message_author.avatar.url
                )
                try:
                    embed.add_field(
                        name="Before",
                        value=payload.cached_message.content,
                        inline=False,
                    )
                except:
                    embed.add_field(
                        name="Before",
                        value="Message content was not cached.",
                        inline=False,
                    )
                embed.add_field(
                    name="After", value=payload.data["content"], inline=False
                )
                embed.add_field(
                    name="Source",
                    value=f'[Jump Link](https://discord.com/channels/{int(payload.data["guild_id"])}/{payload.channel_id}/{payload.message_id})',
                    inline=False,
                )
                embed.set_footer(
                    text=f"Channel: {message_channel} | Author ID: {message_author.id}| Message ID: {payload.message_id}"
                )
                await log_channel.send(embed=embed)

    @commands.Cog.listener(name="on_raw_message_delete")
    async def on_raw_message_delete(
        self, payload: discord.RawMessageDeleteEvent
    ) -> None:
        guild = self.bot.get_guild(payload.guild_id)
        log_channel = guild.get_channel(self.log_channel_id)
        message_channel = guild.get_channel(payload.channel_id)

        if payload.cached_message:
            if payload.cached_message.author.id != self.bot.user.id:
                embed = discord.Embed(
                    title=f"Message Delete",
                    description=payload.cached_message.content,
                    color=discord.Color.red(),
                )
                embed.set_author(
                    name=payload.cached_message.author,
                    icon_url=payload.cached_message.author.avatar.url,
                )
                embed.set_footer(
                    text=f"Channel: {message_channel} | Author ID: {payload.cached_message.author.id} | Message ID: {payload.message_id}"
                )
                await log_channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Message Delete",
                description="Message content was not cached.",
                color=discord.Color.red(),
            )
            embed.set_footer(
                text=f"Channel: {message_channel} | Message ID: {payload.message_id}"
            )
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        guild = channel.guild
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Channel Create",
            description=f"{channel.mention} has been created.",
            color=discord.Color.red(),
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        guild = channel.guild
        log_channel = guild.get_channel(self.log_channel_id)
        embed = discord.Embed(
            title=f"Channel Delete",
            description=f"{channel.mention} has been deleted.",
            color=discord.Color.red(),
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ) -> None:
        guild = before.guild
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Channel Update",
            description=f"{before.mention} has been updated.",
            color=discord.Color.red(),
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        guild = member.guild
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Member Join",
            description=f"{member.mention} has joined the server.",
            color=discord.Color.red(),
        )
        embed.set_author(name=member, icon_url=member.avatar.url)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        guild = member.guild
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Member Leave",
            description=f"{member.mention} has left the server.",
            color=discord.Color.red(),
        )
        embed.set_author(name=member, icon_url=member.avatar.url)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        added_roles = []
        removed_roles = []
        if before.roles != after.roles:
            if len(before.roles) < len(after.roles):
                for role in after.roles:
                    if role not in before.roles:
                        added_roles.append(role)
            if len(before.roles) > len(after.roles):
                for role in before.roles:
                    if role not in after.roles:
                        removed_roles.append(role)
        if added_roles or removed_roles:
            embed = discord.Embed(title=f"Member Update", color=discord.Color.red())
            if added_roles:
                value = (" ").join([role.mention for role in added_roles])
                embed.add_field(name="Added Roles", value=value)
            elif removed_roles:
                value = (" ").join([role.mention for role in removed_roles])
                embed.add_field(name="Removed Roles", value=value)
            embed.set_author(name=before, icon_url=before.avatar.url)

            guild = before.guild
            log_channel = guild.get_channel(self.log_channel_id)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        guild = invite.guild
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Invite Create",
            description=f"An invite has been created.",
            color=discord.Color.red(),
        )
        embed.add_field(name="Code", value=invite.code)
        embed.add_field(name="Channel", value=invite.channel.mention)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite) -> None:
        guild = invite.guild
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Invite Delete",
            description=f"An invite has been deleted.",
            color=discord.Color.red(),
        )
        embed.add_field(name="Code", value=invite.code)
        embed.add_field(name="Channel", value=invite.channel.mention)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_update(
        self, before: discord.Guild, after: discord.Guild
    ) -> None:
        guild = before
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Guild Update",
            description=f"This guild has been updated.",
            color=discord.Color.red(),
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        guild = role.guild
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Role Create",
            description=f"{role.mention} has been created.",
            color=discord.Color.red(),
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        guild = role.guild
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Role Delete",
            description=f"{role.mention} has been deleted.",
            color=discord.Color.red(),
        )
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(
        self, before: discord.Role, after: discord.Role
    ) -> None:
        if after.name == "Rainbow":
            return
        guild = before.guild
        log_channel = guild.get_channel(self.log_channel_id)

        embed = discord.Embed(
            title=f"Role Update",
            description=f"{before.mention} has been updated.",
            color=discord.Color.red(),
        )
        await log_channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModLogs(bot))
