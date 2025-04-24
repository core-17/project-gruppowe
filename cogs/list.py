import discord
from discord.ext import commands

class List(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hello')
    async def hello(self, ctx):
        """Say hello to the bot"""
        await ctx.send(f'Hello, {ctx.author.name}! 👋')

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check the bot's latency"""
        await ctx.send(f'Ping! Latency: {round(self.bot.latency * 1000)}ms')

    @commands.command(name='list')
    async def list_commands(self, ctx):
        """Show a list of all available commands"""
        embed = discord.Embed(
            title="📋 Bot Command List",
            description="Here is a list of all available commands:",
            color=discord.Color.blue()
        )

        commands_list = {
            "🎵 Music": {
                "!music <link>": "Add music from YouTube to the queue",
                "!skip": "Skip the current track",
                "!stop": "Stop playback and clear the queue",
                "!queue (!q)": "Show the current music queue"
            },
            "🎮 Games": {
                "!sales": "Show discounts on Steam",
                "!epic": "Show free games in the Epic Games Store"
            },
             "🔢 Calculator": {
                    "!calc <expression>": "Perform mathematical calculations (e.g. !calc 2 + 2)",
                    "!calc <function>(x)": "Calculate mathematical functions (sqrt, sin, cos, tan, log, ln, abs, factorial)",
                    "!binary <number>": "Convert between decimal and binary numbers",
                    "!hex <number>": "Convert between decimal and hexadecimal numbers"
                },
            "👥 Moderation": {
                "!kick @user": "Kick a user from the server",
                "!ban @user": "Ban a user on the server",
                "!clear <channel type>": "Delete all channels of the specified type",
                "!clean [amount]": "Delete messages in the current channel",
                "!delete_voice_channel <name>": "Delete voice channels with the specified name",
                "!delete_text_channel <name>": "Delete text channels with the specified name",
            },
            "ℹ️ Other": {
                "!hello": "Say hello to the bot",
                "!list": "Show this list of commands",
                "!tip @user": "Tip a user",
                "!top": "Show the top tipped users"
            }
        }

        for category, commands in commands_list.items():
            commands_text = ""
            for cmd, desc in commands.items():
                commands_text += f"**{cmd}**\n└ {desc}\n"
            embed.add_field(
                name=category,
                value=commands_text,
                inline=False
            )

        embed.set_footer(text="Use commands with the ! prefix")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(List(bot))