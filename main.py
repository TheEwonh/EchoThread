### IMPORTS ###
import discord
import json
import traceback
from modules.verification import VerificationView
from modules.rolepicker import ButtonsPingView
from modules.rolepicker import ButtonsInterestsView
from modules.banland import AppealButton, ManageAppeal
from modules import database
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("TOKEN")
### VALUES ###
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
avatar = discord.File("sources/avatar.png", filename="avatar.png")

### MAIN ###
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)7s | %(name)24s | %(message)s",
    filename="bot.log",
    filemode="a",
    encoding="utf-8"
)
logger = logging.getLogger("EchoThread")

logger.info("------------------------------------------")
with open("config.json", "r") as f:
    config = json.load(f)

class MyBot(commands.Bot):
    async def setup_hook(self):
        await database.setup()
        await self.load_extension("modules.verification")
        logger.info("Verification module loaded")
        await self.load_extension("modules.commands")
        logger.info("Commands module loaded")
        await self.load_extension("modules.messages")
        logger.info("Messages module loaded")
        await self.load_extension("modules.events")
        logger.info("Events module loaded")
        await self.load_extension("modules.rolepicker")
        logger.info("Rolepicker module loaded")
        await self.load_extension("modules.moderation")
        logger.info("Moderation module loaded")
        await self.load_extension("modules.banland")
        logger.info("Banland module loaded")
        await self.load_extension("modules.logger")
        logger.info("Logger module loaded")
        await self.load_extension("modules.experience")
        logger.info("Experience module loaded")
        self.add_view(VerificationView())
        self.add_view(ButtonsPingView())
        self.add_view(ButtonsInterestsView())
        self.add_view(AppealButton(self))
        self.add_view(ManageAppeal(self))
        await self.tree.sync(guild=discord.Object(id=config["guild"]))

bot = MyBot(command_prefix="!", intents=intents)
@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    
bot.run(TOKEN)