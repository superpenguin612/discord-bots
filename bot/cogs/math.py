import urllib.parse

import discord
import sympy
from discord import app_commands
from discord.ext import commands
from sympy.parsing.latex import parse_latex
from sympy.plotting.plot import Plot

import bot.helpers.tools as tools


class Math(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Render LaTeX!")
    @app_commands.describe(tex="The LaTeX code to render.")
    async def latex(self, ctx: commands.Context, tex: str) -> None:
        embed = tools.create_embed("LaTeX")
        url = "https://latex.codecogs.com/png.latex?" + urllib.parse.quote(
            "\\huge\\dpi{500}\\color{white}" + tex
        )
        embed.set_image(url=url)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(description="Render the equation for PID control.")
    async def pid(self, ctx: commands.Context) -> None:
        embed = tools.create_embed("PID Control Equation")
        url = "https://latex.codecogs.com/png.latex?" + urllib.parse.quote(
            "\\huge\\dpi{500}\\color{white}" + r"u(t) = K_pe(t) + K_i\int_{0}^{t}e(\tau)d\tau + K_d\frac{\mathrm{d} e(t)}{\mathrm{d} t}"
        )
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    class BadEquationError(Exception):
        pass

    @commands.hybrid_command(
        description="Calculate a mathematical expression.",
    )
    @app_commands.choices(
        solve_type=[
            app_commands.Choice(name="solve", value="solve"),
            app_commands.Choice(name="factor", value="factor"),
            app_commands.Choice(name="system", value="system"),
        ]
    )
    @app_commands.describe(
        solve_type="The type of solve to run.",
        equation="The TeX equation to calculate.",
        x_value='The value of the x variable. Only applies to the "system" solve type.',
        y_value='The value of the y variable. Only applies to the "system" solve type.',
        z_value='The value of the z variable. Only applies to the "system" solve type.',
    )
    async def calc(
        self,
        ctx: commands.Context,
        solve_type: str,
        equation: str,
        x_value: int | None = None,
        y_value: int | None = None,
        z_value: int | None = None,
    ) -> None:
        try:
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
                x = sympy.symbols("x") if not x_value else x_value
                y = sympy.symbols("y") if not y_value else y_value
                z = sympy.symbols("z") if not z_value else z_value
                equations = equation.split(",")
                try:
                    exprs = [parse_latex(equation) for equation in equations]
                except Exception as e:
                    embed = tools.create_error_embed(
                        ctx, "Could not compile LaTeX expression."
                    )
                    await ctx.send(embed=embed)
                    print(e)
                    return
                result = sympy.linsolve(exprs, [x, y, z][0 : len(exprs)])
        except:
            embed = tools.create_error_embed(
                "Sorry, I can't solve that. Figure it out yourself."
            )
            await ctx.send(embed=embed)
            return

        url = "https://latex.codecogs.com/png.latex?" + urllib.parse.quote(
            "\\huge\\dpi{500}\\color{white}" + sympy.latex(result)
        )
        embed = tools.create_embed("Calculation Result")
        embed.set_image(url=url)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Math(bot))
