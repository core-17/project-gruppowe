import discord
from discord.ext import commands
import json
import os
from collections import defaultdict

# Шлях до файлу зі статистикою
STATS_FILE = 'tip_stats.json'

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tip_stats = self.load_stats()

    def load_stats(self):
        """Завантаження статистики з файлу"""
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return defaultdict(int, json.load(f))
        return defaultdict(int)

    def save_stats(self):
        """Збереження статистики у файл"""
        with open(STATS_FILE, 'w') as f:
            json.dump(dict(self.tip_stats), f)

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
        # Збільшуємо лічильник тіпів для користувача
        self.tip_stats[str(member.id)] += 1
        self.save_stats()
        await ctx.send(f'☠️ {ctx.author.mention} тіпнув генія на {member.mention} за {reason} ☠️')

    @tip.error
    async def tip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('❌ Вкажіть користувача!\nПриклад: !tip @користувач причина')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('❌ Користувача не знайдено!')

    @commands.command(name='top')
    async def top(self, ctx):
        """Показує топ тіпнутих користувачів"""
        if not self.tip_stats:
            await ctx.send("❌ Поки що нікого не тіпнули!")
            return
        
        # Сортуємо користувачів за кількістю тіпів
        sorted_stats = sorted(self.tip_stats.items(), key=lambda x: int(x[1]), reverse=True)
        
        # Створюємо повідомлення з топом
        message = "🏆 Топ тіпнутих геніїв:\n\n"
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
            await ctx.send("❌ Не знайдено жодного активного користувача в топі!")
        else:
            await ctx.send(message)

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
