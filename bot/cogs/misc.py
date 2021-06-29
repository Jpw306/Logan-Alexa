import random
import typing as t

from discord.ext import commands
from discord.utils import get

class Misc(commands.Cog):
    @commands.command(name="8ball")
    async def eight_Ball(self, ctx, *, question):
        responses = ['Yes', 'No', 'Definitely Yes', 'Definitely No', 'Most of the time', 'It is certain', 'It is decidedly so', 'Without a doubt', 'As I see, yes', 'Most likely', 'Outlook good', 'Signs point to yes', 'Do not count on it', 'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful', 'When pigs fly']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

    @commands.command()
    async def clear(self, ctx, amount: t.Optional[int]):
        if amount is None:
            await ctx.channel.purge(limit = 6)        
        elif amount >= 11:
            await ctx.send("That is too powerful. Tone it down a bit")
        else:
            await ctx.channel.purge(limit = amount + 1)

    @commands.command()
    async def jallah(self, ctx, *, question):
        responses = ['Alas, the answer you seek lies within you. It is a definite yes', 'Alas, the answer you seek lies within you. It is a definite no']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

    @commands.command()
    async def github(self, ctx):
        await ctx.send("https://github.com/Jpw306/Logan-Alexa")

def setup(bot):
    bot.add_cog(Misc(bot))