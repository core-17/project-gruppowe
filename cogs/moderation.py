import discord
from discord.ext import commands
import typing

# Список дозволених користувачів (можна додавати нові ніки)
ALLOWED_USERS = [
    '_fate_._',
    'horafy',
    'itshazen',
     'core_17',

    # Додайте інші ніки тут, наприклад:
    # 'another_user',
    # 'moderator_nick',
]

def is_allowed_user():
    async def predicate(ctx):
        if ctx.author.name in ALLOWED_USERS:
            return True
        await ctx.send(f"❌ Цю команду можуть використовувати тільки дозволені користувачі!")
        return False
    return commands.check(predicate)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @is_allowed_user()
    async def kick(self, ctx, member: discord.Member, *, reason="Причину не вказано"):
        try:
            # Спроба відправити повідомлення в ЛС
            try:
                embed = discord.Embed(
                    title="❌ Вас було вигнано з серверу",
                    description=f"**Сервер:** {ctx.guild.name}\n**Причина:** {reason}",
                    color=discord.Color.red()
                )
                await member.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("⚠️ Не вдалося відправити повідомлення користувачу (можливо, в нього закриті ЛС)")
            except Exception as e:
                print(f"Помилка при відправці ЛС: {e}")
            
            # Кікаємо користувача
            await member.kick(reason=reason)
            await ctx.send(f'👢 Користувача {member.mention} було вигнано з серверу.\nПричина: {reason}')
        except discord.Forbidden:
            await ctx.send('❌ У мене немає прав для виконання цієї дії!')
        except discord.HTTPException:
            await ctx.send('❌ Виникла помилка при спробі вигнати користувача.')

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('❌ У вас немає прав для виконання цієї команди!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('❌ Вкажіть користувача якого потрібно вигнати!\nПриклад: !kick @користувач причина')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('❌ Користувача не знайдено!')

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @is_allowed_user()
    async def ban(self, ctx, member: typing.Union[discord.Member, str], *, reason=None):
        """Блокує користувача або всіх користувачів на сервері"""
        try:
            if isinstance(member, str) and member.lower() == 'all':
                # Масовий бан всіх користувачів
                banned_count = 0
                failed_count = 0
                
                # Створюємо embed для прогресу
                progress_embed = discord.Embed(
                    title="🔨 Масовий бан користувачів",
                    description="Процес розпочато...",
                    color=discord.Color.red()
                )
                progress_message = await ctx.send(embed=progress_embed)
                
                # Отримуємо всіх учасників серверу
                members = ctx.guild.members
                
                for target in members:
                    # Пропускаємо бота та користувача, який викликав команду
                    if target.bot or target == ctx.author:
                        continue
                        
                    try:
                        # Спроба відправити повідомлення в ЛС
                        try:
                            embed = discord.Embed(
                                title="❌ Вас було заблоковано на сервері",
                                description=f"**Сервер:** {ctx.guild.name}\n**Причина:** {reason if reason else 'Масовий бан'}",
                                color=discord.Color.red()
                            )
                            await target.send(embed=embed)
                        except:
                            pass  # Ігноруємо помилки відправки ЛС
                        
                        # Баним користувача
                        await target.ban(reason=f"Масовий бан | {reason if reason else 'Причину не вказано'}")
                        banned_count += 1
                        
                        # Оновлюємо прогрес кожні 5 банів
                        if banned_count % 5 == 0:
                            progress_embed.description = f"Заблоковано: {banned_count}\nПомилок: {failed_count}"
                            await progress_message.edit(embed=progress_embed)
                            
                    except discord.Forbidden:
                        failed_count += 1
                    except Exception as e:
                        failed_count += 1
                        print(f"Помилка при бані {target.name}: {str(e)}")
                
                # Фінальне повідомлення
                final_embed = discord.Embed(
                    title="🔨 Масовий бан завершено",
                    description=f"✅ Успішно заблоковано: {banned_count}\n❌ Помилок: {failed_count}",
                    color=discord.Color.green()
                )
                await progress_message.edit(embed=final_embed)
                
            else:
                # Звичайний бан одного користувача
                if not isinstance(member, discord.Member):
                    raise commands.MemberNotFound(member)
                    
                # Спроба відправити повідомлення в ЛС
                try:
                    embed = discord.Embed(
                        title="❌ Вас було заблоковано на сервері",
                        description=f"**Сервер:** {ctx.guild.name}\n**Причина:** {reason if reason else 'Причину не вказано'}",
                        color=discord.Color.red()
                    )
                    await member.send(embed=embed)
                except:
                    pass  # Ігноруємо помилки відправки ЛС
                
                await member.ban(reason=reason)
                await ctx.send(f'🔨 Користувача {member.mention} було заблоковано на сервері.\nПричина: {reason if reason else "Не вказано"}')
                
        except discord.Forbidden:
            await ctx.send('❌ У мене немає прав для виконання цієї дії!')
        except commands.MemberNotFound:
            await ctx.send('❌ Користувача не знайдено!')
        except Exception as e:
            await ctx.send(f'❌ Виникла помилка: {str(e)}')

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('❌ У вас немає прав для виконання цієї команди!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('❌ Вкажіть користувача або "all" для бану всіх!\nПриклад: !ban @користувач причина\nАбо: !ban all причина')

    @commands.command(name='clear')
    @commands.has_permissions(manage_channels=True)
    @is_allowed_user()
    async def clear(self, ctx, channel_type: str):
        """Видаляє всі канали вказаного типу"""
        if channel_type.lower() not in ['chat', 'voice-chat']:
            await ctx.send("❌ Вкажіть правильний тип каналів (chat або voice-chat)!")
            return

        deleted_count = 0
        
        try:
            # Отримуємо всі канали серверу
            if channel_type.lower() == 'chat':
                channels = [c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)]
                channel_type_name = "текстових каналів"
            else:  # voice-chat
                channels = [c for c in ctx.guild.channels if isinstance(c, discord.VoiceChannel)]
                channel_type_name = "голосових каналів"

            if not channels:
                await ctx.send(f"❌ На сервері немає {channel_type_name}!")
                return

            # Видаляємо канали
            for channel in channels:
                try:
                    await channel.delete()
                    deleted_count += 1
                except discord.Forbidden:
                    await ctx.send(f"❌ У мене немає прав для видалення каналу {channel.name}!")
                except Exception as e:
                    await ctx.send(f"❌ Помилка при видаленні каналу {channel.name}: {str(e)}")

            await ctx.send(f"🗑️ Видалено {deleted_count} {channel_type_name}")

        except discord.Forbidden:
            await ctx.send("❌ У мене немає прав для керування каналами!")
        except Exception as e:
            await ctx.send(f"❌ Виникла помилка: {str(e)}")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ У вас немає прав для керування каналами!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Вкажіть тип каналів!\nПриклад: !clear chat або !clear voice-chat")

    @commands.command(name='clean')
    @commands.has_permissions(manage_messages=True)
    @is_allowed_user()
    async def clean(self, ctx, amount: int = None):
        """Видаляє повідомлення в поточному каналі"""
        if amount is not None and amount <= 0:
            await ctx.send("❌ Кількість повідомлень має бути більше 0!")
            return

        try:
            # Видаляємо команду користувача
            await ctx.message.delete()
            
            # Якщо кількість не вказана, видаляємо всі повідомлення
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
                            await ctx.send("❌ У мене немає прав для видалення деяких повідомлень!")
                            break
            else:
                # Видаляємо вказану кількість повідомлень
                deleted = 0
                async with ctx.typing():
                    async for message in ctx.channel.history(limit=amount):
                        try:
                            await message.delete()
                            deleted += 1
                        except discord.NotFound:
                            continue
                        except discord.Forbidden:
                            await ctx.send("❌ У мене немає прав для видалення деяких повідомлень!")
                            break

            # Відправляємо повідомлення про результат
            result_message = await ctx.send(f"🗑️ Видалено {deleted} повідомлень")
            # Видаляємо повідомлення про результат через 5 секунд
            await result_message.delete(delay=5)

        except discord.Forbidden:
            await ctx.send("❌ У мене немає прав для видалення повідомлень!")
        except Exception as e:
            await ctx.send(f"❌ Виникла помилка: {str(e)}")

    @clean.error
    async def clean_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ У вас немає прав для видалення повідомлень!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Вкажіть правильне число повідомлень!\nПриклад: !clean 10")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
