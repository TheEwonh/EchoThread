### IMPORTS ###
import discord, logging, time, json, re
from datetime import datetime
from discord.ext import commands
from modules import database as db

### CONSTANTS ###
BANLAND_SERVER = 1525814415893729301
APPEAL_CHANNEL = 1525816369948528680
BANLAND_CATEGORY = 1525816005069246604
MODERATOR_ROLE = 1525814653291331730

### MAIN ###
with open("config.json", "r") as f:
    config = json.load(f)

logger = logging.getLogger("Banland")

class ManageAppeal(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅", custom_id="accept_button")
    async def accept_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild.get_role(MODERATOR_ROLE) not in interaction.user.roles:
            await interaction.response.send_message("Only moderator can make decision", ephemeral=True)
            logger.info(f"{interaction.user.name} ({interaction.user.id}) tried operating they own appeal")
            return
        channel = interaction.channel
        message = interaction.message
        appeal_info = await db.get("appeals_bymessage", message.id)
        if not appeal_info:
            await interaction.response.send_message("Appeal record not found. Contact founder", ephemeral=True)
            logger.warning("Appeal record was not found")
            return
        embed = discord.Embed(
            title="Your appeal was accepted",
            color=0xB48CFF
        )
        embed.add_field(
            name="",
            value="You were unbanned\nYou can join back main server\nhttps://discord.gg/4SyRrAavqB",
            inline=False
        )
        avatar = discord.File("sources/avatar_banland.png", filename="avatar_banland.png")
        embed.set_footer(text="EchoThread〡Banland", icon_url="attachment://avatar_banland.png")
        await db.delete("appeals", appeal_info[0])
        await db.delete("bans", appeal_info[0])
        await self.bot.get_guild(config["guild"]).unban(discord.Object(id=appeal_info[0]))
        user = await self.bot.fetch_user(appeal_info[0])
        try:
            await user.send(embed=embed, file=avatar)
        except discord.Forbidden:
            logger.warning(f"Tried to send approved appeal message to {user.name} ({user.id}), but they're DMs are closed")
        except Exception as e:
            logger.error(f"Tried to send approved appeal message to {user.name} ({user.id}), but Exception occurred. Error: {e}")
        guild = self.bot.get_guild(BANLAND_SERVER)
        try:
            member = await guild.fetch_member(appeal_info[0])
            await member.kick(reason="Appeal approved")
        except discord.NotFound:
            logger.warning("Failed to kick member, they were not found")
        except Exception as e:
            logger.error(f"Failed to kick member, Exception occurred. Error: {e}")
        nickname = re.sub(r"[^a-z0-9_-]", "-", user.name.lower())
        await channel.edit(
            name=f"closed-{nickname}"
        )
        await channel.set_permissions(
            guild.get_role(MODERATOR_ROLE),
            view_channel=False
        )
        logger.info(f"{user.name} ({user.id}) appeal was approved by {interaction.user.name} ({interaction.user.id})")

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="❌", custom_id="decline_button")
    async def decline_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild.get_role(MODERATOR_ROLE) not in interaction.user.roles:
            await interaction.response.send_message("Only moderator can make decision", ephemeral=True)
            logger.info(f"{interaction.user.name} ({interaction.user.id}) tried operating they own appeal")
            return
        channel = interaction.channel
        guild = interaction.guild
        appeal_info = await db.get("appeals_bymessage", interaction.message.id)
        if not appeal_info:
            await interaction.response.send_message("Appeal record not found. Contact founder", ephemeral=True)
            logger.warning("Appeal record was not found")
            return
        embed = discord.Embed(
            title="Your appeal was declined",
            color=0xB48CFF
        )
        embed.add_field(
            name="",
            value="You can appeal again after 1 month",
            inline=False
        )
        avatar = discord.File("sources/avatar_banland.png", filename="avatar_banland.png")
        embed.set_footer(text="EchoThread〡Banland", icon_url="attachment://avatar_banland.png")
        await db.delete("appeals", appeal_info[0])
        user = await self.bot.fetch_user(appeal_info[0])
        try:
            await user.send(embed=embed, file=avatar)
        except discord.Forbidden:
            logger.warning(f"Tried to send declined appeal message to {user.name} ({user.id}), but they're DMs are closed")
        except Exception as e:
            logger.error(f"Tried to send declined appeal message to {user.name} ({user.id}), but Exception occurred. Error: {e}")
        await db.setInfo("appeal_cd", user.id, int(time.time())+2592000)
        nickname = re.sub(r"[^a-z0-9_-]", "-", user.name.lower())
        await channel.edit(
            name=f"closed-{nickname}"
        )
        await channel.set_permissions(
            user,
            view_channel=False
        )
        await channel.set_permissions(
            guild.get_role(MODERATOR_ROLE),
            view_channel=False
        )
        logger.info(f"{user.name} ({user.id}) appeal was decline by {interaction.user.name} ({interaction.user.id})")

class AppealButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="Appeal", style=discord.ButtonStyle.blurple, emoji="📜", custom_id="appeal_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(BANLAND_CATEGORY)
        appeal_cd = await db.get("appeal_cd", interaction.user.id)
        appeals = await db.get("appeals", interaction.user.id)
        if appeals:
            await interaction.response.send_message(f"You already have opened appeal. <#{appeals[1]}>", ephemeral=True)
            return
        if appeal_cd and appeal_cd[1] > int(time.time()):
            await interaction.response.send_message(f"You are on cooldown. You can appeal again at {datetime.fromtimestamp(appeal_cd[1])}", ephemeral=True)
            return
        nickname = re.sub(r"[^a-z0-9_-]", "-", interaction.user.name.lower())
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                embed_links=True,
                attach_files=True
            ),
            guild.get_role(MODERATOR_ROLE): discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                embed_links=True,
                attach_files=True
            )
        }
        newChannel = await guild.create_text_channel(
            name=f"appeal-{nickname}",
            category=category,
            overwrites=overwrites
        )
        embed = discord.Embed(
            title="Appeal our decision",
            color=0xB48CFF
        )
        ban_info = await db.get("bans", interaction.user.id)
        embed.add_field(
            name="Ban information",
            value=(f"**User**: {interaction.user.mention}\n"
                   f"**User ID**: {interaction.user.id}\n"
                   f"**Ban reason**: {ban_info[1]}\n"
                   f"**Moderator**: {ban_info[2]}\n\n"
                   "**Provide next information**:\n"
                   "Please explain in detail why you think your ban should be removed\n"
                   "Attach screenshots, videos or any evidence if available\n"
                   "Our moderators will review your appeal as soon as possible\n"
                   "Open your DMs to receive the result of your appeal. Otherwise you won't get notified\n\n"
                   "You will be able to appeal again after 1 month, in case your appeal would be declined"
            ),
            inline=False
        )
        avatar = discord.File("sources/avatar_banland.png", filename="avatar_banland.png")
        embed.set_footer(text="EchoThread〡Banland", icon_url="attachment://avatar_banland.png")
        message = await newChannel.send(embed=embed, file=avatar, view=ManageAppeal(self.bot))
        logger.info(f"{interaction.user.name} ({interaction.user.id}) sent appeal")
        await db.setInfo("appeals", interaction.user.id, message.id)

class Banland(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != BANLAND_SERVER:
            return
        if not await db.get("bans", member.id):
            await member.kick(reason=f"{member.name} ({member.id}) tried joining, but they were unbanned")

    async def send_appeal(self):
        guild = self.bot.get_guild(1525814415893729301)
        channel = guild.get_channel(APPEAL_CHANNEL)

        embed = discord.Embed(
            title="Appeal your ban there",
            color=0xB48CFF
        )
        embed.add_field(
            name="Details:",
            value=(
                "If you believe this ban was made by mistake, click the button below to appeal it\n"
                "Please make sure your Direct Messages are enabled. Otherwise, we may be unable to notify you about the outcome of your appeal\n"
                "**WARNING**: If you appeal ban that was given to you fairly - you will unable to appeal it for 1 month"
            ),
            inline=False
        )
        avatar = discord.File("sources/avatar_banland.png", filename="avatar_banland.png")
        embed.set_footer(text="EchoThread〡Banland", icon_url="attachment://avatar_banland.png")
        await channel.send(embed=embed, file=avatar, view=AppealButton(self.bot))

async def setup(bot):
    await bot.add_cog(Banland(bot))