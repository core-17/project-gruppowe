import discord
from discord.ext import commands
import requests
from datetime import datetime, timezone

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sales')
    async def sales(self, ctx, page: int = 1):
        """Shows a list of discounted games on Steam"""
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
                await ctx.send("❌ Failed to retrieve discount information!")
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
                await ctx.send(f"❌ Page must be between 1 and {total_pages}!")
                return
                
            # Create embed
            embed = discord.Embed(
                title="🎮 Steam Game Discounts",
                description=f"Page {page}/{total_pages} (excluding DLC and expansions)",
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
                    f"💰 Discounted Price:\n"
                    f"~~{price_eur_original:.2f}€~~ → **{price_eur:.2f}€**\n"
                    f"📉 Discount: **{discount}%**\n"
                    f"🔗 [Steam Page](https://store.steampowered.com/app/{item['id']})"
                )
                
                embed.add_field(
                    name=f"{name} (-{discount}%)",
                    value=value,
                    inline=False
                )
            
            # Add navigation instructions
            embed.set_footer(text=f"Use !sales <page_number> to view other pages")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error retrieving discounts: {str(e)}")

    @commands.command(name='epic')
    async def epic(self, ctx):
        """Shows free games on Epic Games Store"""
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
                await ctx.send("❌ Failed to retrieve free games information!")
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
                title="🎮 Free Games on Epic Games Store",
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
                    name="🎯 Currently Free:",
                    value="Current free games:",
                    inline=False
                )
                
                for item in current_games:
                    game = item['game']
                    name = game['title']
                    description = game.get('description', 'No description available')
                    if len(description) > 200:
                        description = description[:200] + "..."
                    
                    end_date = parse_date(item['end_date'])
                    end_date_str = f"\n⏰ Free until: **{end_date.strftime('%d.%m.%Y %H:%M')} UTC**" if end_date else ""
                    
                    value = (
                        f"{description}\n"
                        f"🔗 [Epic Games Store Page](https://store.epicgames.com/en-US/p/{game['urlSlug']})"
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
                    name="🔜 Coming Soon:",
                    value="Upcoming free games:",
                    inline=False
                )
                
                for item in upcoming_games:
                    game = item['game']
                    name = game['title']
                    
                    start_date = parse_date(item['start_date'])
                    end_date = parse_date(item['end_date'])
                    
                    date_range = ""
                    if start_date and end_date:
                        date_range = (f"\n⏰ Free from "
                                    f"**{start_date.strftime('%d.%m.%Y %H:%M')}** to "
                                    f"**{end_date.strftime('%d.%m.%Y %H:%M')} UTC**")
                    
                    value = (
                        f"🔗 [Epic Games Store Page](https://store.epicgames.com/en-US/p/{game['urlSlug']})"
                        f"{date_range}"
                    )
                    
                    embed.add_field(
                        name=f"{name}",
                        value=value,
                        inline=False
                    )

            if not current_games and not upcoming_games:
                await ctx.send("🎮 There are currently no free games on Epic Games Store")
                return

            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error retrieving free games: {str(e)}")

async def setup(bot):
    await bot.add_cog(Games(bot))
