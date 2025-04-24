import discord
from discord.ext import commands
import re
import math
import operator

class Calculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dictionary of supported operations and their corresponding functions
        self.operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            'x': operator.mul,  # Alternative for multiplication
            '/': operator.truediv,
            '^': operator.pow,
            '%': operator.mod,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log10,
            'ln': math.log,
            'abs': abs,
            'factorial': math.factorial
        }

    @commands.command(name='calc')
    async def calculate(self, ctx, *, expression: str = None):
        """Performs mathematical calculations
        Example: !calc 2 + 2"""
        
        if not expression:
            await ctx.send("❌ Please provide an expression to calculate!\nExample: !calc 2 + 2")
            return
        
        try:
            # Clean the expression from unnecessary characters
            expression = expression.replace('`', '').strip()
            
            # Process specific mathematical functions
            if expression.startswith(('sqrt', 'sin', 'cos', 'tan', 'log', 'ln', 'abs', 'factorial')):
                # Extract function name and its argument
                match = re.match(r'([a-z]+)\s*\(\s*([-+]?\d*\.?\d+)\s*\)', expression)
                if match:
                    func_name, arg = match.groups()
                    arg = float(arg)
                    
                    if func_name in self.operations:
                        result = self.operations[func_name](arg)
                    else:
                        await ctx.send(f"❌ Unknown function: {func_name}")
                        return
                else:
                    await ctx.send(f"❌ Invalid function syntax. Example: !calc sqrt(16)")
                    return
            else:
                # Process standard arithmetic expressions
                # Security check - remove potentially dangerous elements
                sanitized = re.sub(r'[^0-9+\-*/^%().\s]', '', expression)
                
                # Replace ^ with ** for exponentiation
                sanitized = sanitized.replace('^', '**')
                
                # Safe evaluation
                result = eval(sanitized, {"__builtins__": {}}, {"math": math})
            
            # Format the result
            if isinstance(result, int) or result.is_integer():
                formatted_result = str(int(result))
            else:
                formatted_result = f"{result:.6f}".rstrip('0').rstrip('.')
            
            # Create an embed message
            embed = discord.Embed(
                title="🧮 Calculator Result",
                color=discord.Color.blue()
            )
            embed.add_field(name="Expression", value=f"```{expression}```", inline=False)
            embed.add_field(name="Result", value=f"```{formatted_result}```", inline=False)
            
            await ctx.send(embed=embed)
        
        except ZeroDivisionError:
            await ctx.send("❌ Error: Division by zero!")
        except ValueError as e:
            await ctx.send(f"❌ Value Error: {str(e)}")
        except SyntaxError:
            await ctx.send("❌ Syntax Error: Invalid expression.")
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

    @commands.command(name='binary')
    async def binary(self, ctx, *, number: str = None):
        """Convert between decimal and binary numbers
        Examples:
        !binary 10 (decimal to binary)
        !binary 0b1010 (binary to decimal)
        """
        if not number:
            await ctx.send("❌ Please provide a number to convert!\nExamples:\n!binary 10\n!binary 0b1010")
            return
        
        try:
            number = number.strip()
            
            # Check if it's a binary number starting with 0b
            if number.startswith('0b'):
                # Convert from binary to decimal
                decimal_value = int(number, 2)
                result = f"Binary {number} = Decimal {decimal_value}"
            else:
                # Convert from decimal to binary
                try:
                    decimal_value = int(number)
                    binary_value = bin(decimal_value)
                    result = f"Decimal {decimal_value} = Binary {binary_value}"
                except ValueError:
                    await ctx.send("❌ Please provide a valid decimal or binary number.")
                    return
            
            embed = discord.Embed(
                title="🔢 Binary Converter",
                description=result,
                color=discord.Color.green()
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

    @commands.command(name='hex')
    async def hexadecimal(self, ctx, *, number: str = None):
        """Convert between decimal and hexadecimal numbers
        Examples:
        !hex 255 (decimal to hex)
        !hex 0xFF (hex to decimal)
        """
        if not number:
            await ctx.send("❌ Please provide a number to convert!\nExamples:\n!hex 255\n!hex 0xFF")
            return
        
        try:
            number = number.strip()
            
            # Check if it's a hexadecimal number
            if number.startswith('0x') or any(c in "abcdefABCDEF" for c in number):
                # Convert from hex to decimal
                if not number.startswith('0x'):
                    number = '0x' + number
                decimal_value = int(number, 16)
                result = f"Hex {number} = Decimal {decimal_value}"
            else:
                # Convert from decimal to hex
                try:
                    decimal_value = int(number)
                    hex_value = hex(decimal_value)
                    result = f"Decimal {decimal_value} = Hex {hex_value}"
                except ValueError:
                    await ctx.send("❌ Please provide a valid decimal or hexadecimal number.")
                    return
            
            embed = discord.Embed(
                title="🔢 Hexadecimal Converter",
                description=result,
                color=discord.Color.purple()
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Calculator(bot))