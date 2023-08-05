import discord
from discord import app_commands
from discord.ext import commands

from bot.helpers import tools

# TODO: convert some of these extra modals to generic ones for tools module to declutter
# TODO: make ;addembed and ;removeembed commands to have messages with more than one embed


class Embeds(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.bot.tree.add_command(
            app_commands.ContextMenu(
                name="Edit Embed",
                callback=self.editembed_menu,
            )
        )

    async def editembed_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        if message.author.id != self.bot.user.id:
            await interaction.response.send_message(
                embed=tools.create_error_embed(
                    "That message was not sent by this bot."
                ),
                ephemeral=True,
            )
            return
        if interaction.user.guild_permissions.manage_messages:
            view = EmbedEditor(interaction.user, message)
            await interaction.response.send_message(embeds=view.get_embeds(), view=view)
        else:
            await interaction.response.send_message(
                embed=tools.create_error_embed("You can't do that."), ephemeral=True
            )

    @commands.hybrid_command(
        name="sendembed",
        description="Send an embed message from the bot.",
    )
    @app_commands.describe(channel="The channel to send the embed to.")
    @commands.has_permissions(manage_messages=True)
    async def sendembed(
        self, ctx: commands.Context, channel: discord.TextChannel | None = None
    ) -> None:
        view = EmbedEditor(ctx.author, channel if channel else ctx.channel)
        await ctx.send(embeds=view.get_embeds(), view=view)

    @commands.hybrid_command(
        name="editembed",
        description="Edit an embed message sent by the bot.",
    )
    @app_commands.describe(
        channel="The channel to send the embed to.",
        message_id="The ID of the mesasge that contains the embed you want to edit.",
        # embed_number="The number embed you want to edit (1 for the 1st, 2 for the 2nd, etc).",
    )
    @commands.has_permissions(manage_messages=True)
    async def editembed(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel,
        message_id: str,
        # embed_number: int = 1,
    ) -> None:
        try:
            message = await channel.fetch_message(int(message_id))
        except:
            await ctx.send(embed=tools.create_error_embed("Invalid message ID."))
            return
        if message.author.id != ctx.bot.user.id:
            await ctx.send(
                embed=tools.create_error_embed("That message was not sent by this bot.")
            )
            return
        view = EmbedEditor(ctx.author, message)
        await ctx.send(embeds=view.get_embeds(), view=view)


class EmbedEditor(tools.ViewBase):
    embed: discord.Embed
    channel: discord.TextChannel
    message: discord.Message | None

    def __init__(
        self,
        user: discord.User,
        target: discord.TextChannel | discord.Message,
        embed_number: int = 0,
    ) -> None:
        super().__init__(user, timeout=600.0)
        if isinstance(target, discord.TextChannel):
            self.channel = target
            self.embed = discord.Embed(description="Placeholder Text")
            self.message = None
        elif isinstance(target, discord.Message):
            self.message = target
            self.channel = target.channel
            self.embed = self.message.embeds[embed_number]
        self.update_field_buttons()

    def get_embeds(self) -> list[discord.Embed]:
        instructions = discord.Embed(
            title="Embed Editor",
            description="Use the buttons below to edit the displayed embed.",
            colour=discord.Colour.from_str("#FBBF05"),
        )
        instructions.add_field(name="Location", value=self.channel.mention)
        if self.message:
            instructions.add_field(name="Message ID", value=self.message.id)
        return [instructions, self.embed]

    def update_field_buttons(self) -> None:
        field_buttons = [
            child
            for child in self.children
            if isinstance(child, discord.ui.Button) and "Field " in child.label
        ]
        for button in field_buttons:
            self.remove_item(button)

        class FieldButtonModal(discord.ui.Modal):
            embed: discord.Embed
            index: int
            interaction: discord.Interaction
            name = discord.ui.TextInput(label="Name")
            text = discord.ui.TextInput(
                label="Text", style=discord.TextStyle.long, max_length=1024
            )
            inline = discord.ui.TextInput(label="Is Inline")

            def __init__(self, embed: discord.Embed, index: int) -> None:
                super().__init__(title=f"Edit Field {index+1}")
                self.embed = embed
                self.index = index
                self.name.default = self.embed.fields[index].name
                self.text.default = self.embed.fields[index].value
                self.inline.default = str(self.embed.fields[index].inline)

            async def on_submit(self, interaction: discord.Interaction) -> None:
                self.embed.set_field_at(
                    self.index,
                    name=self.name.value,
                    value=self.text.value,
                    inline=self.inline.value.lower() in ["true", "yes", "y"],
                )
                self.interaction = interaction

        def generate_callback(index: int):
            async def callback(interaction: discord.Interaction) -> None:
                modal = FieldButtonModal(self.embed, index)
                await interaction.response.send_modal(modal)
                await modal.wait()
                await modal.interaction.response.edit_message(
                    embeds=self.get_embeds(), view=self
                )

            return callback

        for i in range(len(self.embed.fields)):
            button = discord.ui.Button(label=f"Field {i+1}", row=2)

            button.callback = generate_callback(i)
            self.add_item(button)

    @discord.ui.button(label="Text/Color")
    async def text_color(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        class TextColorModal(discord.ui.Modal, title="Edit Embed Text"):
            embed: discord.Embed
            interaction: discord.Interaction
            title_ = discord.ui.TextInput(label="Title", max_length=256, required=False)
            description = discord.ui.TextInput(
                label="Description",
                style=discord.TextStyle.long,
                max_length=4000,
                required=False,
            )
            url = discord.ui.TextInput(label="URL", required=False)
            color = discord.ui.TextInput(
                label="Color", placeholder="Color as hex (#000000)", required=False
            )

            def __init__(self, embed: discord.Embed) -> None:
                super().__init__()
                self.embed = embed
                self.title_.default = embed.title
                self.description.default = embed.description
                self.url.default = embed.url
                self.color.default = (
                    "#"
                    + "".join(
                        [
                            hex(value)[2:].upper().zfill(2)
                            for value in embed.colour.to_rgb()
                        ]
                    )
                    if embed.colour
                    else None
                )

            async def on_submit(self, interaction: discord.Interaction) -> None:
                self.embed.title = self.title_.value
                self.embed.description = self.description.value
                self.embed.url = self.url.value
                if self.color.value:
                    self.embed.colour = discord.Colour.from_str(self.color.value)
                self.interaction = interaction

        modal = TextColorModal(self.embed)
        await interaction.response.send_modal(modal)
        await modal.wait()
        await modal.interaction.response.edit_message(
            embeds=self.get_embeds(), view=self
        )

    @discord.ui.button(label="Images")
    async def images(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        class ImagesModal(discord.ui.Modal, title="Edit Images"):
            embed: discord.Embed
            interaction: discord.Interaction
            image_url = discord.ui.TextInput(label="Image URL", required=False)
            thumbnail_url = discord.ui.TextInput(label="Thumbnail URL", required=False)

            def __init__(self, embed: discord.Embed) -> None:
                super().__init__()
                self.embed = embed
                self.image_url.default = embed.image.url
                self.thumbnail_url.default = embed.thumbnail.url

            async def on_submit(self, interaction: discord.Interaction) -> None:
                self.embed.set_image(url=self.image_url.value)
                self.embed.set_thumbnail(url=self.thumbnail_url.value)
                self.interaction = interaction

        modal = ImagesModal(self.embed)
        await interaction.response.send_modal(modal)
        await modal.wait()
        await modal.interaction.response.edit_message(
            embeds=self.get_embeds(), view=self
        )

    @discord.ui.button(label="Author")
    async def author(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        class AuthorModal(discord.ui.Modal, title="Edit Author"):
            embed: discord.Embed
            interaction: discord.Interaction
            name = discord.ui.TextInput(label="Name", required=False)
            url = discord.ui.TextInput(label="URL", required=False)
            icon_url = discord.ui.TextInput(label="Icon URL", required=False)

            def __init__(self, embed: discord.Embed) -> None:
                super().__init__()
                self.embed = embed
                self.name.default = embed.author.name
                self.url.default = embed.author.url
                self.icon_url.default = embed.author.icon_url

            async def on_submit(self, interaction: discord.Interaction) -> None:
                self.embed.set_author(
                    name=self.name.value,
                    url=self.url.value,
                    icon_url=self.icon_url.value,
                )
                self.interaction = interaction

        modal = AuthorModal(self.embed)
        await interaction.response.send_modal(modal)
        await modal.wait()
        await modal.interaction.response.edit_message(
            embeds=self.get_embeds(), view=self
        )

    @discord.ui.button(label="Footer")
    async def footer(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        class FooterModal(discord.ui.Modal, title="Edit Footer"):
            embed: discord.Embed
            interaction: discord.Interaction
            text = discord.ui.TextInput(label="Text", required=False)
            icon_url = discord.ui.TextInput(label="Icon URL", required=False)

            def __init__(self, embed: discord.Embed) -> None:
                super().__init__()
                self.embed = embed
                self.text.default = embed.footer.text
                self.icon_url.default = embed.footer.icon_url

            async def on_submit(self, interaction: discord.Interaction) -> None:
                self.embed.set_footer(
                    text=self.text.value,
                    icon_url=self.icon_url.value,
                )
                self.interaction = interaction

        modal = FooterModal(self.embed)
        await interaction.response.send_modal(modal)
        await modal.wait()
        await modal.interaction.response.edit_message(
            embeds=self.get_embeds(), view=self
        )

    class FieldModal(discord.ui.Modal):
        target: int | None = None
        interaction: discord.Interaction
        index = discord.ui.TextInput(label="Index", required=True)

        def __init__(self, title: str) -> None:
            super().__init__(title=title)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            try:
                self.target = int(self.index.value)
            except:
                await interaction.response.send_message(
                    embed=tools.create_error_embed("Inputted index is not an integer.")
                )
                return
            self.interaction = interaction

    @discord.ui.button(label="Add Field", style=discord.ButtonStyle.blurple, row=3)
    async def add_field(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        modal = self.FieldModal("Add Field")
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.target != None:
            self.embed.insert_field_at(
                modal.target - 1, name="Placeholder Text", value="Placeholder Text"
            )
            self.update_field_buttons()
            await modal.interaction.response.edit_message(
                embeds=self.get_embeds(), view=self
            )

    @discord.ui.button(label="Remove Field", style=discord.ButtonStyle.blurple, row=3)
    async def remove_field(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        modal = self.FieldModal("Remove Field")
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.target != None:
            self.embed.remove_field(modal.target - 1)
            self.update_field_buttons()
            await modal.interaction.response.edit_message(
                embeds=self.get_embeds(), view=self
            )

    @discord.ui.button(label="Send", style=discord.ButtonStyle.green, row=4)
    async def send(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Embed Editor",
                description="Sent!",
                colour=discord.Colour.green(),
            ),
            view=None,
        )
        if self.message:
            await self.message.edit(embed=self.embed)
        else:
            await self.channel.send(embed=self.embed)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=4)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Embed Editor",
                description="Cancelled!",
                colour=discord.Colour.red(),
            ),
            view=None,
        )
        self.stop()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Embeds(bot))
