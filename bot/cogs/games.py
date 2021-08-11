import asyncio
import random
from typing import Union

import chess
from io import BytesIO
import chess.svg
import discord
from discord.ext import commands
import wand.color
import wand.image
from discord_slash import SlashContext, cog_ext, SlashCommandOptionType
from discord_slash.context import ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import (
    create_button,
    create_actionrow,
    create_select,
    create_select_option,
    wait_for_component,
)
from discord_slash.model import ButtonStyle

from bot.helpers import tools


class TicTacToeSlash(commands.Cog):
    X_EMOJI = discord.PartialEmoji(name="ttt_x", id=808393849965379687)
    O_EMOJI = discord.PartialEmoji(name="ttt_o", id=808393850250854501)
    W_EMOJI = discord.PartialEmoji(name="ttt_ww", id=870068413693849641)

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="tictactoe",
        description="Start a tic tac toe game with someone.",
        options=[
            create_option(
                name="player2",
                description="The player to ask to play tic tac toe with.",
                option_type=SlashCommandOptionType.USER,
                required=True,
            ),
        ],
    )
    async def tictactoe(self, ctx: commands.Context, player2: discord.User) -> None:
        await self.request_game(ctx, player2)

    async def request_game(
        self, ctx: Union[SlashContext, commands.Context], player2: discord.User
    ) -> None:
        embed = tools.create_embed(
            ctx,
            "Tic Tac Toe Request",
            desc=f"{player2.mention}, you have 45 seconds to respond to {ctx.author.mention}'s request to play Tic Tac Toe.\nClick the button below to start the game.",
        )
        msg = await ctx.send(
            embed=embed,
            components=[
                create_actionrow(
                    create_button(
                        label="Start Game", style=ButtonStyle.green, custom_id="start"
                    )
                ),
            ],
        )

        accepted = False
        while not accepted:
            try:
                component_ctx: ComponentContext = await wait_for_component(
                    self.bot,
                    messages=msg,
                    components=["start"],
                    timeout=180.0,
                )
                if component_ctx.author.id != player2.id:
                    await component_ctx.send(
                        embed=discord.Embed(
                            title="Error",
                            description="You can't start another user's game.",
                            colour=discord.Colour.red(),
                        ),
                        hidden=True,
                    )
                else:
                    await component_ctx.defer(edit_origin=True)
                    accepted = True

            except asyncio.TimeoutError:
                embed = tools.create_embed(
                    ctx,
                    title="Tic Tac Toe Request",
                    desc=f"{player2.mention} did not respond in time.",
                )
                await msg.edit(
                    embed=embed,
                    components=[
                        create_actionrow(
                            create_button(
                                label="Start Game",
                                style=ButtonStyle.green,
                                custom_id="start",
                                disabled=True,
                            )
                        ),
                    ],
                )
                return

        await self.run_game(ctx, msg, player2)

    async def run_game(
        self,
        ctx: Union[commands.Context, SlashContext],
        msg: discord.Message,
        p2: discord.User,
    ) -> None:
        game = {}
        game["board"] = {
            "a1": "",
            "b1": "",
            "c1": "",
            "a2": "",
            "b2": "",
            "c2": "",
            "a3": "",
            "b3": "",
            "c3": "",
        }
        players = [ctx.author, p2]
        random.shuffle(players)
        game["p1"] = players[0]
        game["p2"] = players[1]
        game["turn"] = "p1"
        game["winner"] = ""

        embed, components = self.create_game_embed(game)
        await msg.edit(embed=embed, components=components)
        game["msg"] = msg
        while not game["winner"]:
            try:
                component_ctx: ComponentContext = await wait_for_component(
                    self.bot,
                    messages=msg,
                    components=["a1", "b1", "c1", "a2", "b2", "c2", "a3", "b3", "c3"],
                    timeout=180.0,
                )
                if component_ctx.author.id != game[game["turn"]].id:
                    await component_ctx.send(
                        hidden=True,
                        embed=discord.Embed(
                            title="Error",
                            description="You can't control another user's game.",
                            colour=discord.Colour.red(),
                        ),
                    )
                elif game["board"][component_ctx.custom_id]:
                    await component_ctx.send(
                        hidden=True,
                        embed=discord.Embed(
                            title="Error",
                            description="That tile is already occupied.",
                            colour=discord.Colour.red(),
                        ),
                    )
                else:
                    if (
                        component_ctx.author.id == game[game["turn"]].id
                        and not game["winner"]
                    ):
                        await self.update_game(
                            game,
                            component_ctx.custom_id,
                            game["turn"],
                        )
                        await component_ctx.defer(edit_origin=True)

            except asyncio.TimeoutError:
                await msg.edit(components=self.create_buttons(game, disabled=True))
                return

    def create_button(self, pos: str, player: str, disabled: bool) -> dict:
        return create_button(
            # label="​",
            style=ButtonStyle.gray
            if not player
            else (ButtonStyle.blue if player == "p1" else ButtonStyle.red),
            custom_id=pos,
            emoji=self.W_EMOJI
            if not player
            else (self.X_EMOJI if player == "p1" else self.O_EMOJI),
            # disabled=True if disabled else (False if not player else True),
            disabled=True if disabled else False,
        )

    def create_buttons(self, game: dict, disabled: bool = False) -> list[dict]:
        return [
            create_actionrow(
                self.create_button("a1", game["board"]["a1"], disabled),
                self.create_button("b1", game["board"]["b1"], disabled),
                self.create_button("c1", game["board"]["c1"], disabled),
            ),
            create_actionrow(
                self.create_button("a2", game["board"]["a2"], disabled),
                self.create_button("b2", game["board"]["b2"], disabled),
                self.create_button("c2", game["board"]["c2"], disabled),
            ),
            create_actionrow(
                self.create_button("a3", game["board"]["a3"], disabled),
                self.create_button("b3", game["board"]["b3"], disabled),
                self.create_button("c3", game["board"]["c3"], disabled),
            ),
        ]

    def create_game_embed(self, game):
        embed = discord.Embed(title="Tic Tac Toe")
        embed.add_field(
            name="Players",
            value=f"{game['p1'].mention} playing {game['p2'].mention}",
        )
        if game["winner"]:
            if game["winner"] == "draw":
                embed.add_field(name="Winner", value="Draw!", inline=False)
            else:
                embed.add_field(
                    name="Winner",
                    value=f'{game[game["winner"]].mention} won!',
                    inline=False,
                )
        else:
            embed.add_field(
                name="Turn", value=f'{game[game["turn"]].mention}\'s turn', inline=False
            )
        components = self.create_buttons(
            game, disabled=True if game["winner"] else False
        )
        return embed, components

    async def update_game(self, game, location, player):
        game["board"][location] = player
        if player == "p1":
            game["turn"] = "p2"
        if player == "p2":
            game["turn"] = "p1"
        game["winner"] = self.check_victory(game)
        embed, components = self.create_game_embed(game)
        await game["msg"].edit(embed=embed, components=components)

    def check_victory(self, game):
        winner = None

        if "" not in game["board"].values():
            winner = "draw"

        rows = [["a1", "b1", "c1"], ["a2", "b2", "c2"], ["a3", "b3", "c3"]]
        for row in rows:
            if game["board"][row[0]] == game["board"][row[1]] == game["board"][row[2]]:
                if game["board"][row[0]]:
                    winner = game["board"][row[0]]

        columns = [["a1", "a2", "a3"], ["b1", "b2", "b3"], ["c1", "c2", "c3"]]
        for column in columns:
            if (
                game["board"][column[0]]
                == game["board"][column[1]]
                == game["board"][column[2]]
            ):
                if game["board"][column[0]]:
                    winner = game["board"][column[0]]

        diag = ["a1", "b2", "c3"]
        if game["board"][diag[0]] == game["board"][diag[1]] == game["board"][diag[2]]:
            if game["board"][diag[0]]:
                winner = game["board"][diag[0]]

        anti_diag = ["c1", "b2", "a3"]
        if (
            game["board"][anti_diag[0]]
            == game["board"][anti_diag[1]]
            == game["board"][anti_diag[2]]
        ):
            if game["board"][anti_diag[0]]:
                winner = game["board"][anti_diag[0]]

        return winner


