import discord
from discord.ext import commands
import json
import os
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import SessionLocal, UserStats

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_db(self):
        """Get a database session"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @commands.command(name='tip')
    async def tip(self, ctx, member: discord.Member, *, reason="perfect moment"):
        """Tip a user"""
        try:
            db: Session = next(self.get_db())

            # Update or insert for the tipped user
            db.execute(text("""
                INSERT INTO user_stats (user_id, tips_given, tips_received)
                VALUES (:user_id, 0, 1)
                ON CONFLICT(user_id) DO UPDATE SET tips_received = tips_received + 1
            """), {"user_id": str(member.id)})

            # Update or insert for the command author
            db.execute(text("""
                INSERT INTO user_stats (user_id, tips_given, tips_received)
                VALUES (:user_id, 1, 0)
                ON CONFLICT(user_id) DO UPDATE SET tips_given = tips_given + 1
            """), {"user_id": str(ctx.author.id)})

            db.commit()
            await ctx.send(f'☠️ {ctx.author.mention} tipped {member.mention} for {reason} ☠️')
        except Exception as e:
            db.rollback()
            await ctx.send(f"❌ An error occurred: {str(e)}")
        finally:
            db.close()

    @tip.error
    async def tip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('❌ Please specify a user!\nExample: !tip @user reason')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('❌ User not found!')

    @commands.command(name='top')
    async def top(self, ctx):
        """Show the top tipped users"""
        try:
            db: Session = next(self.get_db())

            # Query the database for the top users who have received the most tips
            result = db.execute(text("""
                SELECT user_id, tips_received FROM user_stats
                WHERE tips_received > 0
                ORDER BY tips_received DESC
                LIMIT 10
            """)).fetchall()

            if not result:
                await ctx.send("❌ No one has been tipped yet!")
                return

            # Format the top users into a message
            message = "🏆 **Top tipped users:**\n\n"
            for i, row in enumerate(result, 1):
                user_id, tips_received = row
                user = await self.bot.fetch_user(int(user_id))
                message += f"{i}. {user.mention if user else f'User ID: {user_id}'} - {tips_received} tips\n"

            await ctx.send(message)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
        finally:
            db.close()

async def setup(bot):
    await bot.add_cog(Utils(bot))
