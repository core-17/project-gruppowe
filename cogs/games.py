import discord
from discord.ext import commands
import requests
from datetime import datetime, timezone

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sales')
    async def sales(self, ctx, page: int = 1):
        """Показує список ігор зі знижками в Steam"""
        try:
            headers = {
                'Accept-Language': 'en',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            # Get prices in EUR
            url = "https://store.steampowered.com/api/featuredcategories/?cc=fr&l=english"
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if 'specials' not in data:
                await ctx.send("❌ Не вдалося отримати інформацію про знижки!")
                return

            # Filter out DLC and get only base games
            def is_base_game(item):
                # Check if it's not a DLC based on name
                name = str(item['name']).lower()
                dlc_indicators = ['dlc', 'expansion', 'pack', 'bundle', 'season pass', 'addon', 'add-on']
                return not any(indicator in name for indicator in dlc_indicators)

            specials = [item for item in data['specials']['items'] if is_base_game(item)]
            
            # Sort by discount percentage (highest first)
            specials.sort(key=lambda x: x['discount_percent'], reverse=True)
            
            # Calculate pagination
            items_per_page = 15
            total_pages = (len(specials) + items_per_page - 1) // items_per_page
            
            if page < 1 or page > total_pages:
                await ctx.send(f"❌ Сторінка має бути між 1 та {total_pages}!")
                return
                
            # Create embed
            embed = discord.Embed(
                title="🎮 Знижки на ігри в Steam",
                description=f"Сторінка {page}/{total_pages} (без DLC та доповнень)",
                color=discord.Color.green()
            )
            
            # Add games to embed
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(specials))
            
            for item in specials[start_idx:end_idx]:
                name = item['name']
                discount = item['discount_percent']
                
                # Get prices in EUR
                price_eur = item['final_price'] / 100
                price_eur_original = item['original_price'] / 100
                
                value = (
                    f"💰 Ціна зі знижкою:\n"
                    f"€ ~~{price_eur_original:.2f}€~~ → **{price_eur:.2f}€**\n"
                    f"📉 Знижка: **{discount}%**\n"
                    f"🔗 [Сторінка в Steam](https://store.steampowered.com/app/{item['id']})"
                )
                
                embed.add_field(
                    name=f"{name} (-{discount}%)",
                    value=value,
                    inline=False
                )
            
            # Add navigation instructions
            embed.set_footer(text=f"Використовуйте !sales <номер_сторінки> для перегляду інших сторінок")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Помилка при отриманні знижок: {str(e)}")

    @commands.command(name='epic')
    async def epic(self, ctx):
        """Показує безкоштовні ігри в Epic Games Store"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            # Epic Games Store API URL
            url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
            params = {
                'locale': 'en-US',
                'country': 'UA',
                'allowCountries': 'UA'
            }
            
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if 'data' not in data or 'Catalog' not in data['data']:
                await ctx.send("❌ Не вдалося отримати інформацію про безкоштовні ігри!")
                return

            # Get current and upcoming free games
            current_games = []
            upcoming_games = []
            
            for game in data['data']['Catalog']['searchStore']['elements']:
                promotions = game.get('promotions')
                if not promotions:
                    continue
                    
                # Check current free games
                if promotions.get('promotionalOffers'):
                    for offer in promotions['promotionalOffers']:
                        for promo in offer.get('promotionalOffers', []):
                            if promo.get('discountSetting', {}).get('discountPercentage') == 0:
                                current_games.append({
                                    'game': game,
                                    'start_date': promo.get('startDate'),
                                    'end_date': promo.get('endDate')
                                })
                                break
                                
                # Check upcoming free games
                if promotions.get('upcomingPromotionalOffers'):
                    for offer in promotions['upcomingPromotionalOffers']:
                        for promo in offer.get('promotionalOffers', []):
                            if promo.get('discountSetting', {}).get('discountPercentage') == 0:
                                upcoming_games.append({
                                    'game': game,
                                    'start_date': promo.get('startDate'),
                                    'end_date': promo.get('endDate')
                                })
                                break

            # Create embed
            embed = discord.Embed(
                title="🎮 Безкоштовні ігри в Epic Games Store",
                color=discord.Color.blue()
            )

            def parse_date(date_str):
                if not date_str:
                    return None
                try:
                    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                except ValueError:
                    try:
                        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    except ValueError:
                        return None

            # Add current free games
            if current_games:
                embed.add_field(
                    name="🎯 Зараз безкоштовно:",
                    value="Поточні безкоштовні ігри:",
                    inline=False
                )
                
                for item in current_games:
                    game = item['game']
                    name = game['title']
                    description = game.get('description', 'Опис відсутній')
                    if len(description) > 200:
                        description = description[:200] + "..."
                    
                    end_date = parse_date(item['end_date'])
                    end_date_str = f"\n⏰ Безкоштовно до: **{end_date.strftime('%d.%m.%Y %H:%M')} UTC**" if end_date else ""
                    
                    value = (
                        f"{description}\n"
                        f"🔗 [Сторінка в Epic Games Store](https://store.epicgames.com/en-US/p/{game['urlSlug']})"
                        f"{end_date_str}"
                    )
                    
                    embed.add_field(
                        name=f"{name}",
                        value=value,
                        inline=False
                    )

            # Add upcoming free games
            if upcoming_games:
                embed.add_field(
                    name="🔜 Скоро будуть безкоштовні:",
                    value="Майбутні безкоштовні ігри:",
                    inline=False
                )
                
                for item in upcoming_games:
                    game = item['game']
                    name = game['title']
                    
                    start_date = parse_date(item['start_date'])
                    end_date = parse_date(item['end_date'])
                    
                    date_range = ""
                    if start_date and end_date:
                        date_range = (f"\n⏰ Буде безкоштовно з "
                                    f"**{start_date.strftime('%d.%m.%Y %H:%M')}** до "
                                    f"**{end_date.strftime('%d.%m.%Y %H:%M')} UTC**")
                    
                    value = (
                        f"🔗 [Сторінка в Epic Games Store](https://store.epicgames.com/en-US/p/{game['urlSlug']})"
                        f"{date_range}"
                    )
                    
                    embed.add_field(
                        name=f"{name}",
                        value=value,
                        inline=False
                    )

            if not current_games and not upcoming_games:
                await ctx.send("🎮 Наразі немає безкоштовних ігор в Epic Games Store")
                return

            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Помилка при отриманні безкоштовних ігор: {str(e)}")

async def setup(bot):
    await bot.add_cog(Games(bot))
