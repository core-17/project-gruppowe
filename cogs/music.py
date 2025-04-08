import discord
from discord.ext import commands
import yt_dlp
import asyncio
from async_timeout import timeout

# YouTube DL options
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extract_flat': True,
    'force_generic_extractor': True,
    'concurrent_fragment_downloads': 1,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate'
    }
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class MusicPlayer:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog

        self.queue = []
        self.next = asyncio.Event()
        
        self.current = None
        self.volume = 0.5
        
        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            if not self.queue:
                try:
                    async with timeout(180):  # 3 minute timeout
                        await self.next.wait()
                except asyncio.TimeoutError:
                    return self.destroy(self.guild)

            if len(self.queue) > 0:
                current = self.queue.pop(0)
                
                try:
                    self.current = current
                    self.guild.voice_client.play(current['source'], after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
                    await self.channel.send(f'🎵 Now playing: **{current["title"]}**')
                    await self.next.wait()
                except Exception as e:
                    await self.channel.send(f'Playback error: {str(e)}')

    def destroy(self, guild):
        return self.bot.loop.create_task(self.cog.cleanup(guild))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player

    async def create_source(self, search: str, loop):
        try:
            # Try to extract info using yt-dlp
            ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
            
            # First try direct URL
            try:
                # If it's not a URL, prepend ytsearch:
                if not search.startswith('http'):
                    search = f"ytsearch:{search}"
                
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
                
                if data is None:
                    raise Exception("Video not found")
                
                # Handle both direct videos and search results
                if 'entries' in data:
                    data = data['entries'][0]
                
                # Get the stream URL
                stream_url = data.get('url')
                if not stream_url:
                    formats = data.get('formats', [])
                    # Find the best audio format
                    for f in formats:
                        if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                            stream_url = f['url']
                            break
                    
                    if not stream_url and formats:
                        # If no audio-only format found, use the first available format
                        stream_url = formats[0]['url']
                
                if not stream_url:
                    raise Exception("Failed to retrieve stream URL")
                
                return discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS), data
                
            except Exception as e:
                raise Exception(f"Error retrieving video: {str(e)}")
                
        except Exception as e:
            raise Exception(f"Error retrieving audio: {str(e)}")

    @commands.command(name='music')
    async def music(self, ctx, *, url):
        """Plays music from a YouTube link"""
        if not ctx.message.author.voice:
            return await ctx.send("You must be in a voice channel!")

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            return await ctx.send("The bot is already being used in another channel!")

        async with ctx.typing():
            try:
                source, data = await self.create_source(url, self.bot.loop)
                player = self.get_player(ctx)
                
                # Create a dictionary with both source and metadata
                track = {
                    'source': source,
                    'title': data['title']
                }
                
                player.queue.append(track)
                
                if not ctx.voice_client.is_playing():
                    player.next.set()
                
                await ctx.send(f'🎵 Added to queue: **{data["title"]}**')
            except Exception as e:
                await ctx.send(f'Error: {str(e)}')

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        """Shows the current music queue"""
        player = self.players.get(ctx.guild.id)
        
        if not player or not player.queue:
            return await ctx.send("🎵 The queue is empty!")
        
        # Create embed for queue
        embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.blue())
        
        # Add currently playing song
        if player.current:
            if isinstance(player.current, dict):
                current_title = player.current.get('title', 'Unknown title')
            else:
                current_title = "Now playing"
            embed.add_field(name="▶️ Now playing:", value=current_title, inline=False)
        
        # Add queued songs
        queue_text = ""
        for i, track in enumerate(player.queue, 1):
            if isinstance(track, dict):
                title = track.get('title', 'Unknown title')
            else:
                title = f"Track {i}"
            queue_text += f"{i}. {title}\n"
            
            # Split into multiple fields if queue is too long
            if i % 10 == 0 or i == len(player.queue):
                embed.add_field(name=f"📝 In queue:", value=queue_text or "The queue is empty", inline=False)
                queue_text = ""
        
        await ctx.send(embed=embed)

    @commands.command(name='stop')
    async def stop(self, ctx):
        """Stops music playback"""
        if ctx.voice_client:
            await self.cleanup(ctx.guild)
            await ctx.send("⏹️ Music stopped")

    @commands.command(name='skip')
    async def skip(self, ctx):
        """Skips the current track"""
        if ctx.voice_client is None:
            return await ctx.send("I'm not playing music right now!")

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped the current track")
        else:
            await ctx.send("Nothing is playing right now!")

async def setup(bot):
    await bot.add_cog(Music(bot))
