import discord
from discord.ext import commands
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import SessionLocal, UserStats

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_db(self):
        """Отримати сесію бази даних"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @commands.command(name='hello')
    async def hello(self, ctx):
        """Привітання з ботом"""
        await ctx.send(f'Привіт, {ctx.author.name}! 👋')

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Перевірка затримки бота"""
        await ctx.send(f'Ping! Затримка: {round(self.bot.latency * 1000)}ms')

    @commands.command(name='tip')
    async def tip(self, ctx, member: discord.Member, *, reason="perfect moment"):
        """Тіпнути користувача"""
        try:
            db: Session = next(self.get_db())

            # Оновлення або вставка для користувача, якого тіпнули
            db.execute(text("""
                INSERT INTO user_stats (user_id, tips_given, tips_received)
                VALUES (:user_id, 0, 1)
                ON CONFLICT(user_id) DO UPDATE SET tips_received = tips_received + 1
            """), {"user_id": str(member.id)})

            # Оновлення або вставка для автора команди
            db.execute(text("""
                INSERT INTO user_stats (user_id, tips_given, tips_received)
                VALUES (:user_id, 1, 0)
                ON CONFLICT(user_id) DO UPDATE SET tips_given = tips_given + 1
            """), {"user_id": str(ctx.author.id)})

            db.commit()
            await ctx.send(f'☠️ {ctx.author.mention} тіпнув генія на {member.mention} за {reason} ☠️')
        except Exception as e:
            db.rollback()
            await ctx.send(f"❌ Сталася помилка: {str(e)}")
        finally:
            db.close()

    @tip.error
    async def tip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('❌ Вкажіть користувача!\nПриклад: !tip @користувач причина')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('❌ Користувача не знайдено!')

    @commands.command(name='top')
    async def top(self, ctx):
        """Показує топ тіпнутих користувачів"""
        db: Session = next(self.get_db())
        try:
            # Отримуємо користувачів, відсортованих за кількістю отриманих "тіпів" у порядку спадання
            users = db.query(UserStats).order_by(UserStats.tips_received.desc()).limit(10).all()

            if not users:
                await ctx.send("❌ Поки що нікого не тіпнули!")
                return

            # Створюємо повідомлення з топом
            message = "🏆 Топ тіпнутих геніїв:\n\n"
            for i, user in enumerate(users, 1):
                try:
                    member = await ctx.guild.fetch_member(int(user.user_id))
                    message += f"{i}. {member.mention} - {user.tips_received} тіпів\n"
                except discord.NotFound:
                    # Якщо користувача немає на сервері, виводимо його ID
                    message += f"{i}. <@{user.user_id}> - {user.tips_received} тіпів\n"

            await ctx.send(message)
        except Exception as e:
            await ctx.send(f"❌ Сталася помилка: {str(e)}")
        finally:
            db.close()

    @commands.command(name='list')
    async def list_commands(self, ctx):
        """Показує список всіх доступних команд"""
        embed = discord.Embed(
            title="📋 Список команд бота",
            description="Ось список всіх доступних команд:",
            color=discord.Color.blue()
        )

        commands_list = {
            "🎵 Музика": {
                "!music <посилання>": "Додати музику з YouTube в чергу",
                "!skip": "Пропустити поточний трек",
                "!stop": "Зупинити відтворення і очистити чергу",
                "!queue (!q)": "Показати поточну чергу музики"
            },
            "🎮 Ігри": {
                "!sales": "Показати знижки в Steam",
                "!epic": "Показати безкоштовні ігри в Epic Games Store"
            },
            "👥 Модерація": {
                "!kick @користувач": "Вигнати користувача з серверу",
                "!ban @користувач": "Заблокувати користувача на сервері",
                "!clear <тип каналів>": "Видалити всі канали вказаного типу",
                "!clean [кількість]": "Видалити повідомлення в поточному каналі"
            },
            "ℹ️ Інше": {
                "!hello": "Привітатися з ботом",
                "!list": "Показати цей список команд",
                "!tip @користувач": "Тіпнути користувача",
                "!top": "Показати топ тіпнутих користувачів"
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

        embed.set_footer(text="Використовуйте команди з префіксом !")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))
