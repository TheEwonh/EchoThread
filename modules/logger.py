### IMPORTS ###
import discord, time
from discord.ext import commands
from datetime import datetime

### MAIN ###
async def createEmbed(text):
    embed=discord.Embed(
        title=text[0],
        color=text[1]
    )
    embed.add_field(
        name="Details:",
        value=text[2],
        inline=False
    )
    avatar = discord.File("sources/avatar.png", filename="avatar.png")
    embed.set_footer(text=f"EchoThread · {datetime.fromtimestamp(int(time.time())).strftime("%d %B %Y, %H:%M:%S")}", icon_url="attachment://avatar.png")
    return (embed, avatar)

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(1524092605590147162)
        embed = await createEmbed((
            "New member",
            0x57F287,
            f"{member.mention} ({member.id}) joined the server"
        ))
        await channel.send(embed=embed[0], file=embed[1])
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(1524092605590147162)
        embed = await createEmbed((
            "Member left",
            0xED4245,
            f"{member.mention} ({member.id}) left the server"
        ))
        await channel.send(embed=embed[0], file=embed[1])

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content == after.content or after.author.bot:
            return
        channel = self.bot.get_channel(1524092605590147162)
        
        embed = await createEmbed((
            "Changed message",
            0xFEE75C,
            f"{after.author.mention} ({after.author.id}) edited message at <#{after.channel.id}>\n"
            "**Before**:\n"
            f"{before.content or "*No text*"}\n\n"
            "**After**:\n"
            f"{after.content or "*No text*"}"
        ))
        await channel.send(embed=embed[0], file=embed[1])
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        channel = self.bot.get_channel(1524092605590147162)
        
        embed = await createEmbed((
            "Deleted message",
            0xED4245,
            f"{message.author.mention} ({message.author.id}) deleted a **message** at <#{message.channel.id}>:\n"
            f"{message.content or "*No text*"}"
        ))
        await channel.send(embed=embed[0], file=embed[1])

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel = self.bot.get_channel(1524092605590147162)
        if not before.mute and after.mute:
            entry = None
            async for log in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                if log.target.id == member.id:
                    entry = log
                    break
            if entry:
                moderator = entry.user
            embed = await createEmbed((
                "Moderator muted user",
                0xED4245,
                f"{member.mention} ({member.id}) got server-muted by {moderator.mention} ({moderator.id})"
            ))
            await channel.send(embed=embed[0], file=embed[1])
        if before.mute and not after.mute:
            entry = None
            async for log in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                if log.target.id == member.id:
                    entry = log
                    break
            if entry:
                moderator = entry.user
            embed = await createEmbed((
                "Moderator unmuted user",
                0x57F287,
                f"{member.mention} ({member.id}) got server-unmuted by {moderator.mention} ({moderator.id})"
            ))
            await channel.send(embed=embed[0], file=embed[1])
        if not before.deaf and after.deaf:
            entry = None
            async for log in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                if log.target.id == member.id:
                    entry = log
                    break
            if entry:
                moderator = entry.user
            embed = await createEmbed((
                "Moderator deafed user",
                0xED4245,
                f"{member.mention} ({member.id}) got server-deafed by {moderator.mention} ({moderator.id})"
            ))
            await channel.send(embed=embed[0], file=embed[1])
        if before.deaf and not after.deaf:
            entry = None
            async for log in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                if log.target.id == member.id:
                    entry = log
                    break
            if entry:
                moderator = entry.user
            embed = await createEmbed((
                "Moderator undeafed user",
                0x57F287,
                f"{member.mention} ({member.id}) got server-undeafed by {moderator.mention} ({moderator.id})"
            ))
            await channel.send(embed=embed[0], file=embed[1])
        if before.channel and not after.channel:
            embed = await createEmbed((
                "Member left the channel",
                0x5865F2,
                f"{member.mention} ({member.id}) left the channel"
            ))
            await channel.send(embed=embed[0], file=embed[1])
        if not before.channel and after.channel:
            embed = await createEmbed((
                "Member joined the channel",
                0x5865F2,
                f"{member.mention} ({member.id}) joined the channel"
            ))
            await channel.send(embed=embed[0], file=embed[1])

async def setup(bot):
    await bot.add_cog(Logger(bot))