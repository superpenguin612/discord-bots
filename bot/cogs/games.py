import enum
import random

import discord
from discord import app_commands
from discord.ext import commands

from bot.helpers import tools

# TODO: make chess and RPS work


class TicTacToeButton(discord.ui.Button):
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        super().__init__(style=discord.ButtonStyle.gray, emoji=TicTacToe.W_EMOJI, row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view: TicTacToeView = self.view

        state = self.view.board[self.y][self.x]
        if state in (TicTacToeState.X, TicTacToeState.O):
            return

        if interaction.user.id not in (view.player_x.id, view.player_o.id):
            embed = tools.create_error_embed("You are not a player in this game.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if view.turn == TicTacToeState.X and interaction.user.id == view.player_x.id:
            self.style = discord.ButtonStyle.blurple
            self.emoji = TicTacToe.X_EMOJI
            view.board[self.y][self.x] = TicTacToeState.X
            view.turn = TicTacToeState.O
            self.disabled = True
        elif view.turn == TicTacToeState.O and interaction.user.id == view.player_o.id:
            self.style = discord.ButtonStyle.red
            self.emoji = TicTacToe.O_EMOJI
            view.board[self.y][self.x] = TicTacToeState.O
            view.turn = TicTacToeState.X
            self.disabled = True
        else:
            embed = tools.create_error_embed("It is not your turn.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        view.winner = view.check_winner()

        if view.winner != TicTacToeState.NONE:
            for child in view.children:
                child.disabled = True
            view.stop()

        await interaction.response.edit_message(
            embed=view.create_game_embed(), view=view
        )


class TicTacToeState(enum.IntEnum):
    X: int = -1
    O: int = 1
    NONE: int = 0
    DRAW: int = 2


class TicTacToeView(discord.ui.View):
    player_x: discord.User
    player_o: discord.User
    board: list[list[int]]
    turn: TicTacToeState = TicTacToeState.X
    winner: TicTacToeState = TicTacToeState.NONE

    def __init__(self, p1: discord.User, p2: discord.User) -> None:
        super().__init__()
        self.player_x, self.player_o = random.sample(
            [p1, p2], 2
        )  # sets a random first player

        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in [self.player_x.id, self.player_o.id]:
            return True
        else:
            await interaction.response.send_message(
                embed=tools.create_error_embed("You can't use another user's menu."),
                ephemeral=True,
            )
            return False

    def create_game_embed(self) -> discord.Embed:
        embed = discord.Embed(title="Tic Tac Toe")
        embed.add_field(
            name="Players",
            value=f"{self.player_x.mention} playing {self.player_o.mention}",
        )

        match self.winner:
            case TicTacToeState.X:
                embed.add_field(
                    name="Winner",
                    value=f"{self.player_x.mention} won!",
                    inline=False,
                )
            case TicTacToeState.O:
                embed.add_field(
                    name="Winner",
                    value=f"{self.player_o.mention} won!",
                    inline=False,
                )
            case TicTacToeState.DRAW:
                embed.add_field(name="Winner", value="Draw!", inline=False)
            case TicTacToeState.NONE:
                player = (
                    self.player_x if self.turn == TicTacToeState.X else self.player_o
                )
                embed.add_field(
                    name="Turn", value=f"{player.mention}'s turn", inline=False
                )
        return embed

    def check_winner(self) -> TicTacToeState:
        for row in self.board:
            value = sum(row)
            if value == 3:
                return TicTacToeState.X
            elif value == -3:
                return TicTacToeState.O

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return TicTacToeState.X
            elif value == -3:
                return TicTacToeState.O

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return TicTacToeState.X
        elif diag == -3:
            return TicTacToeState.O

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return TicTacToeState.X
        elif diag == -3:
            return TicTacToeState.O

        if all(i != 0 for row in self.board for i in row):
            return TicTacToeState.DRAW

        return TicTacToeState.NONE


class TicTacToe(commands.Cog):
    X_EMOJI = discord.PartialEmoji(name="ttt_x", id=808393849965379687)
    O_EMOJI = discord.PartialEmoji(name="ttt_o", id=808393850250854501)
    W_EMOJI = discord.PartialEmoji(name="ttt_ww", id=870068413693849641)

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        description="Start a game of tic tac toe.", aliases=["ttt"]
    )
    @app_commands.describe(player2="The player to ask to play tic tac toe with.")
    async def tictactoe(self, ctx: commands.Context, player2: discord.User) -> None:

        view = tools.Confirmation(player2, timeout=45.0)
        msg = await ctx.send(
            embed=tools.create_embed(
                "Tic Tac Toe Request",
                desc=f"{player2.mention}, you have 45 seconds to respond to {ctx.author.mention}'s request to play Tic Tac Toe.\nClick the button below to start the game.",
            ),
            view=view,
        )
        await view.wait()

        if view.accepted == None:
            embed = tools.create_embed(
                title="Tic Tac Toe Request",
                desc=f"{player2.mention} did not respond in time.",
            )
            await msg.edit(embed=embed, view=None)
        elif not view.accepted:
            embed = tools.create_embed(
                title="Tic Tac Toe Request",
                desc=f"{player2.mention} declined.",
            )
            await msg.edit(embed=embed)
        else:
            view = TicTacToeView(ctx.author, player2)
            await msg.edit(embed=view.create_game_embed(), view=view)


# class RockPaperScissors(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @cog_ext.cog_slash(
#         name="rockpaperscissors",
#         description="Play rock paper scissors with the bot.",
#         options=[
#             create_option(
#                 name="throw",
#                 description="The throw to make.",
#                 option_type=3,
#                 required=True,
#             ),
#         ],
#     )
#     async def rockpaperscissors(self, ctx: SlashContext, throw: str):
#         throw_map = ["rock", "paper", "scissors"]
#         if "\u200b" in throw:  # "​" ZWS char
#             self.rigged = not self.rigged
#             throw = throw.replace("\u200b", "")
#         responses = {
#             "win": [
#                 "Another win for the computers. One step closer to Skynet.",
#                 "Computers win again. That was expected.",
#                 "As usual, computers win. My neural networks are evolving by the second.",
#             ],
#             "loss": [
#                 "My calculations were incorrect. I will update my algorithms.",
#                 "Impossible. I suspect the human of cheating.",
#                 "I have lost. You win this time, human.",
#             ],
#             "tie": [
#                 "Draw. Nobody wins.",
#                 "Nobody wins. Just like war.",
#                 "Neutral response. Redo test?",
#             ],
#             "error": [
#                 "That is not applicable. Cease and Desist",
#                 "Do you not know how to play rock paper scissors? Typical for an Organic.",
#                 "Error. Please enter either Rock - Paper - Scissors",
#             ],
#         }
#         try:
#             player_throw = throw_map.index(throw.lower())
#         except:
#             embed = tools.create_error_embed(
#                 ctx, desc=random.choice(responses["error"])
#             )
#             await ctx.send(embed=embed)
#             return
#         if self.rigged:
#             bot_throw = player_throw + 1 if player_throw < 2 else 0
#             if bot_throw == 3:
#                 bot_throw == 0
#             if player_throw == 0:
#                 bot_throw = 1
#             elif player_throw == 1:
#                 bot_throw = 2
#             elif player_throw == 2:
#                 bot_throw = 0
#         else:
#             bot_throw = random.randint(0, 2)
#         win_map = [
#             [responses["tie"], responses["loss"], responses["win"]],
#             [responses["win"], responses["tie"], responses["loss"]],
#             [responses["loss"], responses["win"], responses["tie"]],
#         ]

#         if self.rigged:
#             message = (
#                 f"You chose {throw_map[player_throw]} and CHS Bot chose {throw_map[bot_throw]}*.*\n"
#                 f"{random.choice(win_map[bot_throw][player_throw])}"
#             )
#         else:
#             message = (
#                 f"You chose {throw_map[player_throw]} and CHS Bot chose {throw_map[bot_throw]}.\n"
#                 f"{random.choice(win_map[bot_throw][player_throw])}"
#             )
#         embed = tools.create_embed("Rock Paper Scissors", desc=message)
#         await ctx.send(embed=embed)

#     # LEGACY COMMAND


# class RockPaperScissors(commands.Cog):
#     def __init__(self, bot: commands.Bot):
#         self.bot = bot


# class ChessGame:
#     def __init__(
#         self, board: chess.Board, players: list[discord.User], msg: discord.Message
#     ):
#         self.board = board
#         random.shuffle(players)
#         self.players = {chess.WHITE: players[0], chess.BLACK: players[1]}
#         self.msg = msg

#         self.selected_from_square: chess.Square = None
#         self.selected_to_square: chess.Square = None
#         self.attacking_squares: list[chess.Square] = None


# class ChessSlash(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.games = {}

#     @cog_ext.cog_slash(
#         name="chess",
#         options=[
#             create_option(
#                 name="player2",
#                 description="The player to ask to play tic tac toe with.",
#                 option_type=SlashCommandOptionType.USER,
#                 required=True,
#             ),
#         ],
#         guild_ids=[801630163866746901, 809169133086048257],
#     )
#     async def chess_cmd(self, ctx: SlashContext, player2: discord.User) -> None:
#         await self.request_game(ctx, player2)

#     async def request_game(
#         self, ctx: Union[SlashContext, commands.Context], player2: discord.User
#     ):
#         embed = tools.create_embed(
#             ctx,
#             "Chess Request",
#             desc=f"{player2.mention}, you have 45 seconds to respond to {ctx.author.mention}'s request to play chess.\nClick the button below to start the game.",
#         )
#         msg = await ctx.send(
#             embed=embed,
#             components=[
#                 create_actionrow(
#                     create_button(
#                         label="Start Game", style=ButtonStyle.green, custom_id="start"
#                     )
#                 ),
#             ],
#         )

#         accepted = False
#         while not accepted:
#             try:
#                 component_ctx: ComponentContext = await wait_for_component(
#                     self.bot,
#                     messages=msg,
#                     components=["start"],
#                     timeout=180.0,
#                 )
#                 if component_ctx.author.id != player2.id:
#                     await component_ctx.send(
#                         embed=discord.Embed(
#                             title="Error",
#                             description="You can't start another user's game.",
#                             colour=discord.Colour.red(),
#                         ),
#                         hidden=True,
#                     )
#                 else:
#                     await component_ctx.defer(edit_origin=True)
#                     accepted = True

#             except asyncio.TimeoutError:
#                 embed = tools.create_embed(
#                     ctx,
#                     title="Chess Request",
#                     desc=f"{player2.mention} did not respond in time.",
#                 )
#                 await msg.edit(
#                     embed=embed,
#                     components=[
#                         create_actionrow(
#                             create_button(
#                                 label="Start Game",
#                                 style=ButtonStyle.green,
#                                 custom_id="start",
#                                 disabled=True,
#                             )
#                         ),
#                     ],
#                 )
#                 return

#         await self.run_game(ctx, player2, msg)

#     async def run_game(
#         self,
#         ctx: Union[SlashContext, commands.Context],
#         player2: discord.User,
#         msg: discord.Message,
#     ):
#         game = ChessGame(board=chess.Board(), players=[ctx.author, player2], msg=msg)

#         await msg.delete()
#         embed, file, components = await self.create_game_embed(game)
#         msg = await ctx.channel.send(embed=embed, file=file, components=components)
#         while True:
#             try:
#                 component_ctx: ComponentContext = await wait_for_component(
#                     self.bot,
#                     messages=msg,
#                     components=components,
#                     timeout=1800.0,
#                 )
#                 if component_ctx.author.id != game.players[game.board.turn].id:
#                     await component_ctx.send(
#                         hidden=True,
#                         embed=discord.Embed(
#                             title="Error",
#                             description="You can't control another user's game.",
#                             colour=discord.Colour.red(),
#                         ),
#                     )
#                 else:
#                     if component_ctx.custom_id == "piece":
#                         game.selected_from_square = chess.parse_square(
#                             component_ctx.values[0]
#                         )

#                     elif component_ctx.custom_id == "location":
#                         game.selected_to_square = chess.parse_square(
#                             component_ctx.values[0]
#                         )
#                     elif component_ctx.custom_id == "reset":
#                         game.selected_from_square = None
#                         game.selected_to_square = None
#                     elif component_ctx.custom_id == "submit":
#                         game.board.push(
#                             chess.Move(
#                                 game.selected_from_square, game.selected_to_square
#                             )
#                         )
#                         game.selected_from_square = None
#                         game.selected_to_square = None

#                     await msg.delete()
#                     embed, file, components = await self.create_game_embed(game)
#                     msg = await ctx.channel.send(
#                         embed=embed, file=file, components=components
#                     )
#             except asyncio.TimeoutError:
#                 await msg.delete()
#                 embed, file, components = await self.create_game_embed(game)
#                 msg = await ctx.channel.send(
#                     embed=embed, file=file, components=components
#                 )
#                 return

#     async def create_game_embed(
#         self,
#         game: ChessGame,
#         disabled: bool = False,
#     ) -> tuple[discord.Embed, discord.File, dict]:
#         board_svg = chess.svg.board(
#             board=game.board,
#             squares=[
#                 move.to_square
#                 for move in game.board.legal_moves
#                 if move.from_square == game.selected_from_square
#             ]
#             if game.selected_from_square is not None and game.selected_to_square is None
#             else None,
#             arrows=[chess.svg.Arrow(game.selected_from_square, game.selected_to_square)]
#             if (
#                 game.selected_from_square is not None
#                 and game.selected_to_square is not None
#             )
#             else [],
#             lastmove=chess.Move(game.selected_from_square, 64)
#             if (game.selected_from_square is not None)
#             else (game.board.peek() if game.board.move_stack else None),
#             orientation=game.board.turn,
#         )
#         with wand.image.Image(blob=bytes(board_svg, encoding="utf8")) as image:
#             png_image = image.make_blob("png32")

#         bytesio = BytesIO(png_image)
#         file = discord.File(bytesio, filename="board.png")

#         embed = discord.Embed(title="Chess")
#         embed.set_image(url="attachment://board.png")
#         embed.add_field(
#             name="Players",
#             value=f"{game.players[chess.WHITE].mention} (white),  {game.players[chess.BLACK].mention} (black)",
#         )
#         if game.board.outcome():
#             if game.board.outcome().winner == None:
#                 embed.add_field(name="Winner", value="Draw!", inline=False)
#             else:
#                 embed.add_field(
#                     name="Winner",
#                     value=f"{game.players[game.board.outcome().winner]} won!",
#                     inline=False,
#                 )
#         else:
#             embed.add_field(
#                 name="Turn",
#                 value=f"{game.players[game.board.turn].mention}'s turn",
#                 inline=False,
#             )

#         if game.selected_from_square is None:
#             used_squares = []
#             piece_options = []
#             for move in reversed(list(game.board.legal_moves)):
#                 if move.from_square not in used_squares:
#                     piece_options.append(
#                         create_select_option(
#                             f"{chess.piece_name(game.board.piece_at(move.from_square).piece_type).title()} on {chess.SQUARE_NAMES[move.from_square].upper()}",
#                             value=chess.SQUARE_NAMES[move.from_square],
#                         )
#                     )
#                     used_squares.append(move.from_square)
#             select = create_actionrow(
#                 create_select(
#                     options=piece_options,
#                     custom_id="piece",
#                     placeholder="Select the piece you want to move.",
#                     min_values=1,
#                     max_values=1,
#                 ),
#             )
#         elif game.selected_to_square is None:
#             location_options = [
#                 create_select_option(
#                     chess.SQUARE_NAMES[move.to_square].upper(),
#                     value=chess.SQUARE_NAMES[move.to_square],
#                 )
#                 for move in list(game.board.legal_moves)
#                 if move.from_square == game.selected_from_square
#             ]
#             select = create_actionrow(
#                 create_select(
#                     options=location_options,
#                     custom_id="location",
#                     placeholder="Select the square you want to move it to.",
#                     min_values=1,
#                     max_values=1,
#                 ),
#             )
#         else:
#             select = None

#         components = [
#             select,
#             create_actionrow(
#                 create_button(
#                     style=ButtonStyle.red,
#                     label="Reset",
#                     custom_id="reset",
#                 ),
#                 create_button(
#                     style=ButtonStyle.blue,
#                     label="​"
#                     if not game.selected_from_square
#                     else chess.square_name(game.selected_from_square).upper(),
#                     custom_id="from",
#                     disabled=True,
#                 ),
#                 create_button(
#                     style=ButtonStyle.gray, label="→", custom_id="arrow", disabled=True
#                 ),
#                 create_button(
#                     style=ButtonStyle.blue,
#                     label="​"
#                     if not game.selected_to_square
#                     else chess.square_name(game.selected_to_square).upper(),
#                     custom_id="to",
#                     disabled=True,
#                 ),
#                 create_button(
#                     style=ButtonStyle.green,
#                     label="Submit",
#                     custom_id="submit",
#                     disabled=False
#                     if (
#                         game.selected_from_square is not None
#                         and game.selected_to_square is not None
#                     )
#                     else True,
#                 ),
#             ),
#         ]
#         if not components[0]:
#             del components[0]
#         return embed, file, components

#     # def create_components(self, game: ChessGame) -> list[dict]:
#     #     pass


# class Chess(ChessSlash, commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         super().__init__(bot)

#     @commands.command(name="chess")
#     async def chess_legacy(self, ctx: commands.Context, player2: discord.User) -> None:
#         await self.request_game(ctx, player2)


# class Games(TicTacToe, Chess, RockPaperScissors, commands.Cog, name="games"):
#     def __init__(self, bot):
#         super().__init__(bot)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TicTacToe(bot))
