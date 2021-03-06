import random
import typing as t
import discord
from urllib.parse import quote

from discord.ext import commands
from discord.utils import get
from discord_slash import SlashCommand, SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option

import io
import aiohttp

pfpurl = ["https://raw.githubusercontent.com/Jpw306/Logan-Alexa/master/sprites/angry.png",
        "https://raw.githubusercontent.com/Jpw306/Logan-Alexa/master/sprites/blush.png",
        "https://raw.githubusercontent.com/Jpw306/Logan-Alexa/master/sprites/happy.png",
        "https://raw.githubusercontent.com/Jpw306/Logan-Alexa/master/sprites/sad.png",
        "https://raw.githubusercontent.com/Jpw306/Logan-Alexa/master/sprites/suprise.png"]



def urlBuilder(msg, pfpNum):
    return "https://www.demirramon.com/gen/undertale_text_box.png?text=%s&box=undertale&boxcolor=ffffff&character=custom&url=%s" % (quote(msg), pfpurl[pfpNum])

class Misc(commands.Cog):
    @commands.command(name="qp", brief="Quick Poll designed for making decisions")
    async def qp(self, ctx, *, question):
        if "|" not in question:
            embed = discord.Embed(
                title=question,
                color=ctx.author.color,
            )
            embed.set_author(name=f"Quick Poll by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.message.delete()

            msg = await ctx.send(embed=embed)
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
        
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
            for i in range(options):
                await msg.add_reaction(emojiList[i])
                

    @commands.command(name="8ball", brief = "Test your fate with the power of a random function")
    async def eight_Ball(self, ctx, *, question):
        responses = ['Yes', 'No', 'Definitely Yes', 'Definitely No', 'Most of the time', 'It is certain', 'It is decidedly so', 'Without a doubt', 'As I see, yes', 'Most likely', 'Outlook good', 'Signs point to yes', 'Do not count on it', 'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful', 'When pigs fly']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

    # @commands.command(name="Clear", brief="Clears up to 5 messages. Clearly eligible for abuse")
    # async def clear(self, ctx, amount: t.Optional[int]):
    #     if amount is None:
    #         await ctx.channel.purge(limit = 6)        
    #     elif amount >= 11:
    #         await ctx.send("That is too powerful. Tone it down a bit")
    #     else:
    #         await ctx.channel.purge(limit = amount + 1)

    @commands.command(name="Jallah", brief="Want a clear yes or no answer? Ask the Quieréslam Queen") 
    async def jallah(self, ctx, *, question):
        responses = ['Alas, the answer you seek lies within you. It is a definite yes', 'Alas, the answer you seek lies within you. It is a definite no']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

    @commands.command(name="Github", brief="Link to the bot's source code")
    async def github(self, ctx):
        await ctx.send("https://github.com/Jpw306/Logan-Alexa")

    @commands.group()
    async def quote(self, ctx:SlashContext, *, msg):
        await ctx.message.delete()
        emote = 2
        if msg.startswith("angry"):
            msg = msg[6:]
            emote = 0
        elif msg.startswith("blush"):
            msg = msg[6:]
            emote = 1
        elif msg.startswith("sad"):
            msg = msg[4:]
            emote = 3     
        elif msg.startswith("surprise"):
            msg = msg[9:]
            emote = 4
        if ctx.invoked_subcommand is None:
            async with aiohttp.ClientSession() as session:
                async with session.get(urlBuilder(msg, emote)) as resp:
                    data = io.BytesIO(await resp.read())
                    await ctx.send(file=discord.File(data, 'underlexa_quote.png'))

    @commands.command()
    async def ship(self, ctx):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as session:
                async with session.get("https://raw.githubusercontent.com/Jpw306/Logan-Alexa/master/sprites/loganboard.png") as resp:
                    data = io.BytesIO(await resp.read())
                    await ctx.send(file=discord.File(data, 'underlexa_quote.png'))

    @commands.command()
    async def RPS(self, ctx, symbol):
        RPSchoices = ["Rock", "Paper", "Scissors"]

        embed = discord.Embed(
            title="Rock Paper Scissors Game",
            color=ctx.author.color,
        )

        symbol = symbol.lower()
        symbol = symbol.capitalize()

        if symbol in RPSchoices:
            result = "None"
            com = RPSchoices[random.randrange(0,3)]

            if com == symbol:
                result = "Tied"
            else:
                if com == "Rock":
                    if symbol == "Paper":
                        result = "Win"
                    else:
                        result = "Lose"
                elif com == "Paper":
                    if symbol == "Rock":
                        result = "Lose"
                    else:
                        result = "Win"
                else:
                    if symbol == "Rock":
                        result = "Win"
                    else:
                        result = "Lose"

            fields = [("Player Choice:", symbol, False),
                        ("Logan's Alexa's Choice:", com, False),
                        ("Outcome:", "You " + result + "!", False)]

            for name, value, inline in fields:
                embed.add_field(name = name, value=value, inline=inline)
            embed.set_footer(text=f"RPS Game invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            await ctx.message.delete()

            msg = await ctx.send(embed=embed)

        else:
            await ctx.send("Invalid choice")

    @commands.command()
    async def define(self, ctx, *, word):
        url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        querystring = {"term": word}

        with open("data/api.0", "r", encoding="utf-8") as f:
            KEY = f.read()

        headers = {
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
            'x-rapidapi-key': KEY
        }

        try:
            async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=querystring) as resp:
                        r = await resp.json()
                        embed = discord.Embed(title=f"First result for '{word}':")

                        definition = r["list"][0]["definition"]
                        example = r["list"][0]["example"]

                        fields = [("Definition", definition, False),
                                ("Example", example, False)]

                        embed.set_thumbnail(url="https://images.newrepublic.com/a0a10f8123e4aeb5617a37ffd2f7f1449d1b69e1.jpeg")

                        for name, value, inline in fields:
                            embed.add_field(name = name, value=value, inline=inline)
                        
                        await ctx.send(embed=embed)
        except:
            await ctx.send(f"Could not find definition for '{word}'")

def setup(bot):
    bot.add_cog(Misc(bot))