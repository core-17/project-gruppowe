import discord
from discord.ext import commands
import typing

# List of allowed users (add new usernames here)
ALLOWED_USERS = [
    '_fate_._',
    'horafy',
    'itshazen',
    'core_17',
    # Add other usernames here, for example:
    # 'another_user',
    # 'moderator_nick',
]

def is_allowed_user():
    async def predicate(ctx):
        if ctx.author.name in ALLOWED_USERS:
            return True
        await ctx.send(f"❌ Only allowed users can use this command!")
        return False
    return commands.check(predicate)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @is_allowed_user()
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        try:
            # Attempt to send a DM to the user
            try:
                embed = discord.Embed(
                    title="❌ You have been kicked from the server",
                    description=f"**Server:** {ctx.guild.name}\n**Reason:** {reason}",
                    color=discord.Color.red()
                )
                await member.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("⚠️ Could not send a DM to the user (they might have DMs disabled)")
            except Exception as e:
                print(f"Error sending DM: {e}")
            
            # Kick the user
            await member.kick(reason=reason)
            await ctx.send(f'👢 User {member.mention} has been kicked from the server.\nReason: {reason}')
        except discord.Forbidden:
            await ctx.send('❌ I do not have permission to perform this action!')
        except discord.HTTPException:
            await ctx.send('❌ An error occurred while trying to kick the user.')

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('❌ You do not have permission to use this command!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('❌ Please specify the user to kick!\nExample: !kick @user reason')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('❌ User not found!')

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @is_allowed_user()
    async def ban(self, ctx, member: typing.Union[discord.Member, str], *, reason=None):
        """Ban a user or all users on the server"""
        try:
            if isinstance(member, str) and member.lower() == 'all':
                # Mass ban all users
                banned_count = 0
                failed_count = 0
                
                # Create an embed for progress
                progress_embed = discord.Embed(
                    title="🔨 Mass banning users",
                    description="Process started...",
                    color=discord.Color.red()
                )
                progress_message = await ctx.send(embed=progress_embed)
                
                # Get all members of the server
                members = ctx.guild.members
                
                for target in members:
                    # Skip the bot and the user who issued the command
                    if target.bot or target == ctx.author:
                        continue
                        
                    try:
                        # Attempt to send a DM to the user
                        try:
                            embed = discord.Embed(
                                title="❌ You have been banned from the server",
                                description=f"**Server:** {ctx.guild.name}\n**Reason:** {reason if reason else 'Mass ban'}",
                                color=discord.Color.red()
                            )
                            await target.send(embed=embed)
                        except:
                            pass  # Ignore DM errors
                        
                        # Ban the user
                        await target.ban(reason=f"Mass ban | {reason if reason else 'No reason provided'}")
                        banned_count += 1
                        
                        # Update progress every 5 bans
                        if banned_count % 5 == 0:
                            progress_embed.description = f"Banned: {banned_count}\nErrors: {failed_count}"
                            await progress_message.edit(embed=progress_embed)
                            
                    except discord.Forbidden:
                        failed_count += 1
                    except Exception as e:
                        failed_count += 1
                        print(f"Error banning {target.name}: {str(e)}")
                
                # Final message
                final_embed = discord.Embed(
                    title="🔨 Mass ban completed",
                    description=f"✅ Successfully banned: {banned_count}\n❌ Errors: {failed_count}",
                    color=discord.Color.green()
                )
                await progress_message.edit(embed=final_embed)
                
            else:
                # Regular ban for a single user
                if not isinstance(member, discord.Member):
                    raise commands.MemberNotFound(member)
                    
                # Attempt to send a DM to the user
                try:
                    embed = discord.Embed(
                        title="❌ You have been banned from the server",
                        description=f"**Server:** {ctx.guild.name}\n**Reason:** {reason if reason else 'No reason provided'}",
                        color=discord.Color.red()
                    )
                    await member.send(embed=embed)
                except:
                    pass  # Ignore DM errors
                
                await member.ban(reason=reason)
                await ctx.send(f'🔨 User {member.mention} has been banned from the server.\nReason: {reason if reason else "No reason provided"}')
                
        except discord.Forbidden:
            await ctx.send('❌ I do not have permission to perform this action!')
        except commands.MemberNotFound:
            await ctx.send('❌ User not found!')
        except Exception as e:
            await ctx.send(f'❌ An error occurred: {str(e)}')

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('❌ You do not have permission to use this command!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('❌ Please specify a user or "all" to ban everyone!\nExample: !ban @user reason\nOr: !ban all reason')

    @commands.command(name='clear')
    @commands.has_permissions(manage_channels=True)
    @is_allowed_user()
    async def clear(self, ctx, channel_type: str):
        """Delete all channels of the specified type"""
        if channel_type.lower() not in ['chat', 'voice-chat']:
            await ctx.send("❌ Please specify a valid channel type (chat or voice-chat)!")
            return

        deleted_count = 0
        
        try:
            # Get all channels of the specified type
            if channel_type.lower() == 'chat':
                channels = [c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)]
                channel_type_name = "text channels"
            else:  # voice-chat
                channels = [c for c in ctx.guild.channels if isinstance(c, discord.VoiceChannel)]
                channel_type_name = "voice channels"

            if not channels:
                await ctx.send(f"❌ No {channel_type_name} found on the server!")
                return

            # Delete the channels
            for channel in channels:
                try:
                    await channel.delete()
                    deleted_count += 1
                except discord.Forbidden:
                    await ctx.send(f"❌ I do not have permission to delete the channel {channel.name}!")
                except Exception as e:
                    await ctx.send(f"❌ Error deleting the channel {channel.name}: {str(e)}")

            await ctx.send(f"🗑️ Deleted {deleted_count} {channel_type_name}")

        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to manage channels!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have permission to manage channels!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please specify the channel type!\nExample: !clear chat or !clear voice-chat")

    @commands.command(name='clean')
    @commands.has_permissions(manage_messages=True)
    @is_allowed_user()
    async def clean(self, ctx, amount: int = None):
        """Delete messages in the current channel"""
        if amount is not None and amount <= 0:
            await ctx.send("❌ The number of messages must be greater than 0!")
            return

        try:
            # Delete the user's command
            await ctx.message.delete()
            
            # If no amount is specified, delete all messages
            if amount is None:
                deleted = 0
                async with ctx.typing():
                    async for message in ctx.channel.history(limit=None):
                        try:
                            await message.delete()
                            deleted += 1
                        except discord.NotFound:
                            continue
                        except discord.Forbidden:
                            await ctx.send("❌ I do not have permission to delete some messages!")
                            break
            else:
                # Delete the specified number of messages
                deleted = 0
                async with ctx.typing():
                    async for message in ctx.channel.history(limit=amount):
                        try:
                            await message.delete()
                            deleted += 1
                        except discord.NotFound:
                            continue
                        except discord.Forbidden:
                            await ctx.send("❌ I do not have permission to delete some messages!")
                            break

            # Send a result message
            result_message = await ctx.send(f"🗑️ Deleted {deleted} messages")
            # Delete the result message after 5 seconds
            await result_message.delete(delay=5)

        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to delete messages!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

    @clean.error
    async def clean_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have permission to delete messages!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Please specify a valid number of messages!\nExample: !clean 10")

    @commands.command(name='delete_voice_channel')
    @commands.has_permissions(manage_channels=True)
    @is_allowed_user()
    async def delete_voice_channel(self, ctx, *, channel_name: str):
        """Delete voice channels with the specified name"""
        try:
            # Get all voice channels on the server
            voice_channels = [c for c in ctx.guild.channels if isinstance(c, discord.VoiceChannel)]
            deleted_count = 0

            for channel in voice_channels:
                if channel.name.lower() == channel_name.lower():
                    try:
                        await channel.delete()
                        deleted_count += 1
                    except discord.Forbidden:
                        await ctx.send(f"❌ I do not have permission to delete the channel {channel.name}!")
                    except Exception as e:
                        await ctx.send(f"❌ Error deleting the channel {channel.name}: {str(e)}")

            if deleted_count > 0:
                await ctx.send(f"🗑️ Deleted {deleted_count} voice channels with the name '{channel_name}'")
            else:
                await ctx.send(f"❌ No voice channels with the name '{channel_name}' found!")

        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to manage channels!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

    @commands.command(name='delete_text_channel')
    @commands.has_permissions(manage_channels=True)
    @is_allowed_user()
    async def delete_text_channel(self, ctx, *, channel_name: str):
        """Delete text channels with the specified name"""
        try:
            # Get all text channels on the server
            text_channels = [c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)]
            deleted_count = 0

            for channel in text_channels:
                if channel.name.lower() == channel_name.lower():
                    try:
                        await channel.delete()
                        deleted_count += 1
                    except discord.Forbidden:
                        await ctx.send(f"❌ I do not have permission to delete the channel {channel.name}!")
                    except Exception as e:
                        await ctx.send(f"❌ Error deleting the channel {channel.name}: {str(e)}")

            if deleted_count > 0:
                await ctx.send(f"🗑️ Deleted {deleted_count} text channels with the name '{channel_name}'")
            else:
                await ctx.send(f"❌ No text channels with the name '{channel_name}' found!")

        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to manage channels!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
