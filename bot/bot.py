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

sql = sqlite3.connect("/home/pi/Desktop/Bot/data/Logan.db")
db = sql.cursor()

async def update_data(user, display):
    db.execute("SELECT id FROM member")
    rows = db.fetchall()
    found = False
    for row in rows:
        if row[0] == user:
            found = True
            db.execute(f"UPDATE member SET display=? WHERE id= ?", (display, user,))
            sql.commit() 
    if found == False:
        print("User not found, adding New User to database")
        db.execute(f"INSERT INTO member (id, display,  msg) VALUES(?, ?, ?)", (user, display, 0,))
        sql.commit()
    
async def add_messages(user):
    db.execute(f"SELECT msg FROM member WHERE id = ?", (user,))
    rows = db.fetchone()
    msg = rows[0]
    msg += 1
    db.execute(f"UPDATE member SET msg=? WHERE id= ?", (msg, user,))
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
            db.execute("SELECT uv FROM member WHERE id = ?", (str(payload.user_id),))
            rows = db.fetchone()
            uv = rows[0]
            uv += 1
            db.execute("UPDATE member SET uv=? WHERE id= ?", (uv, str(payload.user_id),))
            sql.commit()
            print(f"{payload.user_id} has added {payload.emoji} to the message: {message.content}")
        elif payload.emoji.name == "downvote":
            db.execute("SELECT dv FROM member WHERE id = ?", (str(payload.user_id),))
            rows = db.fetchone()
            dv = rows[0]
            dv += 1
            db.execute("UPDATE member SET dv=? WHERE id= ?", (dv, str(payload.user_id),))
            sql.commit()
            print(f"{payload.user_id} has added {payload.emoji} to the message: {message.content}")

            #Hall of Shame
            server = int(str(message.guild.id))
            HOSchannel = db.execute("SELECT HOS FROM member WHERE id=?", (server,))                       
            rows = db.fetchone()
            try:
                id = rows[0]
                HOS = self.get_channel(id)
            except:
                id = None
            if HOS is not None:
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
                            ("Channel", message.channel.mention, True),
                            ("Downvotes", shame, True),
                            ("Content", message.content or "See attachment", False),
                            ("Message", "[Click to jump to message](%s)" % message.jump_url, False)]

                    embed.set_thumbnail(url = message.author.avatar_url)

                    for name, value, inline in fields:
                        embed.add_field(name = name, value=value, inline=inline)

                    if len(message.attachments):
                        embed.set_image(url=message.attachments[0].url)

                    try:
                        star_message = await HOS.fetch_message(msg_id)
                        await star_message.edit(embed=embed)
                        db.execute("UPDATE starboard SET Stars = ? WHERE RootMessageID = ?", (shame, str(message.id),))

                    except:
                        star_message = await HOS.send(embed=embed)
                        db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?)", (str(message.id), str(star_message.id),))

    async def on_raw_reaction_remove(self, payload):
        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.emoji.name == "upvote":
            db.execute("SELECT uv FROM member WHERE id = ?", (str(payload.user_id),))
            rows = db.fetchone()
            uv = rows[0]
            if uv != 0: 
                uv -= 1
                db.execute("UPDATE member SET uv=? WHERE id= ?", (uv, str(payload.user_id),))
                sql.commit()
                print(f"{payload.user_id} has removed {payload.emoji} from the message: {message.content}")
        elif payload.emoji.name == "downvote":
            db.execute("SELECT dv FROM member WHERE id = ?", (str(payload.user_id),))
            rows = db.fetchone()
            dv = rows[0]
            if dv != 0:
                dv -= 1
                db.execute("UPDATE member SET dv=? WHERE id= ?", (dv, str(payload.user_id),))
                sql.commit()
                print(f"{payload.user_id} has removed {payload.emoji} from the message: {message.content}")

            #Hall of Shame
            server = int(str(message.guild.id))
            HOSchannel = db.execute("SELECT HOS FROM server WHERE id=?", (server,))           
            rows = db.fetchone()
            try:
                id = rows[0]
                HOS = self.get_channel(id)  
            except:
                id = None
            if HOS is not None:
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
                            ("Channel", message.channel.mention, True),
                            ("Downvotes", shame, True),
                            ("Content", message.content or "See attachment", False),
                            ("Message", "[Click to jump to message](%s)" % message.jump_url, False)]

                    embed.set_thumbnail(url = message.author.avatar_url)

                    for name, value, inline in fields:
                        embed.add_field(name = name, value=value, inline=inline)

                    if len(message.attachments):
                        embed.set_image(url=message.attachments[0].url)

                    
                    star_message = await HOS.fetch_message(msg_id)
                    await star_message.edit(embed=embed)
                    db.execute("UPDATE starboard SET Stars = ? WHERE RootMessageID = ?", (shame, str(message.id),))
                except:
                    pass

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, ctx, exc):
        raise getattr(exc, "original", exc)

    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        #self.HOS = self.get_channel(883807348701925416)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Field of Hopes and Dreams'))
        print('Logged in as {0} ({0.id})'.format(self.user))
        print('------')

    async def prefix(self, bot, msg):
        prefixes = ["$", "Alexa ", "alexa "]
        return commands.when_mentioned_or(*prefixes)(bot, msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        keywords = [r"\byippee\b"]

        if not msg.author.bot:
            if len(re.findall(keywords[0], msg.content, re.I)) > 0:
                await ctx.send("https://c.tenor.com/g16jQZqbvWoAAAAC/yippee-happy.gif")

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        await update_data(int(msg.author.id), str(msg.author))
        await add_messages(int(msg.author.id))
        await self.process_commands(msg)