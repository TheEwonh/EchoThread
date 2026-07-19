### IMPORTS ###
import discord, time, json
from discord.ext import commands
from modules import database as db

### VALUES ###
with open("config.json", "r") as f:
    config = json.load(f)
cooldown = {}
# ^^^ | type: dynamic - "user_id":int = int(time.time())+5
levels = {
    "10": (1527998049555579041, 7),
    "20": (1528000221093822584, 10),
    "30": (1528000549356830730, 12),
    "40": (1528001268587429888, 15),
    "50": (1528001484157882370, 18),
    "60": (1528001840153624688, 20),
    "70": (1528002107183992833, 23),
    "80": (1528002496864456774, 25),
    "90": (1528002703731458108, 28),
    "100": (1528002874020335637, 30)
}
# ^^^ | type: static - role_id:int = increase:int
# Table levels (user_id, experience, level)

### MAIN ###
class Experience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if config["guild"] != message.guild.id:
            return
        
        member = message.author
        if cooldown.get(str(member.id), 0) and time.time() <= cooldown.get(str(member.id)):
            return
        cooldown.update({str(member.id): int(time.time())+5})

        if len(message.content) < 5:
            return
        exp = await db.get("levels", member.id)
        if not exp:
            await db.setInfo("levels", member.id, 1, 10, 0, 5)
        else:
            experience, exp_levelup, level, addition_exp = exp[1], exp[2], exp[3], exp[4]
            experience += 1
            if experience == exp_levelup:
                experience = 0
                level += 1
                exp_levelup += addition_exp
                if str(level) in levels and member.guild.get_role(levels[str(level)][0]) not in member.roles:
                    await member.add_roles(
                        member.guild.get_role(levels[str(level)][0])
                    )
                    addition_exp = levels[str(level)][1]
                await message.reply(f"Congratulations, {member.mention}!\nYou reached Level {level}{f" and received {member.guild.get_role(levels(str[level][0])).mention}!" if str(level) in levels else "!"}")
            
            await db.setInfo("levels", member.id, experience, exp_levelup, level, addition_exp)

    async def leaderboard(self, member: discord.Member, interaction: discord.Interaction | None = None):
        exp = await db.get("levels", member.id)
        if not exp:
            await db.setInfo("levels", member.id, 0, 10, 0, 5)
            exp = await db.get("levels", member.id)
        level, experience, exp_levelup = exp[3], exp[1], exp[2]
        if not interaction: 
            return await db.getLeaderboardPlace(level, experience)
        top = await db.getLeaderboard(10)
        embed = discord.Embed(
            title="Leaderboard: Top 10",
            color=0xB48CFF
        )
        text = ""
        for user in top:
            place = top.index(user) + 1
            text += f"{"🥇 " if place == 1 else "🥈 " if place == 2 else "🥉 " if place == 3 else f"{place}."} {interaction.guild.get_member(user[0]).mention}\nLevel {user[1]} • {user[2]} XP\n\n"
        embed.add_field(
            name="Members:",
            value=text+f"Your position:\n#{await db.getLeaderboardPlace(level, experience)} • Level {level} • {experience}/{exp_levelup} XP",
            inline=False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        await interaction.response.send_message(embed=embed, file=avatar)

    async def get_exp(self, member: discord.Member, interaction: discord.Interaction):
        rank = await self.leaderboard(member)
        exp = await db.get("levels", member.id)
        if not exp:
            await db.setInfo("levels", 0, 10, 0, 5)
            level, experience, exp_levelup = 0, 0, 10
        else:
            level, experience, exp_levelup = exp[3], exp[1], exp[2]
        embed = discord.Embed(
            title=f"Level information",
            description=f"For user {member.mention}",
            color=0xB48CFF
        )
        finished = (experience / exp_levelup) * 100
        embed.add_field(
            name="Details:",
            value=(
                f"🏅 Rank: #{rank}\n"
                f"⭐ Level: {level}\n"
                f"✨ XP: {experience}/{exp_levelup}\n\n"
                f"{("█"*max(0, int(finished/10))).ljust(10, "░")} - {finished:05.2f}%"
            ),
            inline=False
        )
        avatar = discord.File("sources/avatar.png", filename="avatar.png")
        embed.set_footer(text="EchoThread", icon_url="attachment://avatar.png")
        await interaction.response.send_message(embed=embed, file=avatar)
    
async def setup(bot):
    await bot.add_cog(Experience(bot))
