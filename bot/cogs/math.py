import discord
import discord.ext.commands as commands
import bot.helpers.tools as tools
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType

import importlib

sympy = importlib.import_module("sympy")
from sympy.parsing.latex import parse_latex
from sympy.plotting.plot import Plot


class Math(commands.Cog, name="math"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="latex",
        description="Compile LaTeX code and view a standalone output.",
        options=[
            create_option(
                name="tex",
                description="The TeX code to compile.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="scale",
                description="The scale to render the LaTeX at. Default is 100.",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            ),
        ],
    )
    async def latex(self, ctx: SlashContext, tex: str, scale: int = 100) -> None:
        try:
            sympy.preview(
                tex,
                viewer="file",
                euler=False,
                filename="texout.png",
                dvioptions=[
                    "-T",
                    "bbox",
                    "-z",
                    "0",
                    "--truecolor",
                    f"-D {(scale/100)*600}",
                    "-bg HTML 2f3136",
                    "-fg gray 1.0",
                ],
            )
        except Exception as e:
            embed = tools.create_error_embed(
                ctx, "Could not compile LaTeX. Check your code and try again."
            )
            await ctx.send(embed=embed)
            return
        embed = tools.create_embed(ctx, "LaTeX")
        file = discord.File("texout.png", filename="texout.png")
        embed.set_image(url="attachment://texout.png")
        await ctx.send(file=file, embed=embed)

    @cog_ext.cog_slash(
        name="calc",
        description="Calculate a mathematical expression.",
        options=[
            create_option(
                name="solve_type",
                description="The type of solve to run.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
                choices=[
                    create_choice(
                        name="solve",
                        value="solve",
                    ),
                    create_choice(
                        name="factor",
                        value="factor",
                    ),
                    create_choice(
                        name="system",
                        value="system",
                    ),
                ],
            ),
            create_option(
                name="equation",
                description="The TeX equation to calculate.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="x_value",
                description="The value of the x variable.",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            ),
            create_option(
                name="y_value",
                description="The value of the y variable.",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            ),
            create_option(
                name="z_value",
                description="The value of the z variable.",
                option_type=SlashCommandOptionType.INTEGER,
                required=False,
            ),
        ],
        guild_ids=[809169133086048257, 801630163866746901],
    )
    async def calc(
        self,
        ctx: SlashContext,
        solve_type: str,
        equation: str,
        x_value: int = None,
        y_value: int = None,
        z_value: int = None,
    ) -> None:
        x = sympy.symbols("x")
        y = sympy.symbols("y")
        z = sympy.symbols("z")

        if solve_type == "solve":
            try:
                expr = parse_latex(equation)
            except Exception as e:
                embed = tools.create_error_embed(
                    ctx, "Could not compile LaTeX expression."
                )
                await ctx.send(embed=embed)
                print(e)
                return
            result = sympy.solveset(expr)
        elif solve_type == "factor":
            try:
                expr = parse_latex(equation)
            except Exception as e:
                embed = tools.create_error_embed(
                    ctx, "Could not compile LaTeX expression."
                )
                await ctx.send(embed=embed)
                print(e)
                return
            result = sympy.factor(expr, deep=True)
        elif solve_type == "system":
            x = sympy.symbols("x")
            y = sympy.symbols("y")
            z = sympy.symbols("z")
            equations = equation.split(", ")
            try:
                exprs = [parse_latex(equation) for equation in equations]
            except Exception as e:
                embed = tools.create_error_embed(
                    ctx, "Could not compile LaTeX expression."
                )
                await ctx.send(embed=embed)
                print(e)
                return
            result = sympy.linsolve(exprs, [x, y, z])
            print(result)

        try:
            sympy.preview(
                result,
                viewer="file",
                euler=False,
                filename="texout.png",
                dvioptions=[
                    "-T",
                    "bbox",
                    "-z",
                    "0",
                    "--truecolor",
                    "-D 600",
                    "-bg HTML 2f3136",
                    "-fg gray 1.0",
                ],
            )
        except Exception as e:
            embed = tools.create_error_embed(ctx, "Could not compile LaTeX output.")
            await ctx.send(embed=embed)
            print(e)
            return
        embed = tools.create_embed(ctx, "Calculation Result")
        file = discord.File("texout.png", filename="texout.png")
        embed.set_image(url="attachment://texout.png")
        await ctx.send(file=file, embed=embed)

    @cog_ext.cog_slash(
        name="graph",
        description="Graph a mathematical expression.",
        options=[
            create_option(
                name="graph_type",
                description="The type of graph to create.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
                choices=[
                    create_choice(
                        name="explicit (using only the variable x, in terms of f(x), or y)",
                        value="explicit",
                    ),
                    create_choice(
                        name="implicit (using variables x and y, used when vertical line test fails)",
                        value="implicit",
                    ),
                    create_choice(
                        name="explicit, 3D (using only variables x and y, in terms of f(x, y), or z)",
                        value="explicit3d",
                    ),
                ],
            ),
            create_option(
                name="equation",
                description="The TeX equation to graph.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
        guild_ids=[809169133086048257, 801630163866746901],
    )
    async def graph(self, ctx: SlashContext, graph_type: str, equation: str):
        await ctx.defer()
        x, y, z = sympy.symbols("x y z")
        # equations = equation.split(', ')
        try:
            expr = parse_latex(equation)
        except Exception as e:
            embed = tools.create_error_embed(ctx, "Could not compile LaTeX expression.")
            await ctx.send(embed=embed)
            print(e)
            return

        # plots = Plot()
        # for expr in exprs:
        #     plot = sympy.plotting.plot_implicit(expr, show=False)
        #     plots.append(plot[0])
        if graph_type == "explicit":
            plot = sympy.plotting.plot(expr, show=False)
        elif graph_type == "implicit":
            plot = sympy.plotting.plot_implicit(expr, show=False)
        elif graph_type == "explicit3d":
            plot = sympy.plotting.plot3d(expr, show=False)
        plot.save("graphout.png")
        embed = tools.create_embed(ctx, "Graph Result")
        file = discord.File("graphout.png", filename="graphout.png")
        embed.set_image(url="attachment://graphout.png")
        if "3d" not in graph_type:
            embed.add_field(
                name="X Intercept(s)",
                value=f"```{[(val, 0) for val in list(sympy.solveset(expr.subs(y, 0)))]}```",
            )
            embed.add_field(
                name="Y Intercept(s)",
                value=f"```{[(0, val) for val in list(sympy.solveset(expr.subs(x, 0)))]}```",
            )
        await ctx.send(file=file, embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Math(bot))