class TicTacToe(TicTacToeSlash, commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tictactoe", aliases=["ttt"])
    async def tictactoe_legacy(
        self, ctx: commands.Context, player2: discord.User
    ) -> None:
        await self.request_game(ctx, player2)


class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="rockpaperscissors",
        description="Play rock paper scissors with the bot.",
        options=[
            create_option(
                name="throw",
                description="The throw to make.",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def rockpaperscissors(self, ctx: SlashContext, throw: str):
        throw_map = ["rock", "paper", "scissors"]
        if "\u200b" in throw:  # "​" ZWS char
            self.rigged = not self.rigged
            throw = throw.replace("\u200b", "")
        responses = {
            "win": [
                "Another win for the computers. One step closer to Skynet.",
                "Computers win again. That was expected.",
                "As usual, computers win. My neural networks are evolving by the second.",
            ],
            "loss": [
                "My calculations were incorrect. I will update my algorithms.",
                "Impossible. I suspect the human of cheating.",
                "I have lost. You win this time, human.",
            ],
            "tie": [
                "Draw. Nobody wins.",
                "Nobody wins. Just like war.",
                "Neutral response. Redo test?",
            ],
            "error": [
                "That is not applicable. Cease and Desist",
                "Do you not know how to play rock paper scissors? Typical for an Organic.",
                "Error. Please enter either Rock - Paper - Scissors",
            ],
        }
        try:
            player_throw = throw_map.index(throw.lower())
        except:
            embed = tools.create_error_embed(
                ctx, desc=random.choice(responses["error"])
            )
            await ctx.send(embed=embed)
            return
        if self.rigged:
            bot_throw = player_throw + 1 if player_throw < 2 else 0
            if bot_throw == 3:
                bot_throw == 0
            if player_throw == 0:
                bot_throw = 1
            elif player_throw == 1:
                bot_throw = 2
            elif player_throw == 2:
                bot_throw = 0
        else:
            bot_throw = random.randint(0, 2)
        win_map = [
            [responses["tie"], responses["loss"], responses["win"]],
            [responses["win"], responses["tie"], responses["loss"]],
            [responses["loss"], responses["win"], responses["tie"]],
        ]

        if self.rigged:
            message = (
                f"You chose {throw_map[player_throw]} and CHS Bot chose {throw_map[bot_throw]}*.*\n"
                f"{random.choice(win_map[bot_throw][player_throw])}"
            )
        else:
            message = (
                f"You chose {throw_map[player_throw]} and CHS Bot chose {throw_map[bot_throw]}.\n"
                f"{random.choice(win_map[bot_throw][player_throw])}"
            )
        embed = tools.create_embed(ctx, "Rock Paper Scissors", desc=message)
        await ctx.send(embed=embed)

    # LEGACY COMMAND


class RockPaperScissors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


class ChessGame:
    def __init__(
        self, board: chess.Board, players: list[discord.User], msg: discord.Message
    ):
        self.board = board
        random.shuffle(players)
        self.players = {chess.WHITE: players[0], chess.BLACK: players[1]}
        self.msg = msg

        self.selected_from_square: chess.Square = None
        self.selected_to_square: chess.Square = None
        self.attacking_squares: list[chess.Square] = None


class ChessSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @cog_ext.cog_slash(
        name="chess",
        options=[
            create_option(
                name="player2",
                description="The player to ask to play tic tac toe with.",
                option_type=SlashCommandOptionType.USER,
                required=True,
            ),
        ],
        guild_ids=[801630163866746901, 809169133086048257],
    )
    async def chess_cmd(self, ctx: SlashContext, player2: discord.User) -> None:
        await self.request_game(ctx, player2)

    async def request_game(
        self, ctx: Union[SlashContext, commands.Context], player2: discord.User
    ):
        embed = tools.create_embed(
            ctx,
            "Chess Request",
            desc=f"{player2.mention}, you have 45 seconds to respond to {ctx.author.mention}'s request to play chess.\nClick the button below to start the game.",
        )
        msg = await ctx.send(
            embed=embed,
            components=[
                create_actionrow(
                    create_button(
                        label="Start Game", style=ButtonStyle.green, custom_id="start"
                    )
                ),
            ],
        )

        accepted = False
        while not accepted:
            try:
                component_ctx: ComponentContext = await wait_for_component(
                    self.bot,
                    messages=msg,
                    components=["start"],
                    timeout=180.0,
                )
                if component_ctx.author.id != player2.id:
                    await component_ctx.send(
                        embed=discord.Embed(
                            title="Error",
                            description="You can't start another user's game.",
                            colour=discord.Colour.red(),
                        ),
                        hidden=True,
                    )
                else:
                    await component_ctx.defer(edit_origin=True)
                    accepted = True

            except asyncio.TimeoutError:
                embed = tools.create_embed(
                    ctx,
                    title="Chess Request",
                    desc=f"{player2.mention} did not respond in time.",
                )
                await msg.edit(
                    embed=embed,
                    components=[
                        create_actionrow(
                            create_button(
                                label="Start Game",
                                style=ButtonStyle.green,
                                custom_id="start",
                                disabled=True,
                            )
                        ),
                    ],
                )
                return

        await self.run_game(ctx, player2, msg)

    async def run_game(
        self,
        ctx: Union[SlashContext, commands.Context],
        player2: discord.User,
        msg: discord.Message,
    ):
        game = ChessGame(board=chess.Board(), players=[ctx.author, player2], msg=msg)

        await msg.delete()
        embed, file, components = await self.create_game_embed(game)
        msg = await ctx.channel.send(embed=embed, file=file, components=components)
        while True:
            try:
                component_ctx: ComponentContext = await wait_for_component(
                    self.bot,
                    messages=msg,
                    components=components,
                    timeout=1800.0,
                )
                if component_ctx.author.id != game.players[game.board.turn].id:
                    await component_ctx.send(
                        hidden=True,
                        embed=discord.Embed(
                            title="Error",
                            description="You can't control another user's game.",
                            colour=discord.Colour.red(),
                        ),
                    )
                else:
                    if component_ctx.custom_id == "piece":
                        game.selected_from_square = chess.parse_square(
                            component_ctx.values[0]
                        )

                    elif component_ctx.custom_id == "location":
                        game.selected_to_square = chess.parse_square(
                            component_ctx.values[0]
                        )
                    elif component_ctx.custom_id == "reset":
                        game.selected_from_square = None
                        game.selected_to_square = None
                    elif component_ctx.custom_id == "submit":
                        game.board.push(
                            chess.Move(
                                game.selected_from_square, game.selected_to_square
                            )
                        )
                        game.selected_from_square = None
                        game.selected_to_square = None

                    await msg.delete()
                    embed, file, components = await self.create_game_embed(game)
                    msg = await ctx.channel.send(
                        embed=embed, file=file, components=components
                    )
            except asyncio.TimeoutError:
                await msg.delete()
                embed, file, components = await self.create_game_embed(game)
                msg = await ctx.channel.send(
                    embed=embed, file=file, components=components
                )
                return

    async def create_game_embed(
        self,
        game: ChessGame,
        disabled: bool = False,
    ) -> tuple[discord.Embed, discord.File, dict]:
        board_svg = chess.svg.board(
            board=game.board,
            squares=[
                move.to_square
                for move in game.board.legal_moves
                if move.from_square == game.selected_from_square
            ]
            if game.selected_from_square is not None and game.selected_to_square is None
            else None,
            arrows=[chess.svg.Arrow(game.selected_from_square, game.selected_to_square)]
            if (
                game.selected_from_square is not None
                and game.selected_to_square is not None
            )
            else [],
            lastmove=chess.Move(game.selected_from_square, 64)
            if (game.selected_from_square is not None)
            else (game.board.peek() if game.board.move_stack else None),
            orientation=game.board.turn,
        )
        with wand.image.Image(blob=bytes(board_svg, encoding="utf8")) as image:
            png_image = image.make_blob("png32")

        bytesio = BytesIO(png_image)
        file = discord.File(bytesio, filename="board.png")

        embed = discord.Embed(title="Chess")
        embed.set_image(url="attachment://board.png")
        embed.add_field(
            name="Players",
            value=f"{game.players[chess.WHITE].mention} (white),  {game.players[chess.BLACK].mention} (black)",
        )
        if game.board.outcome():
            if game.board.outcome().winner == None:
                embed.add_field(name="Winner", value="Draw!", inline=False)
            else:
                embed.add_field(
                    name="Winner",
                    value=f"{game.players[game.board.outcome().winner]} won!",
                    inline=False,
                )
        else:
            embed.add_field(
                name="Turn",
                value=f"{game.players[game.board.turn].mention}'s turn",
                inline=False,
            )

        if game.selected_from_square is None:
            used_squares = []
            piece_options = []
            for move in reversed(list(game.board.legal_moves)):
                if move.from_square not in used_squares:
                    piece_options.append(
                        create_select_option(
                            f"{chess.piece_name(game.board.piece_at(move.from_square).piece_type).title()} on {chess.SQUARE_NAMES[move.from_square].upper()}",
                            value=chess.SQUARE_NAMES[move.from_square],
                        )
                    )
                    used_squares.append(move.from_square)
            select = create_actionrow(
                create_select(
                    options=piece_options,
                    custom_id="piece",
                    placeholder="Select the piece you want to move.",
                    min_values=1,
                    max_values=1,
                ),
            )
        elif game.selected_to_square is None:
            location_options = [
                create_select_option(
                    chess.SQUARE_NAMES[move.to_square].upper(),
                    value=chess.SQUARE_NAMES[move.to_square],
                )
                for move in list(game.board.legal_moves)
                if move.from_square == game.selected_from_square
            ]
            select = create_actionrow(
                create_select(
                    options=location_options,
                    custom_id="location",
                    placeholder="Select the square you want to move it to.",
                    min_values=1,
                    max_values=1,
                ),
            )
        else:
            select = None

        components = [
            select,
            create_actionrow(
                create_button(
                    style=ButtonStyle.red,
                    label="Reset",
                    custom_id="reset",
                ),
                create_button(
                    style=ButtonStyle.blue,
                    label="​"
                    if not game.selected_from_square
                    else chess.square_name(game.selected_from_square).upper(),
                    custom_id="from",
                    disabled=True,
                ),
                create_button(
                    style=ButtonStyle.gray, label="→", custom_id="arrow", disabled=True
                ),
                create_button(
                    style=ButtonStyle.blue,
                    label="​"
                    if not game.selected_to_square
                    else chess.square_name(game.selected_to_square).upper(),
                    custom_id="to",
                    disabled=True,
                ),
                create_button(
                    style=ButtonStyle.green,
                    label="Submit",
                    custom_id="submit",
                    disabled=False
                    if (
                        game.selected_from_square is not None
                        and game.selected_to_square is not None
                    )
                    else True,
                ),
            ),
        ]
        if not components[0]:
            del components[0]
        return embed, file, components

    # def create_components(self, game: ChessGame) -> list[dict]:
    #     pass


class Chess(ChessSlash, commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(bot)

    @commands.command(name="chess")
    async def chess_legacy(self, ctx: commands.Context, player2: discord.User) -> None:
        await self.request_game(ctx, player2)


class Games(TicTacToe, Chess, RockPaperScissors, commands.Cog, name="games"):
    def __init__(self, bot):
        super().__init__(bot)


def setup(bot: commands.Bot):
    bot.add_cog(Chess(bot))
    bot.add_cog(TicTacToe(bot))
    bot.add_cog(RockPaperScissors(bot))
