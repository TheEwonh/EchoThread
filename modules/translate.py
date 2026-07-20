### IMPORTS ###
import discord, deepl, os, logging, json, re
from discord.ext import commands
from discord import app_commands
from modules import database as db

translator = deepl.Translator(os.getenv("DEEPL_API_KEY"))
logger = logging.getLogger("Translate")
with open("config.json", "r") as f:
    config = json.load(f)

class SelectMenu(discord.ui.View):
        def __init__(self, message):
            super().__init__(timeout=None)
            self.message = message

        @discord.ui.select(
                placeholder = "Choose language",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(label="English (US)", value="EN-US", emoji="🇺🇸"),
                    discord.SelectOption(label="English (UK)", value="EN-GB", emoji="🇬🇧"),
                    discord.SelectOption(label="Russian", value="RU", emoji="🇷🇺")
                ]
        )
        async def language_select(self, interaction: discord.Interaction, select: discord.ui.Select):
            # "message_id": {"lang": [text]}
            lang = select.values[0]
            translation = await db.get("translate", self.message.id) or dict()
            if translation:
                translation = json.loads(translation["details"])
            if translation and lang in translation:
                result_text = translation[lang]
                if len(result_text) > 1:
                    embed = discord.Embed(
                        title=result_text[0],
                        color=self.message.embeds[0].color
                    )
                    # Checking if fields
                    if result_text[1]:
                        embed.add_field(
                            name=result_text[2],
                            value=result_text[3],
                            inline=False
                        )
                    avatar = discord.File("sources/avatar.png", filename="avatar.png")
                    embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
                    await interaction.response.send_message(embed=embed, file=avatar, ephemeral=True)
                    logger.info(f"{interaction.user.name} translated {self.message.id} to {lang} language (found in database)")
                    return
                await interaction.response.send_message(result_text[0], ephemeral=True)
                logger.info(f"{interaction.user.name} translated {self.message.id} to {lang} language (found in database)")
                return

            if self.message.embeds:
                old_embed = self.message.embeds[0]
                title = old_embed.title
                fields = old_embed.fields
                text = [title,]
                placeholders = dict()
                cur_place = 0
                if fields:
                    for i in range(len(fields)):
                        text.extend([fields[i].name, fields[i].value])
                for field in text:
                    matches = re.findall(
                        r"<a?:\w+:\d+>|:\w+:",
                        field
                    )
                    for match in matches:
                        placeholders.update({f"__EMOJI{cur_place}__": match})
                        cur_place += 1
                cur_place = 0
                result = translator.translate_text(
                    text,
                    target_lang=lang
                )
                result_text = []
                for i in range(len(result)):
                    if i == 1:
                        result_text.append(bool(fields))
                    result_text.append(result[i].text)
                for field in result_text:
                    if field is bool:
                        continue
                    for placeholder, emoji in placeholders.items():
                        field = field.replace(placeholder, emoji)
                embed = discord.Embed(
                    title=result_text[0],
                    color=old_embed.color
                )
                if fields:
                    embed.add_field(
                        name=result_text[2],
                        value=result_text[3],
                        inline=False
                    )
                avatar = discord.File("sources/avatar.png", filename="avatar.png")
                embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
                await interaction.response.send_message(embed=embed, file=avatar, ephemeral=True)
                await db.setInfo("translate", self.message.id, translation | {lang: result_text})
                logger.info(f"{interaction.user.name} translated {self.message.id} to {lang} language")
                return
            result = translator.translate_text(
                text=self.message.content,
                target_lang=lang
            )
            await interaction.response.send_message(result.text, ephemeral=True)
            await db.setInfo("translate", self.message.id, translation | {lang: result_text})
            logger.info(f"{interaction.user.name} translated {self.message.id} to {lang} language")
            return

class TranslateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Translate", style=discord.ButtonStyle.grey, emoji="🌐", custom_id="translate_button")
    async def translatebtn_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Select language for text to be translated...", view=SelectMenu(interaction.message), ephemeral=True)

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # The code below was commented, because discord doesn't allow to use
        # Context menu commands in channels without having permission
        # To send messages. Y'know I can't give permission for that in news channels
        """
        self.translate = app_commands.ContextMenu(
            name="Translate",
            callback=self.translate_callback,
            guild_ids=(config["guild"],)
        )
        self.bot.tree.add_command(self.translate)
    
    async def translate_callback(self, interaction: discord.Interaction, message: discord.Message):
        if message.channel.id != config["channels"]["NEWS"]:
            await interaction.response.send_message(f"This channel is not supported (Use in <#{config['channels']['NEWS']}>)", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried translate message ({message.id}) in {message.channel.id}")
            return
        if message.attachments:
            await interaction.response.send_message(f"Attachments cannot be translated", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried translating... attachment? ({message.id})")
            return
        if message.stickers:
            await interaction.response.send_message(f"Stickers cannot be translated", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) seems to be braindead translating sticker ({message.id})")
            return
        if message.poll:
            await interaction.response.send_message(f"Polls cannot be translated", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried translating poll ({message.id})")
            return
        if message.components:
            await interaction.response.send_message(f"This component cannot be translated", ephemeral=True)
            logger.warning(f"{interaction.user.name} ({interaction.user.id}) tried translating component ({message.id})")
            return
        await interaction.response.send_message("Choose language...", ephemeral=True, view=SelectMenu(message)) 
        """

async def setup(bot: commands.Bot):
    await bot.add_cog(Translate(bot))