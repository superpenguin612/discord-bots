import random
import typing
from datetime import datetime

import discord
from discord.ext import commands


def create_embed(
    title: str,
    desc: str = "",
    url: str = None,
    color: discord.Colour = None,
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=desc,
        timestamp=datetime.now(),
        colour=random.choice(
            [discord.Colour.from_str("#FBBF05"), discord.Colour.from_str("#0F64FA")]
        ),
    )
    if url:
        embed.url = url
    # embed.set_footer(
    #     text=random.choice(
    #         ["*vrrrrrrrrrrrrr*", "*frisbee shooting noises*", "*beep boop*"]
    #     ),
    #     # icon_url="https://raw.githubusercontent.com/frc868/flick/master/icon_footer.png",
    # )
    return embed


def create_error_embed(desc: str) -> discord.Embed:
    color = discord.Color.red()
    embed = discord.Embed(title="Error", description=desc, color=color)
    embed.set_footer(
        text=random.choice(
            ["*vrrrrrrrrrrrrr*", "*frisbee shooting noises*", "*beep boop*"]
        ),
        icon_url="https://raw.githubusercontent.com/frc868/flick/master/icon_footer.png",
    )
    return embed


class ViewBase(discord.ui.View):
    user: discord.User
    msg: discord.Message  # any Views must have msg set when the message is sent (e.g. `view.msg = await ctx.send(view=view)`)

    def __init__(self, user: discord.User, timeout: float = 180.0) -> None:
        super().__init__(timeout=timeout)
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user.id:
            return True
        else:
            await interaction.response.send_message(
                embed=create_error_embed("You can't use another user's menu."),
                ephemeral=True,
            )
            return False

    def disable(self) -> None:
        for child in self.children:
            child.disabled = True
        self.stop()

    async def on_timeout(self) -> None:
        self.disable()
        try:
            await self.msg.edit(view=self)
        except:
            pass


class Confirmation(ViewBase):
    accepted: bool

    def __init__(self, user: discord.User, timeout: float = 300.0):
        super().__init__(user, timeout=timeout)
        self.accepted = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        self.accepted = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.accepted = False
        self.stop()


class JumpToPage(discord.ui.Modal, title="Jump To Page"):
    page_number = discord.ui.TextInput(label="Page Number")
    target: int
    interaction: discord.Interaction
    sucessful: bool

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.target = int(self.page_number.value)
            self.interaction = interaction  # implication of not responding to interaction here is that EmbedButtonPaginator MUST respond within 3 seconds
            self.successful = True
        except:
            await interaction.response.send_message(
                embed=create_error_embed("Inputted page number is not an integer."),
                ephemeral=True,
            )
            self.successful = False


class EmbedButtonPaginator(ViewBase):
    embeds: list[discord.Embed]
    page_index: int
    callback: typing.Callable[[int], discord.Embed]

    def __init__(
        self,
        user: discord.User,
        embeds: list[discord.Embed],
        initial_page_index: int = 0,
        callback: typing.Callable = None,
    ):
        super().__init__(user, timeout=180.0)
        self.embeds = embeds
        self.page_index = initial_page_index
        self.callback = callback if callback else lambda page: self.embeds[page]
        self.update_buttons()  # to make the page button has a correct label

    def get_page(self, page: int):
        return self.callback(page)

    def update_buttons(self):
        self.first.disabled = self.page_index == 0
        self.prev.disabled = self.page_index == 0
        self.next.disabled = self.page_index == len(self.embeds) - 1
        self.last.disabled = self.page_index == len(self.embeds) - 1

        self.page.label = f"Page {self.page_index+1}/{len(self.embeds)}"

    @discord.ui.button(label="First", style=discord.ButtonStyle.blurple)
    async def first(self, interaction: discord.Interaction, button: discord.Button):
        self.page_index = 0
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.get_page(self.page_index), view=self
        )

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.green)
    async def prev(self, interaction: discord.Interaction, button: discord.Button):
        self.page_index -= 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.get_page(self.page_index), view=self
        )

    @discord.ui.button(label=f"Page", style=discord.ButtonStyle.gray)
    async def page(self, interaction: discord.Interaction, button: discord.Button):
        modal = JumpToPage()
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.successful:
            try:
                if modal.target - 1 < 0 or modal.target - 1 > len(self.embeds) - 1:
                    raise ValueError()
                self.page_index = modal.target - 1
            except:
                await modal.interaction.response.send_message(
                    embed=create_error_embed("Invalid page number."), ephemeral=True
                )
                return
            self.update_buttons()
            await modal.interaction.response.edit_message(
                embed=self.get_page(self.page_index), view=self
            )

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.page_index += 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.get_page(self.page_index), view=self
        )

    @discord.ui.button(label="Last", style=discord.ButtonStyle.blurple)
    async def last(self, interaction: discord.Interaction, button: discord.Button):
        self.page_index = len(self.embeds) - 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.get_page(self.page_index), view=self
        )


