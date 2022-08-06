import discord
import sqlite3

from discord.ext import commands
from discord.utils import get

sql = sqlite3.connect("/home/pi/Desktop/Bot/data/Logan.db")
db = sql.cursor()

class Stats(commands.Cog):
    @commands.command(brief = "See how many messages you have sent")
    async def msg(self, ctx, user: discord.Member = None):
        if user:
            author = user
        else:
            author = ctx.message.author
        db.execute("SELECT msg FROM member WHERE id=?", (int(author.id),))
        rows = db.fetchone()
        msg = rows[0]
        await ctx.send(f'{author.mention} has sent {msg} messages!')
    
    @commands.command(brief = "See how popular you are")
    async def uv(self, ctx, user: discord.Member = None):
        if user:
            author = user
        else:
            author = ctx.message.author
        db.execute("SELECT uv FROM member WHERE id=?", (int(author.id),))
        rows = db.fetchone()
        uv = rows[0]
        await ctx.send(f'{author.mention} has {uv} upvotes!')

    @commands.command(brief = "See what shame you have brought to your friends and family")   
    async def dv(self, ctx, user: discord.Member = None):
        if user:
            author = user
        else:
            author = ctx.message.author
        db.execute("SELECT dv FROM member WHERE id=?", (int(author.id),))
        rows = db.fetchone()
        dv = rows[0]
        await ctx.send(f'{author.mention} has {dv} downvotes!')

    @commands.command(brief = "See how average you are")    
    async def v(self, ctx, user: discord.Member = None):
        if user:
            author = user
        else:
            author = ctx.message.author   
        db.execute("SELECT uv FROM member WHERE id=?", (int(author.id),))
        rows = db.fetchone()
        uv = rows[0]
        db.execute("SELECT dv FROM member WHERE id=?", (int(author.id),))
        rows = db.fetchone()
        dv = rows[0]
        sum = uv + dv
        try:
            pop = round((uv/sum) * 100, 2)
        except:
            pop = 100
        await ctx.send(f'{author.mention} has {uv} upvotes and {dv} downvotes for a total of {pop}% popularity')    

    @commands.command()
    async def setHOS(self, ctx):
        channel = int(str(ctx.message.channel.id))
        server = int(str(ctx.message.guild.id))
        db.execute("SELECT HOS FROM server WHERE id=?", (server,))
        rows = db.fetchone()
        try:
            id = rows[0]
        except:
            id = None
        if id is not None:
            db.execute("UPDATE server SET HOS=? WHERE id=?", (channel, server,))
        else:
            db.execute("INSERT INTO server (id, HOS) VALUES (?,?)", (server, channel,))
        sql.commit()
        await ctx.send("Setup complete! Welcome to the HOS")

def setup(bot):
    bot.add_cog(Stats(bot))