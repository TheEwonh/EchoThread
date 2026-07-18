import discord
from discord.ext import commands
import json, logging

logger = logging.getLogger("Messages")
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def rules(self):
        channel = self.bot.get_channel(config["channels"]["RULES"])
        embed = discord.Embed(
            title="Please read the rules before chatting",
            color=0xB48CFF
        )
        embed.add_field(
            name="**Rules**",
            value=(
                "**Be respectful**\n"
                "└ Treat everyone with respect\n"
                "└ No harassment, insults or targeted toxicity\n"
                "**No discrimination**\n"
                "└ This server is LGBTQ+ friendly\n"
                "└ Homophobia, transphobia, racism, sexism or any other form of discrimination is prohibited\n"
                "**No NSFW**\n"
                "└ Pornographic, sexually explicit or otherwise NSFW content is not allowed\n"
                "**No spam**\n"
                "└ Avoid spam, excessive mentions, flood or disruptive behavior\n"
                "**Stay on topic**\n"
                "└ Use the correct channels and keep discussions relevant\n"
                "**No advertising**\n"
                "└ Do not advertise servers, products or social media without staff permission\n"
                "\n"
                "Not knowing these rules does not exempt you from consequences"
            ),
            inline = False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        await channel.send(embed=embed, file=avatar)
        logger.info("Rules were sent")
    
    async def info(self):
        embed = discord.Embed(
            title="💜 Information",
            color=0xB48CFF
        )
        embed.add_field(
            name="**Who are we?**",
            value=(
                "We are EchoThread, an independent game development studio starting as a small team with big ideas\n"
                "\n"
                "Our goals:\n"
                "\- Build projects we're proud of\n"
                "\- Grow as a studio\n"
                "\- Share our development journey\n"
                "\- Create friendly and welcoming community around our projects\n"
                "\n"
                "Whether you're here to play our games, follow development or simply chat with others, we're glad to have you here\n"
                "\n"
                "Welcome to **EchoThread** 💜\n"
            ),
            inline = False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        channel = self.bot.get_channel(config["channels"]["INFO"])
        await channel.send(embed=embed, file=avatar)
        logger.info("Information was sent")
    
    async def announcements(self, file):
        ann_config = json.loads((await file.read()).decode("utf-8"))
        channel = self.bot.get_channel(config["channels"]["NEWS"])
        
        embed = discord.Embed(
            title=ann_config["title"],
            color=0xB48CFF
        )
        embed.add_field(
            name=ann_config["description"],
            value=("\n".join(ann_config["fields"])),
            inline = False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")

        await channel.send(embed=embed, file=avatar)
        await channel.send(f"||{self.bot.get_channel(config['channels']['NEWS']).guild.get_role(config['roles']['ANNOUNCEMENTS']).mention}||")
        logger.info("News were sent")
    
    async def gameupd(self, file):
        gameupd_config = json.loads((await file.read()).decode("utf-8"))
        channel = self.bot.get_channel(config["channels"]["NEWS"])
        
        embed = discord.Embed(
            title=gameupd_config["title"],
            color=0xB48CFF
        )
        embed.add_field(
            name=gameupd_config["description"],
            value=("\n".join(gameupd_config["fields"])),
            inline = False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        
        await channel.send(embed=embed, file=avatar)
        await channel.send(f"||{self.bot.get_channel(config['channels']['NEWS']).guild.get_role(config['roles']['GAMEUPD']).mention}||")
        logger.info("Game updates were sent")

    async def devupd(self, file):
        devupd_config = json.loads((await file.read()).decode("utf-8"))
        channel = self.bot.get_channel(config["channels"]["CHANGELOG"])

        embed = discord.Embed(
            title=devupd_config["title"],
            color=0xB48CFF
        )
        embed.add_field(
            name=devupd_config["description"],
            value=("\n".join(devupd_config["fields"])),
            inline = False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        
        await channel.send(embed=embed, file=avatar)
        await channel.send(f"||{self.bot.get_channel(config['channels']['CHANGELOG']).guild.get_role(config['roles']['DEVUPD']).mention}||")
        logger.info("Development updates were sent")

    async def adm_announcements(self, file):
        ann_config = json.loads((await file.read()).decode("utf-8"))
        channel = self.bot.get_channel(config["channels"]["ADM_ANNOUNCEMENTS"])
        
        embed = discord.Embed(
            title=ann_config["title"],
            color=0xB48CFF
        )
        embed.add_field(
            name=ann_config["description"],
            value=("\n".join(ann_config["fields"])),
            inline = False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")

        await channel.send(embed=embed, file=avatar)
        await channel.send(f"||{self.bot.get_channel(config['channels']['ADM_ANNOUNCEMENTS']).guild.get_role(config['roles']['ANNOUNCEMENTS']).mention}||")
        logger.info("Admin announcements were sent")

    async def sendmsg(self, channel_id, attach=None):
        channel = self.bot.get_channel(int(channel_id))
        if channel is None:
            logger.warning(f"Channel {channel_id} was not found")
            return
        
        if isinstance(attach, discord.Attachment):
            if attach.filename == "embed.json":
                msg = json.loads((await attach.read()).decode("utf-8"))
                embed = discord.Embed(
                    title=msg["title"],
                    color=0xB48CFF
                )
                embed.add_field(
                    name=msg["description"],
                    value=("\n".join(msg["fields"])),
                    inline = False
                )
                avatar = discord.File("sources/avatar.png", filename="avatar.png")
                embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")

                logger.info(f"Embed sent to {channel_id} with sendmsg")
                await channel.send(embed=embed, file=avatar)
                return
        
        if isinstance(attach, str):
            logger.info(f"Text was sent to {channel_id} with sendmsg")
            await channel.send(attach)
            return
        logger.info(f"File was sent to {channel_id} with sendmsg")
        await channel.send(file=await attach.to_file())

async def setup(bot):
    await bot.add_cog(Messages(bot))