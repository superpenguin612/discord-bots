import discord
from discord.ext import commands
from bot.helpers import tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType
import asyncio
import random

class Games(commands.Cog, name='games'):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.rigged = False

    @cog_ext.cog_slash(
        name='tictactoe',
        description='Start a tic tac toe game with someone.',
        options=[
            create_option(
                name='player2',
                description='The player to ask to play tic tac toe with.',
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
        ],
    )
    async def tictactoe(self, ctx, player2: discord.User):
        embed = tools.create_embed(ctx, "Tic Tac Toe Request", desc=f'{player2.mention}, you have 45 seconds to respond to {ctx.author.mention}\'s request to play Tic Tac Toe.\nReact with 👍 to accept, 👎 to decline.')
        request_msg = await ctx.send(embed=embed)
        await request_msg.add_reaction('👍')
        await request_msg.add_reaction('👎')
        def check(reaction, user):
            return user == player2 and reaction.message == request_msg
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=45)
        except asyncio.TimeoutError:
            embed = tools.create_error_embed(ctx, f"Sorry, {player2.mention} didn't respond in time!")
            await request_msg.edit(embed=embed)
            return
        
        if reaction.emoji == '👍':
            embed = tools.create_embed(ctx, "Tic Tac Toe Request", desc=f"{player2.mention} accepted {ctx.author.mention}'s request to play Tic Tac Toe.")
            await request_msg.edit(embed=embed)
            await request_msg.clear_reactions()
            await self.start_game(ctx, request_msg, player2)
        elif reaction.emoji == '👎':
            embed = tools.create_embed(ctx, "Tic Tac Toe Request", desc=f"{player2.mention} rejected {ctx.author.mention}'s request to play Tic Tac Toe.")
            await request_msg.edit(embed=embed)
            await request_msg.clear_reactions()
            return
        else:
            embed = tools.create_error_embed(ctx, f"Invalid reaction.")
            await request_msg.edit(embed=embed)
            return
    
    # LEGACY COMMAND

    @commands.command(aliases=['tic', 'ttt'])
    async def tictactoe_legacy(self, ctx, player2: discord.User):
        embed = tools.create_embed(ctx, "Tic Tac Toe Request", desc=f'{player2.mention}, you have 45 seconds to respond to {ctx.author.mention}\'s request to play Tic Tac Toe.\nReact with 👍 to accept, 👎 to decline.')
        request_msg = await ctx.send(embed=embed)
        await request_msg.add_reaction('👍')
        await request_msg.add_reaction('👎')
        def check(reaction, user):
            return user == player2 and reaction.message == request_msg
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=45)
        except asyncio.TimeoutError:
            embed = tools.create_error_embed(ctx, f"Sorry, {player2.mention} didn't respond in time!")
            await request_msg.edit(embed=embed)
            return
        
        if reaction.emoji == '👍':
            embed = tools.create_embed(ctx, "Tic Tac Toe Request", desc=f"{player2.mention} accepted {ctx.author.mention}'s request to play Tic Tac Toe.")
            await request_msg.edit(embed=embed)
            await request_msg.clear_reactions()
            await self.start_game(ctx, request_msg, player2)
        elif reaction.emoji == '👎':
            embed = tools.create_embed(ctx, "Tic Tac Toe Request", desc=f"{player2.mention} rejected {ctx.author.mention}'s request to play Tic Tac Toe.")
            await request_msg.edit(embed=embed)
            await request_msg.clear_reactions()
            return
        else:
            embed = tools.create_error_embed(ctx, f"Invalid reaction.")
            await request_msg.edit(embed=embed)
            return

    async def start_game(self, ctx, msg, p2):
        game = {}
        game['board'] = {
            'a1':'', 
            'b1':'', 
            'c1':'', 
            'a2':'', 
            'b2':'', 
            'c2':'', 
            'a3':'', 
            'b3':'', 
            'c3':''
        }
        game['p1'] = ctx.message.author
        game['p2'] = p2
        game['turn'] = 'p1'
        game['winner'] = ''

        board_text = self.create_board_text(game['board'])
        embed = self.create_game_embed(game, board_text)
        await msg.edit(embed=embed)
        for arrow in ['↖️','⬆️','↗️','⬅️','⏺','➡️','↙️','⬇️','↘️']:
            await msg.add_reaction(arrow)
        game['msg'] = msg
        self.games[msg.id] = game
    
    def create_game_embed(self, game, board_text):
        embed = discord.Embed(title='Tic Tac Toe')
        embed.add_field(name='Board', value=board_text, inline=False)
        embed.add_field(name='Players', value=f'{game["p1"].mention} playing {game["p2"].mention}', inline=False)
        if game['winner']:
            if game['winner'] == 'draw':
                embed.add_field(name='Winner', value='Draw!', inline=False)
            else:
                embed.add_field(name='Winner', value=f'{game[game["winner"]].mention} won!')
        else:
            embed.add_field(name='Turn', value=f'{game[game["turn"]].mention}\'s turn', inline=False)
        return embed

    def create_board_text(self, board):
        iter_list = [['a1','b1','c1'],['a2','b2','c2'],['a3','b3','c3']]
        text = ''
        for row in iter_list:
            for item in row:
                if board[item] == 'p1':
                    text += '<:ttt_x:808393849965379687>'
                elif board[item] == 'p2':
                    text += '<:ttt_o:808393850250854501>'
                elif board[item] == '':
                    text += '<:ttt_w:808396628766621787>'
            text += '\n'
        return text

    async def update_game(self, game_id, game, location, player):
        game['board'][location] = player
        if player == 'p1':
            game['turn'] = 'p2'
        if player == 'p2':
            game['turn'] = 'p1'
        game['winner'] = self.check_victory(game)
        self.games[game_id] = game
        board_text = self.create_board_text(game['board'])
        embed = self.create_game_embed(game, board_text)
        await game['msg'].edit(embed=embed)
    
    def check_victory(self, game):
        iter_list = [['a1','b1','c1'],['a2','b2','c2'],['a3','b3','c3']]
        winner = None

        # draw
        if not '' in game['board'].values():
            winner = 'draw'

        # vertical
        for i in range(0,2):
            if game['board'][iter_list[i][0]] == game['board'][iter_list[i][1]] == game['board'][iter_list[i][2]]:
                winner = game['board'][iter_list[i][0]]        
        # horizontal
        for i in range(0,2):
            if game['board'][iter_list[0][i]] == game['board'][iter_list[1][i]] == game['board'][iter_list[2][i]]:
                winner = game['board'][iter_list[0][i]]
        
        # diagonal
        if game['board'][iter_list[0][0]] == game['board'][iter_list[1][1]] == game['board'][iter_list[2][2]]:
            winner = game['board'][iter_list[1][1]]

        # anti-diagonal
        if game['board'][iter_list[2][0]] == game['board'][iter_list[1][1]] == game['board'][iter_list[0][2]]:
            winner = game['board'][iter_list[1][1]]

        return winner

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        compare_dict = {
            '↖️':'a1',
            '⬆️':'b1',
            '↗️':'c1',
            '⬅️':'a2',
            '⏺':'b2',
            '➡️':'c2',
            '↙️':'a3',
            '⬇️':'b3',
            '↘️':'c3'
        }
        active_game = self.games.get(reaction.message.id)
        
        if active_game and (user.id != self.bot.user.id):
            location = compare_dict[reaction.emoji]
            if user.id == active_game[active_game['turn']].id and not active_game['winner']:
                if active_game['board'][location] == '':
                    await self.update_game(reaction.message.id, active_game, location, active_game['turn'])
            await reaction.remove(user)

    @cog_ext.cog_slash(
        name='rockpaperscissors',
        description='Play rock paper scissors with the bot.',
        options=[
            create_option(
                name='throw',
                description='The throw to make.',
                option_type=3,
                required=True
            ),
        ],
    )
    async def rockpaperscissors(self, ctx, throw):
        throw_map = ['rock', 'paper', 'scissors']
        if '\u200b' in throw: # "​" ZWS char
            self.rigged = not self.rigged
            throw = throw.replace('\u200b', '')
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
            embed = tools.create_error_embed(ctx, desc=random.choice(responses["error"]))
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
            bot_throw = random.randint(0,2)
        win_map = [
            [responses['tie'], responses['loss'], responses['win']], 
            [responses['win'], responses['tie'], responses['loss']], 
            [responses['loss'], responses['win'], responses['tie']]
        ]
        
        if self.rigged:
            message = (f'You chose {throw_map[player_throw]} and CHS Bot chose {throw_map[bot_throw]}*.*\n'
                f'{random.choice(win_map[bot_throw][player_throw])}')
        else:
            message = (f'You chose {throw_map[player_throw]} and CHS Bot chose {throw_map[bot_throw]}.\n'
            f'{random.choice(win_map[bot_throw][player_throw])}')
        embed = tools.create_embed(ctx, 'Rock Paper Scissors', desc=message)
        await ctx.send(embed=embed)


    # LEGACY COMMAND
    @commands.command(
        name='rockpaperscissors',
        brief='Play Rock Paper Scissors with the bot.',
        aliases=['rps']
    )
    async def rps_legacy(self, ctx, *, throw):
        throw_map = ['rock', 'paper', 'scissors']
        if '\u200b' in ctx.message.content: # "​"
            self.rigged = not self.rigged
            throw = throw.replace('\u200b', '')
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
            embed = tools.create_error_embed(ctx, desc=random.choice(responses["error"]))
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
            bot_throw = random.randint(0,2)
        win_map = [
            [responses['tie'], responses['loss'], responses['win']], 
            [responses['win'], responses['tie'], responses['loss']], 
            [responses['loss'], responses['win'], responses['tie']]
        ]
        
        if self.rigged:
            message = (f'You chose {throw_map[player_throw]} and CHS Bot chose {throw_map[bot_throw]}*.*\n'
                f'{random.choice(win_map[bot_throw][player_throw])}')
        else:
            message = (f'You chose {throw_map[player_throw]} and CHS Bot chose {throw_map[bot_throw]}.\n'
            f'{random.choice(win_map[bot_throw][player_throw])}')
        embed = tools.create_embed(ctx, 'Rock Paper Scissors', desc=message)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Games(bot))