import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base
from repository import populate_database

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

db_file = "dbddle.db"
all_characters_file = "data.json"
add_file = "add_character.json"
if not os.path.exists(db_file):
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        populate_database(session, all_characters_file)
else:
    engine = create_engine(f"sqlite:///{db_file}")
    Session = sessionmaker(bind=engine)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix={"_"}, intents=intents)

    @property
    def session(self):
        return Session()


client = Bot()

cogs = ["Functions.classic"]


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game("DBDLE")
    )
    for cog in cogs:
        try:
            print(f"loading cog {cog}")
            await client.load_extension(cog)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print(f"failed to load cog {cog}\n{exc}")


client.run(TOKEN)
