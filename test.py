import unittest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
import discord
from discord.ext import commands
from cogs.list import List
from cogs.utils import Utils

class TestDiscordBot(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Створюємо інтенти для бота
        intents = discord.Intents.default()
        intents.message_content = True  # Дозволяє читати вміст повідомлень
        
        # Створюємо тестовий бот з інтентами
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.list_cog = List(self.bot)
        self.utils_cog = Utils(self.bot)
        await self.bot.add_cog(self.list_cog)
        await self.bot.add_cog(self.utils_cog)

    async def test_hello_command(self):
        # Мокаємо контекст команди
        ctx = MagicMock()
        ctx.author.name = "TestUser"
        ctx.send = AsyncMock()

        # Викликаємо команду
        await self.list_cog.hello(ctx)

        # Перевіряємо, чи було викликано ctx.send з правильним повідомленням
        ctx.send.assert_called_once_with("Hello, TestUser! 👋")

    async def test_ping_command(self):
        # Мокаємо контекст команди
        ctx = MagicMock()
        ctx.send = AsyncMock()
        
        # Використовуємо PropertyMock для заміни latency
        with patch('discord.ext.commands.Bot.latency', new_callable=PropertyMock) as mock_latency:
            mock_latency.return_value = 0.123  # Мокаємо затримку бота

            # Викликаємо команду
            await self.list_cog.ping(ctx)

            # Перевіряємо, чи було викликано ctx.send з правильним повідомленням
            ctx.send.assert_called_once_with("Ping! Latency: 123ms")

    async def test_tip_command(self):
        # Мокуємо метод get_db
        with patch.object(self.utils_cog, 'get_db') as mock_get_db:
            # Мокаємо контекст команди
            ctx = MagicMock()
            ctx.author.mention = "@TestUser"
            ctx.author.id = 12345
            ctx.send = AsyncMock()
            member = MagicMock()
            member.mention = "@AnotherUser"
            member.id = 67890

            # Мокуємо сесію бази даних
            mock_session = MagicMock()
            mock_get_db.return_value.__enter__.return_value = mock_session
            mock_get_db.return_value.__iter__.return_value = [mock_session]

            # Викликаємо команду
            await self.utils_cog.tip(ctx, member, reason="helpful advice")

            # Перевіряємо, чи було викликано ctx.send з правильним повідомленням
            ctx.send.assert_called_once_with("☠️ @TestUser tipped @AnotherUser for helpful advice ☠️")

    async def test_list_command(self):
        # Мокаємо контекст команди
        ctx = MagicMock()
        ctx.send = AsyncMock()

        # Викликаємо команду
        await self.list_cog.list_commands(ctx)

        # Перевіряємо, чи було викликано ctx.send
        ctx.send.assert_called_once()
        
        # Перевіряємо, чи повідомлення є Embed
        embed = ctx.send.call_args[1]["embed"]
        self.assertEqual(embed.title, "📋 Bot Command List")
        self.assertIn("🎵 Music", [field.name for field in embed.fields])

if __name__ == "__main__":
    unittest.main()
