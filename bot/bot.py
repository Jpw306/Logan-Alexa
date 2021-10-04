from pathlib import Path
from datetime import datetime

import discord
import sqlite3
import re

from discord.ext import commands
from discord import Embed
from discord.utils import get

intents = discord.Intents.default()
intents.members = True

sql = sqlite3.connect("/home/jpw306/Desktop/Bot/data/Logan.db")
db = sql.cursor()

async def update_data(user):        
    db.execute("SELECT id FROM discord")
    rows = db.fetchall()
    found = False
    for row in rows:
        if row[0] == user:
            found = True
    if found == False:
        print("User not found")
        db.execute(f"INSERT INTO discord (id, msg) VALUES(?, ?)", (user, 0,))
        sql.commit()
    
async def add_messages(user):
    db.execute(f"SELECT msg FROM discord WHERE id = ?", (user,))
    rows = db.fetchone()
    msg = rows[0]
    msg += 1
    db.execute(f"UPDATE discord SET msg=? WHERE id= ?", (msg, user,))
    sql.commit() 

class Bot(commands.Bot):
    def __init__(self):
        self._cogs = [p.stem for p in Path(".").glob("./bot/cogs/*.py")]
        super().__init__(command_prefix=self.prefix, case_insensitive=True, intents=discord.Intents.all())

    def setup(self):
        print("Running setup...")

        for cog in self._cogs:
            self.load_extension(f"bot.cogs.{cog}")

        self.help_command = commands.DefaultHelpCommand(no_category = 'Other Commands')

        print("Setup complete.")

    def run(self):
        self.setup()

        with open("data/token.0", "r", encoding="utf-8") as f:
            TOKEN = f.read()

        print("Running bot...")
        super().run(TOKEN, reconnect=True)

    async def shutdown(self):
        print("Closing connection to Discord...")
        await super().close()

    async def close(self):
        print("Closing on keyboard interrupt...")
        await self.shutdown()

    async def on_connect(self):
        print(f"Connected to Discord (latency: {self.latency*1000:,.0f} ms).")

    async def on_resume(self):
        print("Bot resumed.")

    async def on_disconnect(self):
        print("Bot disconnected.")

    async def on_raw_reaction_add(self, payload):
        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.emoji.name == "upvote":
            db.execute("SELECT uv FROM discord WHERE id = ?", (str(message.author),))
            rows = db.fetchone()
            uv = rows[0]
            uv += 1
            db.execute("UPDATE discord SET uv=? WHERE id= ?", (uv, str(message.author),))
            sql.commit()
            print(f"{payload.user_id} has added {payload.emoji} to the message: {message.content}")
        elif payload.emoji.name == "downvote":
            db.execute("SELECT dv FROM discord WHERE id = ?", (str(message.author),))
            rows = db.fetchone()
            dv = rows[0]
            dv += 1
            db.execute("UPDATE discord SET dv=? WHERE id= ?", (dv, str(message.author),))
            sql.commit()
            print(f"{payload.user_id} has added {payload.emoji} to the message: {message.content}")

            #Hall of Shame
            reaction = get(message.reactions, emoji=payload.emoji)
            shame = reaction.count
            reqShame = 6

            if shame >= reqShame:
                db.execute("SELECT StarMessageID FROM starboard WHERE RootMessageID = ?", 
                                    (str(message.id),)) or None
                try:
                    rows = db.fetchone()
                    msg_id = rows[0]
                except:
                    pass

                embed = Embed(title="Hall Of Shame", 
                            color=message.author.color,
                            timestamp=datetime.utcnow())

                fields = [("Author", message.author.mention, False),
                        ("Content", message.content or "See attachment", False),
                        ("Downvotes", shame, False)]

                for name, value, inline in fields:
                    embed.add_field(name = name, value=value, inline=inline)

                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                try:
                    star_message = await self.HOS.fetch_message(msg_id)
                    await star_message.edit(embed=embed)
                    db.execute("UPDATE starboard SET Stars = ? WHERE RootMessageID = ?", (shame, str(message.id),))

                except:
                    star_message = await self.HOS.send(embed=embed)
                    db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?)", (str(message.id), str(star_message.id),))

                # if shame == reqShame:
                #     star_message = await self.HOS.send(embed=embed)
                #     db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?)", (str(message.id),), str(star_message.id))

                # else:
                #     star_message = await self.HOS.fetch_message(msg_id)
                #     await star_message.edit(embed=embed)
                #     db.execute("UPDATE starboard SET Stars = ? WHERE RootMessageID = ?", shame, (str(message.id),))
            
        else:
            pass

    async def on_raw_reaction_remove(self, payload):
        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.emoji.name == "upvote":
            db.execute("SELECT uv FROM discord WHERE id = ?", (str(message.author),))
            rows = db.fetchone()
            uv = rows[0]
            if uv != 0: 
                uv -= 1
                db.execute("UPDATE discord SET uv=? WHERE id= ?", (uv, str(message.author),))
                sql.commit()
                print(f"{payload.user_id} has removed {payload.emoji} from the message: {message.content}")
        elif payload.emoji.name == "downvote":
            db.execute("SELECT dv FROM discord WHERE id = ?", (str(message.author),))
            rows = db.fetchone()
            dv = rows[0]
            if dv != 0:
                dv -= 1
                db.execute("UPDATE discord SET dv=? WHERE id= ?", (dv, str(message.author),))
                sql.commit()
                print(f"{payload.user_id} has removed {payload.emoji} from the message: {message.content}")

            #Hall of Shame
            try:
                reaction = get(message.reactions, emoji=payload.emoji)
                shame = reaction.count

                db.execute("SELECT StarMessageID FROM starboard WHERE RootMessageID = ?", 
                                    (str(message.id),)) or None
                rows = db.fetchone()
                msg_id = rows[0]

                embed = Embed(title="Hall Of Shame", 
                            color=message.author.color,
                            timestamp=datetime.utcnow())

                fields = [("Author", message.author.mention, False),
                        ("Content", message.content or "See attachment", False),
                        ("Downvotes", shame, False)]

                for name, value, inline in fields:
                    embed.add_field(name = name, value=value, inline=inline)

                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)

                
                star_message = await self.HOS.fetch_message(msg_id)
                await star_message.edit(embed=embed)
                db.execute("UPDATE starboard SET Stars = ? WHERE RootMessageID = ?", (shame, str(message.id),))
            except:
                pass
        else:
            pass

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, ctx, exc):
        raise getattr(exc, "original", exc)

    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        self.HOS = self.get_channel(883807348701925416)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Field of Hopes and Dreams'))
        print('Logged in as {0} ({0.id})'.format(self.user))
        print('------')

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("$")(bot, msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        keyword1 = r"\bforgot\b"
        keyword2 = r"\bforgor\b"
        keyword3 = r"\bone\b"
        keyword4 = r"\b1\b"

        if len(re.findall(keyword1, msg.content, re.I)) > 0:
            await ctx.send("forgor 💀")
        
        if len(re.findall(keyword2, msg.content, re.I)) > 0:
            await ctx.send("forgot ❤️")

        if len(re.findall(keyword3, msg.content, re.I)) > 0 or len(re.findall(keyword4, msg.content, re.I)) > 0:
            await ctx.send("Uno!")

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await update_data(str(msg.author))
            await add_messages(str(msg.author))
            await self.process_commands(msg)
     