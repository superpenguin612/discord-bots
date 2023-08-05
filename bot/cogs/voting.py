import discord
from discord import app_commands
from discord.ext import commands

from bot.helpers import tools


class VoteView(discord.ui.View):
    text: str
    number_required: int
    role: discord.Role | None
    anonymous: bool
    votes: dict[int, str]

    def __init__(
        self,
        text: str,
        number_required: int,
        role: discord.Role | None = None,
        anonymous: bool = False,
    ):
        super().__init__(timeout=None)
        self.text = text
        self.number_required = number_required
        self.role = role
        self.anonymous = anonymous
        self.votes = {}

    def create_embed(self, completed: bool = False) -> discord.Embed:
        embed = tools.create_embed("Vote", self.text)
        embed.add_field(name="Votes Required", value=self.number_required, inline=False)
        if self.role:
            embed.add_field(name="Required Role", value=self.role.mention, inline=False)

        if self.anonymous:
            embed.add_field(name="For", value=list(self.votes.values()).count("yes"))
            embed.add_field(name="Against", value=list(self.votes.values()).count("no"))
            embed.add_field(
                name="Abstaining", value=list(self.votes.values()).count("abstain")
            )
        else:
            embed.add_field(
                name="For",
                value="\n".join(
                    [
                        f"<@{user_id}>"
                        for user_id, vote in self.votes.items()
                        if vote == "yes"
                    ]
                )
                if list(self.votes.values()).count("yes") > 0
                else "None",
            )
            embed.add_field(
                name="Against",
                value="\n".join(
                    [
                        f"<@{user_id}>"
                        for user_id, vote in self.votes.items()
                        if vote == "no"
                    ]
                )
                if list(self.votes.values()).count("no") > 0
                else "None",
            )
            embed.add_field(
                name="Abstaining",
                value="\n".join(
                    [
                        f"<@{user_id}>"
                        for user_id, vote in self.votes.items()
                        if vote == "abstain"
                    ]
                )
                if list(self.votes.values()).count("abstain") > 0
                else "None",
            )

        if completed:
            embed.title = "Vote Results"
            embed.color = discord.Colour.green()
        return embed

    async def process_vote(self, interaction: discord.Interaction, vote: str):
        prev_vote = self.votes.get(interaction.user.id)
        self.votes[interaction.user.id] = vote
        if prev_vote == vote:
            await interaction.response.send_message(
                embed=tools.create_embed(
                    "Vote", "You have already voted for this option."
                ),
                ephemeral=True,
            )
        elif prev_vote:
            await interaction.response.send_message(
                embed=tools.create_embed(
                    "Vote",
                    f"Your vote of {prev_vote.title()} has been moved to {vote.title()}.",
                ),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                embed=tools.create_embed(
                    "Vote", f"Your vote of '{vote.title()}' has been added."
                ),
                ephemeral=True,
            )

        completed = (
            len([vote for user_id, vote in self.votes.items() if vote in ["yes", "no"]])
            >= self.number_required
        )
        if completed:
            self.stop()
            for child in self.children:
                child.disabled = True

        await interaction.message.edit(
            embed=self.create_embed(completed=completed), view=self
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not self.role or self.role in interaction.user.roles:
            return True
        else:
            await interaction.response.send_message(
                embed=tools.create_error_embed("You cannot vote in this."),
                ephemeral=True,
            )
            return False

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_vote(interaction, "yes")

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_vote(interaction, "no")

    @discord.ui.button(label="Abstain", style=discord.ButtonStyle.gray)
    async def abstain(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.process_vote(interaction, "abstain")


class Voting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(description="Create a vote.")
    @app_commands.describe(
        text="The thing to vote for.",
        number_required="The number of votes required on either side to close the vote.",
        role="The role to restrict voting to.",
        anonymous="Whether to make voting anonymous (display does not show who voted for what). Default is False.",
    )
    async def mkvote(
        self,
        ctx: commands.Context,
        text: str,
        number_required: int,
        role: discord.Role | None = None,
        anonymous: bool = False,
    ) -> None:
        view = VoteView(text, number_required, role, anonymous)
        await ctx.send(embed=view.create_embed(), view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Voting(bot))
