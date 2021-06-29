import discord
import sqlite3

from discord.ext import commands
from discord.utils import get

sql = sqlite3.connect("/home/jpw306/Desktop/Bot/data/Logan.db")
db = sql.cursor()

class Stats(commands.Cog):
    @commands.command()
    async def msg(self, ctx, user: discord.Member = None):
        if user:
            author = user
        else:
            author = ctx.message.author
        db.execute("SELECT msg FROM discord WHERE id=?", (str(author),))
        rows = db.fetchone()
        msg = rows[0]
        await ctx.send(f'{author.mention} has sent {msg} messages!')
    
    @commands.command()
    async def uv(self, ctx, user: discord.Member = None):
        if user:
            author = user
        else:
            author = ctx.message.author
        db.execute("SELECT uv FROM discord WHERE id=?", (str(author),))
        rows = db.fetchone()
        uv = rows[0]
        await ctx.send(f'{author.mention} has {uv} upvotes!')

    @commands.command()   
    async def dv(self, ctx, user: discord.Member = None):
        if user:
            author = user
        else:
            author = ctx.message.author
        db.execute("SELECT dv FROM discord WHERE id=?", (str(author),))
        rows = db.fetchone()
        dv = rows[0]
        await ctx.send(f'{author.mention} has {dv} downvotes!')

    @commands.command()    
    async def v(self, ctx, user: discord.Member = None):
        if user:
            author = user
        else:
            author = ctx.message.author   
        db.execute("SELECT uv FROM discord WHERE id=?", (str(author),))
        rows = db.fetchone()
        uv = rows[0]
        db.execute("SELECT dv FROM discord WHERE id=?", (str(author),))
        rows = db.fetchone()
        dv = rows[0]
        sum = uv + dv
        try:
            pop = round((uv/sum) * 100, 2)
        except:
            pop = 100
        if str(author) == "Jpw306#2584":
            await ctx.send(f'{author.mention} has {uv} upvotes and ~~{dv}~~ 0 downvotes for a total of ~~{pop}%~~ 100% popularity')   
        else:
            await ctx.send(f'{author.mention} has {uv} upvotes and {dv} downvotes for a total of {pop}% popularity')    

def setup(bot):
    bot.add_cog(Stats(bot))