class RoleSelectorButton(discord.ui.Button):
    role: discord.Role
    other_roles: list[discord.Role]
    embed_title: str
    role_map: dict[int, str]
    mutually_exclusive: bool

    def __init__(
        self,
        role: discord.Role,
        all_roles: list[discord.Role],
        embed_title: str,
        custom_id: str | None = None,
        mutually_exclusive: bool = True,
    ) -> None:
        super().__init__(
            style=discord.ButtonStyle.gray, label=role.name, custom_id=custom_id
        )
        self.role = role
        self.other_roles = [role for role in all_roles if role != self.role]
        self.embed_title = embed_title
        self.mutually_exclusive = mutually_exclusive

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view: RoleSelector | PersistentRoleSelector = self.view

        if self.mutually_exclusive:
            if interaction.user.get_role(self.role.id):
                embed = create_embed(
                    self.embed_title, f"You are already in {self.role.name}."
                )
            elif self.get_prior_role(interaction.user):
                embed = create_embed(
                    self.embed_title,
                    f"You have moved from {self.get_prior_role(interaction.user)} to {self.role.name}.",
                )
            else:
                embed = create_embed(
                    self.embed_title, f"You have been added to {self.role.name}."
                )
            await self.assign_role(interaction)
        else:
            if interaction.user.get_role(self.role.id):
                embed = create_embed(
                    self.embed_title, f"You have been removed from {self.role.name}."
                )
                await interaction.user.remove_roles(self.role)
            else:
                embed = create_embed(
                    self.embed_title, f"You have been added to {self.role.name}."
                )
                await interaction.user.add_roles(self.role)

        if self.is_persistent():
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
        else:
            self.style = discord.ButtonStyle.green
            view.disable()
            await interaction.response.edit_message(
                embed=embed,
                view=view,
            )

    def get_prior_role(self, user: discord.Member) -> str | None:
        for role in self.other_roles:
            if user.get_role(role.id):
                return role.name
        return None

    async def assign_role(self, interaction: discord.Interaction) -> None:
        for role in self.other_roles:
            if interaction.user.get_role(role.id):
                await interaction.user.remove_roles(role)

        await interaction.user.add_roles(self.role)


class RoleSelector(ViewBase):
    def __init__(
        self,
        user: discord.User,
        guild: discord.Guild,
        role_ids: typing.Iterable[int],
        embed_title: str,
    ) -> None:
        super().__init__(user)

        roles = [guild.get_role(role_id) for role_id in role_ids]
        for role in roles:
            self.add_item(RoleSelectorButton(role, roles, embed_title))


class PersistentRoleSelector(discord.ui.View):
    def __init__(
        self,
        guild: discord.Guild,
        role_ids: typing.Iterable[int],
        embed_title: str,
        custom_id_prefix: str,
        mutually_exclusive: bool = True,
    ) -> None:
        super().__init__(timeout=None)

        roles = [guild.get_role(role_id) for role_id in role_ids]
        for role in roles:
            self.add_item(
                RoleSelectorButton(
                    role,
                    roles,
                    embed_title,
                    f"{custom_id_prefix}:{role.id}",
                    mutually_exclusive,
                )
            )

    def disable(self) -> None:
        for child in self.children:
            child.disabled = True
        self.stop()
