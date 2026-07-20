### IMPORTS ###
import discord
from discord.ext import commands
import json, logging

with open("config.json", "r") as f:
    config = json.load(f)

### MAIN ###
logger = logging.getLogger("Rolepicker")
class ButtonsPingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Announcements", style=discord.ButtonStyle.grey, emoji="📢", custom_id="announcements_role")
    async def announcements_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["ANNOUNCEMENTS"])
        if any(role.id == config["roles"]["ANNOUNCEMENTS"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("You unsubscribed from Announcements.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("You subscribed to Announcements.", ephemeral=True)
    
    @discord.ui.button(label="Game Updates", style=discord.ButtonStyle.grey, emoji="🎮", custom_id="gameupd_role")
    async def gameupd_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["GAMEUPD"])
        if any(role.id == config["roles"]["GAMEUPD"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("You unsubscribed from Game Updates.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("You subscribed to Game Updates.", ephemeral=True)

    @discord.ui.button(label="Dev Updates", style=discord.ButtonStyle.grey, emoji="🚧", custom_id="devupd_role")
    async def devupd_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["DEVUPD"])
        if any(role.id == config["roles"]["DEVUPD"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("You unsubscribed from Development Updates role.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("You subscribed to Development Updates role.", ephemeral=True)

class ButtonsInterestsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Creator", style=discord.ButtonStyle.grey, emoji="🛠️", custom_id="creator_role", row=1)
    async def creator_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["CREATOR"])
        if any(role.id == config["roles"]["CREATOR"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("Creator role was removed from your profile.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You received Creator role. <@{interaction.user.id}>", ephemeral=True)
    
    @discord.ui.button(label="Programmer", style=discord.ButtonStyle.grey, emoji="💻", custom_id="programmer_role", row=1)
    async def programmer_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["PROGRAMMER"])
        if any(role.id == config["roles"]["PROGRAMMER"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("Programmer role was removed from your profile.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You received Programmer role. <@{interaction.user.id}>", ephemeral=True)

    @discord.ui.button(label="3D Artist", style=discord.ButtonStyle.grey, emoji="🧊", custom_id="3dartist_role", row=1)
    async def art3d_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["ARTIST3D"])
        if any(role.id == config["roles"]["ARTIST3D"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("3D Artist role was removed from your profile.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You received 3D Artist role. <@{interaction.user.id}>", ephemeral=True)

    @discord.ui.button(label="Artist", style=discord.ButtonStyle.grey, emoji="🎨", custom_id="artist_role", row=1)
    async def artist_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["ARTIST"])
        if any(role.id == config["roles"]["ARTIST"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("Artist role was removed from your profile.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You received Artist role. <@{interaction.user.id}>", ephemeral=True)

    @discord.ui.button(label="Animator", style=discord.ButtonStyle.grey, emoji="🎬", custom_id="animator_role", row=2)
    async def animator_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["ANIMATOR"])
        if any(role.id == config["roles"]["ANIMATOR"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("Animator role was removed from your profile.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You received Animator role. <@{interaction.user.id}>", ephemeral=True)

    @discord.ui.button(label="Game Designer", style=discord.ButtonStyle.grey, emoji="🧩", custom_id="gamedes_role", row=2)
    async def gamedes_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["GAMEDES"])
        if any(role.id == config["roles"]["GAMEDES"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("Game Designer role was removed from your profile.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You received Game Designer role. <@{interaction.user.id}>", ephemeral=True)
    
    @discord.ui.button(label="Gamer", style=discord.ButtonStyle.grey, emoji="🎮", custom_id="gamer_role", row=2)
    async def gamer_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["GAMER"])
        if any(role.id == config["roles"]["GAMER"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("Gamer role was removed from your profile.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You received Gamer role. <@{interaction.user.id}>", ephemeral=True)

    @discord.ui.button(label="Musician", style=discord.ButtonStyle.grey, emoji="🎵", custom_id="musician_role", row=2)
    async def musician_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(config["roles"]["MUSICIAN"])
        if any(role.id == config["roles"]["MUSICIAN"] for role in interaction.user.roles):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("Musician role was removed from your profile.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You received Musician role. <@{interaction.user.id}>", ephemeral=True)
        
class Rolepicker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_roles(self):
        channel = self.bot.get_channel(config["channels"]["ROLES"])
        embed1 = discord.Embed(
            title="📰 Notification Roles",
            color=0xB48CFF
        )
        embed1.add_field(
            name="Description",
            value=(
                "◆ Announcements - receive important server announcements\n"
                "◆ Game Updates - receive notifications about game updates\n"
                "◆ Dev Updates - receive development updates and changelogs\n"
                "\n"
                "Click a button to subscribe or unsubscribe.\n"
            ),
            inline=False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed1.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        await channel.send(embed=embed1, view=ButtonsPingView(), file=avatar)
        embed2 = discord.Embed(
            title="⭐ Interests",
            color=0xB48CFF
        )
        embed2.add_field(
            name="Description",
            value=(
                "◆ Creator - creates videos, streams, blogs or other content\n"
                "◆ Programmer - interested in programming or software development\n"
                "◆ 3D Artist - creates 3D models, environments or assets\n"
                "◆ Artist - creates illustrations, concept art or digital artwork\n"
                "◆ Animator - creates 2D or 3D animations\n"
                "◆ Game Designer - designs game mechanics, levels or gameplay systems\n"
                "◆ Gamer - enjoys playing games\n"
                "◆ Musician - composes, produces or performs music\n"
                "\n"
                "Click a button to add or remove a role.\n"
            ),
            inline=False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed2.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        await channel.send(embed=embed2, view=ButtonsInterestsView(), file=avatar)
    
async def setup(bot):
    await bot.add_cog(Rolepicker(bot))