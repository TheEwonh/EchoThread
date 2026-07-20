### IMPORTS ###
import discord
from discord.ext import commands, tasks
import logging, json, time
from modules import database as db

with open("config.json", "r") as f:
    config = json.load(f)

### MAIN ###
logger = logging.getLogger("Events")
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_watcher.start()

    def cog_unload(self):
        self.mute_watcher.cancel()

    @tasks.loop(seconds=1)
    async def mute_watcher(self):
        guild = self.bot.get_guild(config["guild"])
        if guild is None:
            return
        muted_role = guild.get_role(config["roles"]["MUTED"])
        expired = await db.get("expired_mutes", int(time.time()))
        for user_id, expires in expired:
            member = guild.get_member(user_id)
            if member:
                try:
                    await member.remove_roles(muted_role, reason="Mute expired")
                except discord.HTTPException:
                    pass
                try:
                    embed = discord.Embed(
                        title="You have been unmuted on EchoThread",
                        color=0xB48CFF
                    )
                    embed.add_field(
                        name="Details:",
                        value="Follow rules to avoid further mutes",
                        inline=False
                    )
                    avatar = discord.File("sources/avatar.png", filename="avatar.png")
                    embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
                    await member.send(embed=embed, file=avatar)
                except discord.Forbidden:
                    logger.warning(f"Unmute message was not sent to {member.name} ({member.id}), because DMs were closed")
                except Exception as e:
                    logger.error(f"Unmute message was not sent to {member.name} ({member.id}), because Exception occurred. Error: {e}")

            await db.delete("mutes", user_id)
        expired_warns = await db.get("expired_warns", int(time.time()))
        for warn_id, member_id, expires in expired_warns:
            member = guild.get_member(member_id)
            if member:
                try:
                    embed = discord.Embed(
                        title="Your warn on EchoThread expired",
                        color=0xB48CFF
                    )
                    embed.add_field(
                        name="Details:",
                        value="Follow rules to avoid further warns",
                        inline=False
                    )
                    avatar = discord.File("sources/avatar.png", filename="avatar.png")
                    embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
                    await member.send(embed=embed, file=avatar)
                except discord.Forbidden:
                    logger.warning(f"Unwarn message was not sent to {member.name} ({member.id}), because DMs were closed")
                except Exception as e:
                    logger.error(f"Unwarn message was not sent to {member.name} ({member.id}), because Exception occurred. Error: {e}")

            await db.delete("warns", warn_id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != config["guild"]:
            return
        isMuted = await db.get("mutes", member.id)
        if isMuted:
            if isMuted[2] > int(time.time()):
                await member.add_roles(member.guild.get_role(config["roles"]["MUTED"]))
        logger.info(f"{member.name} ({member.id}) joined the server")
        visitor = member.guild.get_role(config["roles"]["VISITOR"])
        await member.add_roles(visitor)
        channel = self.bot.get_channel(config["channels"]["WELCOME"])
        embed = discord.Embed(
            title=f"New member",
            description=f"Welcome to EchoThread, {member.mention}!",
            color=0xB48CFF
        )
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        embed.add_field(name="" ,value=f"Please read <#{config['channels']['RULES']}> before chatting")
        embed.set_thumbnail(url=member.display_avatar.url)
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        await channel.send(embed=embed, file=avatar)

async def setup(bot):
    await bot.add_cog(Events(bot))