### IMPORTS ###
import discord, logging, json
from modules import database
from discord.ext import commands
from discord import app_commands
from typing import Optional

with open("config.json", "r") as f:
    config = json.load(f)
FOUNDER_ROLE = config["roles"]["FOUNDER"]
MODERATOR_ROLE = config["roles"]["MODERATOR"]

### MAIN ###
logger = logging.getLogger("Commands")
class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # FOUNDER ONLY COMMANDS
    @commands.command()
    async def verify_setup(self, ctx):
        if ctx.guild is None:
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing verify_setup in DMs")
            return
        if not any(role.id == FOUNDER_ROLE for role in ctx.author.roles):
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing verify_setup command")
            return
        verification = self.bot.get_cog("Verification")
        if verification is None:
            logger.error("Verification module isn't loaded.")
            return

        await verification.verify_setup()
    
    @commands.command()
    async def messages(self, ctx, action=None):
        if ctx.guild is None:
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing message command in DMs")
            return
        if not any(role.id == FOUNDER_ROLE for role in ctx.author.roles):
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing message command")
            return
        if action is None:
            return
        messages_mod = self.bot.get_cog("Messages")
        if messages_mod is None:
            logger.error("Messages module isn't loaded.")
            return
        match action:
            case "send_rules":
                logger.info("send_rules command was fired")
                await messages_mod.rules()
            case "send_info":
                logger.info("senf_info command was fired")
                await messages_mod.info()
            case "send_announcements":
                if not ctx.message.attachments:
                    logger.warning("Tried to fire send_announcements but no files were attached")
                    return
                logger.info("send_announcements command was fired")
                await messages_mod.announcements(ctx.message.attachments[0])
            case "send_gameupd":
                if not ctx.message.attachments:
                    logger.warning("Tried to fire send_gameupd but no files were attached")
                    return
                logger.info("send_gameupd command was fired")
                await messages_mod.gameupd(ctx.message.attachments[0])
            case "send_devupd":
                if not ctx.message.attachments:
                    logger.warning("Tried to fire send_devupd but no files were attached")
                    return
                logger.info("send_devupd command was fired")
                await messages_mod.devupd(ctx.message.attachments[0])

    @commands.command()
    async def sendmsg(self, ctx, channel_id=None, msg=None):
        if ctx.guild is None:
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing sendmsg command in DMs")
            return
        if not any(role.id == FOUNDER_ROLE for role in ctx.author.roles):
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing sendmsg command")
            return
        
        messages_mod = self.bot.get_cog("Messages")
        if messages_mod is None:
            logger.error("Messages module isn't loaded.")
            return
        if channel_id == None:
            logger.warning("Tried firing sendmsg command with no channel_id")
            return
        
        if msg:
            logger.info("sendmsg was fired with text")
            await messages_mod.sendmsg(channel_id, msg)
        elif ctx.message.attachments:
            logger.info("sendmsg was fired with file")
            await messages_mod.sendmsg(channel_id, ctx.message.attachments[0])
    
    @commands.command()
    async def send_roles(self, ctx):
        if ctx.guild is None:
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing send_roles command in DMs")
            return
        if not any(role.id == FOUNDER_ROLE for role in ctx.author.roles):
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing send_roles command")
            return
        rolepicker = self.bot.get_cog("Rolepicker")
        if rolepicker is None:
            logger.error("Rolepicker module isn't loaded.")
            return
        
        logger.info("send_roles command was fired")
        await rolepicker.send_roles()

    @commands.command()
    async def purge(self, ctx, count: int = None, channel_id: int = None):
        if ctx.guild is None:
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing purge command in DMs")
            return
        if not any(role.id == FOUNDER_ROLE for role in ctx.author.roles):
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing purge command")
            return
        if not count:
            logger.warning("Tried firing purge command, but no message count was given")
            return
        if not channel_id:
            await ctx.channel.purge(limit=count+1)
            return
        channel = self.bot.get_channel(channel_id)
        await channel.purge(limit=count)
        return

    @commands.command()
    async def db(self, ctx, action: str, table: str, *args):
        if ctx.guild is None:
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing db command in DMs")
            return
        if not any(role.id == FOUNDER_ROLE for role in ctx.author.roles):
            logger.warning(f"{ctx.author.name} ({ctx.author.id}) tried firing db command")
            return
        if not args:
            await ctx.send("Missing arguments")
            logger.warning("Tried using db command, but no arguments were given")
            return
        if table in ("bans", "appeals", "appeal_cd", "mutes", "warns", "levels"):
            match action:
                case "get":
                    await ctx.send(f"Result for get method on {table} table - {await database.get(table, args[0])}")
                case "set":
                    if len(args) < 2:
                        await ctx.send("Missing value")
                        logger.warning("Tried setting value, but no value/key was given")
                        return
                    await database.setInfo(table, args)
                    await ctx.send(f"Value {args[1]} with key {args[0]} was set to table {table}")
                case "delete":
                    await database.delete(table, args[0])
                    await ctx.send(f"Value from table {table} with key {args[0]} was successfully deleted")
                case _:
                    await ctx.send("Unknown action.")
                    logger.warning(f"Tried calling db with {action}")
        else:
            await ctx.send("Unknown table")
            logger.warning(f"Tried accessing unknown table {table}")

    # BANLAND ONLY COMMANDS
    @commands.command()
    async def send_appeal(self, ctx):
        if ctx.guild is None:
            logger.warning(f"BANLAND - {ctx.author.name} ({ctx.author.id}) tried firing send_appeal command in DMs")
            return
        if not any(role.id == FOUNDER_ROLE for role in ctx.author.roles):
            logger.warning(f"BANLAND - {ctx.author.name} ({ctx.author.id}) tried firing send_appeal command")
            return
        banland = self.bot.get_cog("Banland")
        if banland is None:
            logger.error("Banland module isn't loaded.")
            return
        await banland.send_appeal()
        
    # MODERATOR ONLY COMMANDS
    @app_commands.command(name="ban", description="Bans member (Moderator only command)")
    @app_commands.guilds(discord.Object(id=config["guild"]))
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if interaction.guild.get_role(MODERATOR_ROLE) not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried firing ban command")
            return
        
        if interaction.user.id == member.id:
            await interaction.response.send_message("🤔", ephemeral=True)
            logger.warning(f"{interaction.user.name} tried calling ban on themselve")
            return
        
        moderation = self.bot.get_cog("Moderation")
        if moderation is None:
            logger.error("Moderation module isn't loaded.")
            return
        
        await moderation.ban(member, reason, interaction)
    
    @app_commands.command(name="unban", description="Unbans member (Moderator only command)")
    @app_commands.guilds(discord.Object(id=config["guild"]))
    async def unban(self, interaction: discord.Interaction, member_id: str):
        if interaction.guild.get_role(MODERATOR_ROLE) not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried firing unban command")
            return
        
        member_id = int(member_id)
        if interaction.user.id == member_id:
            await interaction.response.send_message("🤔", ephemeral=True)
            logger.warning(f"{interaction.user.name} tried calling unban on themselve")
            return
        
        isBanned = await database.get("bans", member_id)
        if not isBanned:
            await interaction.response.send_message(f"{member_id} is not banned")
            logger.warning(f"{interaction.user.name} tried firing unban command on {member_id}")
            return
        
        try:
            user = await self.bot.fetch_user(member_id)
        except discord.NotFound:
            await interaction.response.send_message("User not found", ephemeral=True)
            return
        except:
            await interaction.response.send_message(f"Tried getting user, but exception occurred. Please notify founder.", ephemeral=True)
            return
        await interaction.guild.unban(user)
        await database.delete("bans", member_id)
        await interaction.response.send_message(f"{user.name} ({member_id}) was unbanned")
        logger.info(f"{user.name} ({member_id}) was unbanned by {interaction.user.name}")
    
    @app_commands.command(name="kick", description="Kicks member (Moderator only command)")
    @app_commands.guilds(discord.Object(id=config["guild"]))
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if interaction.guild.get_role(MODERATOR_ROLE) not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried firing kick command")
            return
        
        if interaction.user.id == member.id:
            await interaction.response.send_message("🤔", ephemeral=True)
            logger.warning(f"{interaction.user.name} tried calling mute on themselve")
            return
        
        moderation = self.bot.get_cog("Moderation")
        if moderation is None:
            logger.error("Moderation module isn't loaded.")
            return
        
        await moderation.kick(member, reason, interaction)
    
    @app_commands.command(name="mute", description="Mutes member (Moderator only command)")
    @app_commands.guilds(discord.Object(id=config["guild"]))
    async def mute(self, interaction: discord.Interaction, member: discord.Member, reason: str, time: str):
        if interaction.guild.get_role(MODERATOR_ROLE) not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried firing kick command")
            return
        
        if interaction.user.id == member.id:
            await interaction.response.send_message("🤔", ephemeral=True)
            return
        
        isMuted = await database.get("mutes", member.id)
        if isMuted:
            await interaction.response.send_message(f"{member.name} ({member.id}) is already muted", ephemeral=True)
            logger.info(f"Tried firing mute command, but user is already in mute (by - {interaction.user.name})")
            return
        
        moderation = self.bot.get_cog("Moderation")
        if moderation is None:
            logger.error("Moderation module isn't loaded.")
            return
        
        await moderation.mute(member, reason, time, interaction)
    
    @app_commands.command(name="unmute", description="Unmutes member (Moderator only command)")
    @app_commands.guilds(discord.Object(id=config["guild"]))
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.guild.get_role(MODERATOR_ROLE) not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried firing unmute command")
            return
        
        if interaction.user.id == member.id:
            await interaction.response.send_message("🤔", ephemeral=True)
            logger.warning(f"{interaction.user.name} tried calling unmute on themselve")
            return
        
        isMuted = await database.get("mutes", member.id)
        if not isMuted:
            await interaction.response.send_message(f"{member.id} is not muted")
            logger.warning(f"{interaction.user.name} tried firing unmute command on {member.id}")
            return
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
        await member.remove_roles(interaction.guild.get_role(config["roles"]["MUTED"]), reason=f"Unmuted by {interaction.user.name}")
        await database.delete("mutes", member.id)
        await interaction.response.send_message(f"{member.name} ({member.id}) was unmuted")
        logger.info(f"{member.name} ({member.id}) was unmuted by {interaction.user.name}")

    @app_commands.command(name="warn", description="Warnes member (Moderator only command)")
    @app_commands.guilds(discord.Object(id=config["guild"]))
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str, severity: int):
        if interaction.guild.get_role(MODERATOR_ROLE) not in interaction.user.roles:
            await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried firing warn command")
            return
        
        if interaction.user.id == member.id:
            await interaction.response.send_message("🤔", ephemeral=True)
            logger.warning(f"{interaction.user.name} tried calling warn on themselve")
            return
        
        if not 1 <= severity <= 3:
            await interaction.response.send_message("Invalid severity.\nEnter number:\n1 - Low\n2 - Medium\n3 - High", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried calling warn command, but wrong severity was given ({severity})")
            return

        moderation = self.bot.get_cog("Moderation")
        if moderation is None:
            logger.error("Moderation module isn't loaded.")
            return

        warnings = await database.get("warns", member.id)
        if warnings and len(warnings) == 2:
            await moderation.mute_warn(member, severity, interaction)
            logger.info(f"{interaction.user.name} ({interaction.user.id}) gave 1 week mute (via warning) to {member.name} ({member.id})")
        if warnings and len(warnings) == 3:
            await interaction.response.send_message("Member already has 3 warnings. They received 1 week mute", ephemeral=True)
            await moderation.mute_warn(member, severity, interaction)
            logger.info(f"{interaction.user.name} ({interaction.user.id}) gave 1 week mute (via warning) to {member.name} ({member.id})")
            return

        await moderation.warn(member, reason, severity, interaction)

    # Member commands
    @app_commands.command(name="level", description="Gets members level")
    @app_commands.guilds(discord.Object(id=config["guild"]))
    async def level(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not member:
            member = interaction.user
        
        experience = self.bot.get_cog("Experience")
        if not experience:
            logger.error("Experience module isn't loaded.")
            return
        
        await experience.get_exp(member, interaction)

    @app_commands.command(name="leaderboard", description="Gets level leaderboard")
    @app_commands.guilds(discord.Object(id=config["guild"]))
    async def leaderboard(self, interaction: discord.Interaction):
        member = interaction.user
        
        experience = self.bot.get_cog("Experience")
        if not experience:
            logger.error("Experience module isn't loaded.")
            return
        
        await experience.leaderboard(member, interaction)

async def setup(bot):
    await bot.add_cog(Commands(bot))