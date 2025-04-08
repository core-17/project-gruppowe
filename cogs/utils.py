import discord
from discord.ext import commands
import json
import os
from collections import defaultdict

# Path to the stats file
STATS_FILE = 'tip_stats.json'

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tip_stats = self.load_stats()

    def load_stats(self):
        """Load stats from the file"""
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return defaultdict(int, json.load(f))
        return defaultdict(int)

    def save_stats(self):
        """Save stats to the file"""
        with open(STATS_FILE, 'w') as f:
            json.dump(dict(self.tip_stats), f)

    @commands.command(name='hello')
    async def hello(self, ctx):
        """Say hello to the bot"""
        await ctx.send(f'Hello, {ctx.author.name}! 👋')

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check the bot's latency"""
        await ctx.send(f'Ping! Latency: {round(self.bot.latency * 1000)}ms')

    @commands.command(name='tip')
    async def tip(self, ctx, member: discord.Member, *, reason="perfect moment"):
        """Tip a user"""
        # Increment the tip counter for the user
        self.tip_stats[str(member.id)] += 1
        self.save_stats()
        await ctx.send(f'☠️ {ctx.author.mention} tipped {member.mention} for {reason} ☠️')

    @tip.error
    async def tip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('❌ Please specify a user!\nExample: !tip @user reason')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('❌ User not found!')

    @commands.command(name='top')
    async def top(self, ctx):
        """Show the top tipped users"""
        if not self.tip_stats:
            await ctx.send("❌ No one has been tipped yet!")
            return
        
        # Sort users by the number of tips
        sorted_stats = sorted(self.tip_stats.items(), key=lambda x: int(x[1]), reverse=True)
        
        # Create a message with the top users
        message = "🏆 Top tipped users:\n\n"
        shown_users = 0
        
        for user_id, tips in sorted_stats:
            try:
                user = await ctx.guild.fetch_member(int(user_id))
                if user:
                    shown_users += 1
                    message += f"{shown_users}. {user.mention} - {tips} tip{'s' if tips != 1 else ''}\n"
            except discord.NotFound:
                continue
        
        if shown_users == 0:
            await ctx.send("❌ No active users found in the top!")
        else:
            await ctx.send(message)

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
            "👥 Moderation": {
                "!kick @user": "Kick a user from the server",
                "!ban @user": "Ban a user on the server",
                "!clear <channel type>": "Delete all channels of the specified type",
                "!clean [amount]": "Delete messages in the current channel",
                "!delete_voice_channel <name>": "Delete voice channels with the specified name"
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
    await bot.add_cog(Utils(bot))
