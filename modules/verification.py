### IMPORTS ###
import discord
from discord.ext import commands
import random, logging, asyncio
### ROLES ###
FOUNDER_ROLE = 1524107410061393980
VISITOR_ROLE = 1524107946320072714
MEMBER_ROLE = 1524109369103618099
### CHANNELS ###
VERIFICATION_CHANNEL = 1524093430634905661
RULES_CHANNEL = 1524085746955452618
### ARRAYS ###
cooldown = set()
### OTHERS ###
CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ234679"

### MAIN ###
logger = logging.getLogger("Verification")
def generate_captcha():
    return "".join(random.choices(CHARS, k=random.randint(5, 10)))

async def remove_after(user_id):
    await asyncio.sleep(5)
    cooldown.discard(user_id)

class VerificationModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Verification")
        self.captcha = generate_captcha()
        self.captcha_input = discord.ui.TextInput(label="Copy text - "+self.captcha, placeholder="Enter the text above", required=True)
        self.add_item(self.captcha_input)

    async def on_submit(self, interaction):
        if self.captcha_input.value.upper() == self.captcha:
            user = interaction.user
            guild = interaction.guild
            member_role = guild.get_role(MEMBER_ROLE)
            visitor_role = guild.get_role(VISITOR_ROLE)
            await user.add_roles(member_role)
            await user.remove_roles(visitor_role)
            embed = discord.Embed(
                title="You are verified!",
                description=f"You've got access to the server! Be sure to read <#{RULES_CHANNEL}>",
                color=0xB48CFF
            )
            avatar = discord.File("sources/avatar.png", filename="avatar.png")
            embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
            try:
                await user.send(embed=embed, file=avatar)
            except discord.Forbidden:
                pass
            await interaction.response.send_message("✅ Successfully verified!",ephemeral=True)
            logger.info(f"{user.name} ({user.id}) passed captcha! {self.captcha_input.value.upper()}=={self.captcha}")
        else:
            await interaction.response.send_message("❌ Wrong captcha!", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) failed captcha! {self.captcha_input.value.upper()}!={self.captcha}")

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == VISITOR_ROLE for role in interaction.user.roles):
            return
        
        if interaction.user.id in cooldown:
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried accessing captcha while cooldown!")
            await interaction.response.send_message("Cooldown!", ephemeral=True)
            return
        
        cooldown.add(interaction.user.id)
        asyncio.create_task(remove_after(interaction.user.id))
        
        await interaction.response.send_modal(VerificationModal())

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def verify_setup(self):
        channel = self.bot.get_channel(VERIFICATION_CHANNEL)
        embed = discord.Embed(
            title = "Verification",
            description = "Click the button below to verify and gain access to the server",
            color = 0xB48CFF
        )
        
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        await channel.send(embed=embed, view=VerificationView(), file=avatar)

async def setup(bot):
    await bot.add_cog(Verification(bot))

# working