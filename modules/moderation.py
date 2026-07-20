### IMPORTS ###
import discord
from discord.ext import commands
import logging, time, json, re
from modules import database as db
from datetime import datetime

with open("config.json", "r") as f:
    config = json.load(f)

logger = logging.getLogger("Moderation")

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def kick(self, member: discord.Member, reason: str, interaction: discord.Interaction):
        embed = discord.Embed(
            title="You have been kicked from EchoThread",
            color=0xB38CFF
        )
        embed.add_field(
            name="Details:",
            value=(f"Reason: {reason}\n"
                   f"Moderator: {interaction.user.name}\n\n"
                   "This is NOT a ban\n"
                   "You may join the server again at any time\n"
                   "The invite link is available in the bot profile."
                ),
            inline=False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        try:
            await member.send(embed=embed, file=avatar)
        except discord.Forbidden:
            logger.warning(f"Kick message was not sent to {member.name} ({member.id}), because DMs were closed")
        except Exception as e:
            logger.error(f"Kick message was not sent to {member.name} ({member.id}), because Exception occurred. Error: {e}")
        await interaction.response.send_message(f"{member.name} ({member.id}) was kicked")
        await member.kick(reason=f"{reason} - Kicked by {interaction.user.name}")
        logger.info(f"{interaction.user.name} kicked {member.name} ({member.id}) for {reason}")

    async def ban(self, member: discord.Member, reason: str, interaction: discord.Interaction):
        embed = discord.Embed(
            title="You have been permanently banned from EchoThread",
            color=0xB48CFF
        )
        embed.add_field(
            name="Details:",
            value=(f"**Reason**: {reason}\n"
                   f"**Moderator**: @{interaction.user.name}\n\n"
                   "If you wish to appeal this ban - join discord server.\n"
                   "https://discord.gg/VJFBV5cEhe"
            ),
            inline=False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        try:
            await member.send(embed=embed, file=avatar)
        except discord.Forbidden:
            logger.warning(f"Appeal message was not sent to {member.name} ({member.id}), because DMs were closed")
        except Exception as e:
            logger.error(f"Appeal message was not sent to {member.name} ({member.id}), because Exception occurred. Error: {e}")
        await member.ban(reason=f"{reason} - Banned by {interaction.user.name}")
        await interaction.response.send_message(f"{member.name} ({member.id}) was banned")
        await db.setInfo("bans", member.id, reason, interaction.user.name)
        logger.info(f"{member.name} ({member.id}) was banned for {reason} by {interaction.user.name}")

    async def mute(self, member: discord.Member, reason: str, duration_first: str, interaction: discord.Interaction):
        duration = duration_first.lower()
        multipliers = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800,
            "mo": 2592000,
            "y": 31536000,
            "c": 3153600000
        }
        matches = re.findall(r"(\d+)(mo|[smhdwyc])", duration)
        if not matches:
            await interaction.response.send_message("Invalid duration. Example: 30m, 1h30m, 2d", ephemeral=True)
            return
        parsed = "".join(f"{value}{unit}" for value, unit in matches)
        if parsed != duration:
            await interaction.response.send_message("Invalid duration. Example: 30m, 1h30m, 2d", ephemeral=True)
            return
        seconds = 0
        for value, unit in matches:
            seconds += int(value) * multipliers[unit]

        duration = int(time.time())+seconds
        embed = discord.Embed(
            title="You have been muted on EchoThread",
            color=0xB48CFF
        )
        embed.add_field(
            name="Details:",
            value=(f"**Reason**: {reason}\n"
                   f"**Duration**: {duration_first} - until {datetime.fromtimestamp(duration).strftime("%d %B %Y, %H:%M:%S")}\n"
                   f"**Moderator**: {interaction.user.name}\n\n"
                   "You can still view the server, but you won't be able to send messages"
            ),
            inline=False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        try:
            await member.send(embed=embed, file=avatar)
        except discord.Forbidden:
            logger.warning(f"Mute message was not sent to {member.name} ({member.id}), because DMs were closed")
        except Exception as e:
            logger.error(f"Mute message was not sent to {member.name} ({member.id}), because Exception occurred. Error: {e}")
        await member.add_roles(
            interaction.guild.get_role(config["roles"]["MUTED"]),
            reason=f"{reason} - Muted by {interaction.user.name}"
        )
        await db.setInfo("mutes", member.id, reason, duration, interaction.user.name)
        await interaction.response.send_message(f"{member.name} was muted successfully!", ephemeral=True)

    async def mute_warn(self, member: discord.Member, severity: int, interaction: discord.Interaction):
        await member.add_roles(
            interaction.guild.get_role(config["roles"]["MUTED"])
        )
        await db.setInfo("mutes", member.id, "3rd warning", int(time.time()) + 2592000 * severity, interaction.user.name)

    async def warn(self, member: discord.Member, reason: str, severity: int, interaction: discord.Interaction):
        warnings = await db.get("warns", member.id)
        embed = discord.Embed(
            title="You receive warning",
            color=0xB48CFF
        )
        embed.add_field(
            name="Details:",
            value=(
                f"**Reason**: {reason}\n"
                f"**Severity**: {"🟢 Low" if severity == 1 else "🟡 Medium" if severity == 2 else "🔴 High"}\n"
                f"**Expires**: {"In 1 month" if severity == 1 else "In 2 months" if severity == 2 else "In 3 months"}\n\n"
                f"{"You have 3 warnings, you received 1 week mute" if warnings and len(warnings) == 2 else "This is only warning. Receiving 3 warnings gives 1 week mute"}\n"
                "If your violations were **severe** - you'll be permanently banned"
            )
        )

        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        try:
            await member.send(embed=embed, file=avatar)
        except discord.Forbidden:
            logger.warning(f"Warn message was not sent to {member.name} ({member.id}), because DMs were closed")
        except Exception as e:
            logger.error(f"Warn message was not sent to {member.name} ({member.id}), because Exception occurred. Error: {e}")
        expires = int(time.time()) + 2592000 * severity
        await db.setInfo("warns", member.id, reason, severity, expires, interaction.user.id)
        await interaction.response.send_message(f"{member.name} ({member.id}) was warned", ephemeral=True)
        logger.info(f"{member.name} ({member.id}) was warned for {reason} by {interaction.user.name} ({interaction.user.id})")
        if warnings and len(warnings) == 2:
            channel = self.bot.get_channel(config["channels"]["FOUNDER_CRY_CORNER"])
            embed = discord.Embed(
                title="🚨Member received their third warning🚨",
                description=f"{member.name} ({member.id}) received third warning",
                color=0xED4245
            )
            embed.add_field(
                name="Violations:",
                value=await db.get("warns", member.id),
                inline=False
            )
            avatar = discord.File("sources/avatar.png", filename="avatar.png")
            embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
            await channel.send(embed=embed, file=avatar)

async def setup(bot):
    await bot.add_cog(Moderation(bot))