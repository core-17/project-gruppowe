import discord
from discord.ext import commands
import random

class Sort(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_ids = {}  # Store IDs for each server

    @commands.command(name="randomids")
    async def random_ids(self, ctx):
        """Generates random IDs for all users (except bots) on the server."""
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used on a server.")
            return

        members = [member for member in guild.members if not member.bot]
        if not members:
            await ctx.send("No users found.")
            return

        ids = {member: random.randint(1, 1000) for member in members}
        self.user_ids[guild.id] = ids

        msg = "Users and their random IDs:\n"
        for member, user_id in ids.items():
            msg += f"{member.display_name}: {user_id}\n"

        await ctx.send(msg)

    @commands.command(name="stalinsort")
    async def stalin_sort(self, ctx):
        """
        Performs Stalin sort by saved IDs and kicks those who do not fit the order.
        """
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used on a server.")
            return

        ids = self.user_ids.get(guild.id)
        if not ids:
            await ctx.send("First generate IDs with the !randomids command.")
            return

        gulag = list(ids.values())
        urn = []
        for i, item in enumerate(gulag):
            if not urn or item >= urn[-1]:
                urn.append(item)
            else:
                member_to_kick = list(ids.keys())[i]
                try:
                    await member_to_kick.kick(reason="ID does not fit the sorting order.")
                    await ctx.send(f"{member_to_kick.name} was kicked for breaking the order.")
                except discord.Forbidden:
                    await ctx.send(f"Could not kick {member_to_kick.name}. Missing permission.")
                except discord.HTTPException as e:
                    await ctx.send(f"Error kicking {member_to_kick.name}: {e}")

        await ctx.send(f"Sorted IDs: {urn}")

# Add Cog to the bot
async def setup(bot):
    await bot.add_cog(Sort(bot))

