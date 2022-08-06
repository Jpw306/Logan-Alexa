import asyncio
import datetime as dt
import re
import random
import typing as t
from enum import Enum
from urllib.parse import parse_qsl
import math

import discord
import wavelink
from discord.ext import commands
from wavelink.ext import spotify

URL_REG = re.compile(r'https?://(?:www\.)?.+')
SPOTIFY_URL_REG = re.compile(r'https?://open.spotify.com/(?P<type>album|playlist|track)/(?P<id>[a-zA-Z0-9]+)')
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        with open("data/secret.0", "r", encoding="utf-8") as f:
            SECRET = f.read()

        await wavelink.NodePool.create_node(bot=self.bot,
                                                host="127.0.0.1",
                                                port=2333,
                                                password="youshallnotpass",
                                                spotify_client=spotify.SpotifyClient(client_id="6223df78940940e1b50f4a671bc48128", client_secret=SECRET))

    async def add_track(self, ctx, vc, track, playlist = False):
        if not track:
            await ctx.send("Could not find track(s)")

        if playlist:
            for item in track.tracks:
                vc.queue.put(item)
        else:
            vc.queue.put(track)

    async def advance(self, vc, skip = False):
        print("advance")
        if skip:
            await vc.seek(vc.track.duration * 1000)
        else:
            if len(vc.queue) > 0:
                await vc.play(vc.queue.get(), replace = True)
            else:
                print("queue is empty")

    async def choose_track(self, ctx, tracks):
        def _check(reaction, user):
            return reaction.emoji in OPTIONS.keys() and user == ctx.author and reaction.message.id == msg.id
            
        embed = discord.Embed(
            title = "Choose a song",
            description=(
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            color = ctx.author.color,
            timestamp = dt.datetime.utcnow()
        )
        embed.set_author(name="Query results")
        embed.set_footer(text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check = _check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]

    async def queue_tracks(self, ctx, vc, query):
        if SPOTIFY_URL_REG.match(query):
            info = spotify.decode_url(query)
            if info['type'] is spotify.SpotifySearchType.playlist or info['type'] is spotify.SpotifySearchType.album:
                async for track in spotify.SpotifyTrack.iterator(query=info['id'], type=info['type'], partial_tracks=True):
                    await self.add_track(ctx, vc, track)
            else:
                search = await spotify.SpotifyTrack.search(query=info['id'], return_first=True)
                await self.add_track(ctx, vc, search)

        elif URL_REG.match(query):
            if "playlist" in query:
                search = await wavelink.YouTubePlaylist.search(query=query)
                await self.add_track(ctx, vc, search, True)
            else:
                search = await wavelink.YouTubeTrack.search(query=query, return_first=True)
                await self.add_track(ctx, vc, search)

        else:
            await self.add_track(ctx, vc, await self.choose_track(ctx, await wavelink.YouTubeTrack.search(query)))

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node {node.identifier} is ready!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await member.guild.voice_client.disconnect()

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, vc, track, reason):
        await self.advance(vc)
        print("end")

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, vc, track, error):
        await self.advance(vc)
        print("exception")

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, vc, track, threshold):
        await self.advance(vc)
        print("stuck")

    @commands.command()
    async def dropin(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        try:
            channel = channel or ctx.author.voice.channel
        except AttributeError:
            return await ctx.send('No voice channel to connect to. Please either provide one or join one.')

        vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
        vc.queue.clear()
        return vc

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            vc = await ctx.invoke(self.dropin)

        await self.queue_tracks(ctx, vc, query)

        if not vc.is_playing():
            await vc.play(vc.queue.get())
            await ctx.send("Now playing (hopefully)")

    @commands.command()
    async def volume(self, ctx, *, volume: int):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            await ctx.send("Bot is not currently in a voice channel")

        await vc.set_volume(volume)
        await ctx.send(f"Volume set to {volume}")

    @commands.command()
    async def skip(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            await ctx.send("Bot is not currently in a voice channel")

        await self.advance(vc, True)
        await ctx.send("Song skipped")

    @commands.command()
    async def clear(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            await ctx.send("Bot is not currently in a voice channel")

        vc.queue.clear()
        await ctx.send("Queue cleared")

    @commands.command()
    async def queue(self, ctx, show: int = 10):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            await ctx.send("Bot is not currently in a voice channel")

        embed = discord.Embed(
            title="Queue",
            description=f"Showing up to next {show} tracks",
            color=ctx.author.color,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Currently playing", value=getattr(vc.track, "title", "No tracks currently playing."), inline = False)

        if not vc.queue.is_empty:
            embed.add_field(
                name="Next up",
                value="\n".join(vc.queue[track].title for track in range(len(vc.queue) if len(vc.queue) < 10 else 10)),
                inline=False
            )
            embed.add_field(
                name="Songs in queue",
                value=len(vc.queue),
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def shuffle(self, ctx, *, query: str):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            vc = await ctx.invoke(self.dropin)

        await self.queue_tracks(ctx, vc, query)

        upcoming = []
        length = len(vc.queue)
        for i in range(length):
            upcoming.append(vc.queue[i])

        random.shuffle(upcoming)
        vc.queue.clear()

        for i in range(length):
            vc.queue.put(upcoming[i])

        await ctx.send("Queue shuffled")

        if not vc.is_playing():
            await vc.play(vc.queue.get())
            await ctx.send("Now playing (hopefully)")

    @commands.command()
    async def current(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            await ctx.send("Bot is not currently in a voice channel")
        
        if vc.is_playing():

            if str(vc.track.author).lower() not in str(vc.track.title).lower():
                description = vc.track.title + " - " + vc.track.author
            else:
                description = vc.track.title

            embed = discord.Embed(
                title="Current Track",
                description=description,
                color=ctx.author.color,
                timestamp=dt.datetime.utcnow()
            )

            duration = math.floor(vc.track.duration)
            current = math.floor(vc.position)
            percent = ((current/duration) * 100) / 5
            time = ""
            for i in range(math.floor(percent)):
                time += "▅"
            for i in range(20 - math.floor(percent)):
                time += "▁"

            duration = str(math.floor(duration/60)) + ":" + f"{(duration % 60):02d}"
            current = str(math.floor(current/60)) + ":" + f"{(current % 60):02d}"
            
            embed.add_field(
                name="Duration",
                value=time + f" [{current}/{duration}]",
                inline=False
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("No track currently playing")

def setup(bot):
    bot.add_cog(Music(bot))