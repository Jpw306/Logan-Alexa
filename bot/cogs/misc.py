import random
import typing as t
import discord
import datetime as dt

from discord.ext import commands
from discord.utils import get

class Misc(commands.Cog):
    @commands.command(name="qp", descriptoin="Quick Poll designed for making decisions")
    async def qp(self, ctx, *, question):
        if "|" not in question:
            embed = discord.Embed(
                title=question,
                color=ctx.author.color,
            )
            embed.set_author(name=f"Quick Poll by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.message.delete()

            msg = await ctx.send(embed=embed)
            await msg.add_reaction(":check:860981980661284864")
            await msg.add_reaction(":xmark:860981945529008169")
        
        else:
            emojiList = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            options = question.count("|") + 1
            embed = discord.Embed(
                title=question,
                color=ctx.author.color,
            )
            embed.set_author(name=f"Quick Poll by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.message.delete()

            msg = await ctx.send(embed=embed)
            count = 0
            for i in range(options):
                await msg.add_reaction(emojiList[i])
                

    @commands.command(name="8ball", description = "Test your fate with the power of a random function")
    async def eight_Ball(self, ctx, *, question):
        responses = ['Yes', 'No', 'Definitely Yes', 'Definitely No', 'Most of the time', 'It is certain', 'It is decidedly so', 'Without a doubt', 'As I see, yes', 'Most likely', 'Outlook good', 'Signs point to yes', 'Do not count on it', 'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful', 'When pigs fly']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

    @commands.command(name="Clear", description="Clears up to 5 messages. Clearly eligible for abuse")
    async def clear(self, ctx, amount: t.Optional[int]):
        if amount is None:
            await ctx.channel.purge(limit = 6)        
        elif amount >= 11:
            await ctx.send("That is too powerful. Tone it down a bit")
        else:
            await ctx.channel.purge(limit = amount + 1)

    @commands.command(name="Jallah", description="Want a clear yes or no answer? Ask the Quieréslam Queen") 
    async def jallah(self, ctx, *, question):
        responses = ['Alas, the answer you seek lies within you. It is a definite yes', 'Alas, the answer you seek lies within you. It is a definite no']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

    @commands.command(name="Github", description="Link to the bot's source code")
    async def github(self, ctx):
        await ctx.send("https://github.com/Jpw306/Logan-Alexa")

def setup(bot):
    bot.add_cog(Misc(bot))