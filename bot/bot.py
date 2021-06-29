from pathlib import Path

import discord
import sqlite3

from discord.ext import commands
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

    async def on_reaction_add(self, reaction, user):
        if reaction.emoji.name == "upvote":
            db.execute("SELECT uv FROM discord WHERE id = ?", (str(reaction.message.author),))
            rows = db.fetchone()
            uv = rows[0]
            uv += 1
            db.execute("UPDATE discord SET uv=? WHERE id= ?", (uv, str(reaction.message.author),))
            sql.commit()
            print(f"{user.name} has added {reaction.emoji} to the message: {reaction.message.content}")
        elif reaction.emoji.name == "downvote":
            db.execute("SELECT dv FROM discord WHERE id = ?", (str(reaction.message.author),))
            rows = db.fetchone()
            dv = rows[0]
            dv += 1
            db.execute("UPDATE discord SET dv=? WHERE id= ?", (dv, str(reaction.message.author),))
            sql.commit()
            print(f"{user.name} has added {reaction.emoji} to the message: {reaction.message.content}")
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
        else:
            pass

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, ctx, exc):
        raise getattr(exc, "original", exc)

    async def on_ready(self):
        self.client_id = (await self.application_info()).id
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Harvard Lectures'))
        print('Logged in as {0} ({0.id})'.format(self.user))
        print('------')

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("$")(bot, msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await update_data(str(msg.author))
            await add_messages(str(msg.author))
            await self.process_commands(msg)