import discord
from discord.ext import commands
from datetime import timedelta

from core.logger import send_mod_log
from core.database import (
    add_warning,
    get_warnings,
    clear_warnings
)


CRIMSON = discord.Color.from_rgb(150, 25, 35)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # MODERATION CHECKS
    # =========================

    async def hierarchy_check(
        self,
        ctx: commands.Context,
        member: discord.Member
    ):
        if member == ctx.author:
            await ctx.send(
                "❌ You can't moderate yourself."
            )
            return False

        if member == ctx.guild.owner:
            await ctx.send(
                "❌ You can't moderate the server owner."
            )
            return False

        if member == ctx.guild.me:
            await ctx.send(
                "❌ You can't moderate Vexora."
            )
            return False

        if member.top_role >= ctx.author.top_role:
            await ctx.send(
                "❌ You can't moderate a member with an "
                "equal or higher role than yours."
            )
            return False

        bot_member = ctx.guild.me

        if member.top_role >= bot_member.top_role:
            await ctx.send(
                "❌ I can't moderate this member because "
                "their highest role is equal to or higher "
                "than my highest role."
            )
            return False

        return True

    # =========================
    # KICK
    # =========================

    @commands.hybrid_command(
        name="kick",
        description="Kick a member from the server."
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        ctx: commands.Context,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        if not await self.hierarchy_check(ctx, member):
            return

        await member.kick(reason=reason)

        await send_mod_log(
            ctx.guild,
            "👢 Kick",
            member,
            ctx.author,
            reason
        )

        embed = discord.Embed(
            title="👢 Member Kicked",
            description=(
                f"**{member}** has been kicked from the server."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="👤 Member",
            value=f"{member.mention}\n`{member.id}`",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(
            text="Vexora • Moderation System"
        )

        await ctx.send(embed=embed)

    # =========================
    # BAN
    # =========================

    @commands.hybrid_command(
        name="ban",
        description="Ban a member from the server."
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: commands.Context,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        if not await self.hierarchy_check(ctx, member):
            return

        await member.ban(reason=reason)

        await send_mod_log(
            ctx.guild,
            "🔨 Ban",
            member,
            ctx.author,
            reason
        )

        embed = discord.Embed(
            title="🔨 Member Banned",
            description=(
                f"**{member}** has been banned from the server."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="👤 Member",
            value=f"{member.mention}\n`{member.id}`",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(
            text="Vexora • Moderation System"
        )

        await ctx.send(embed=embed)

    # =========================
    # TIMEOUT
    # =========================

    @commands.hybrid_command(
        name="timeout",
        aliases=["mute"],
        description="Timeout a member."
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx: commands.Context,
        member: discord.Member,
        minutes: int,
        *,
        reason: str = "No reason provided"
    ):

        if not await self.hierarchy_check(ctx, member):
            return

        if minutes < 1 or minutes > 40320:
            return await ctx.send(
                "❌ Timeout duration must be between "
                "**1 minute** and **28 days**."
            )

        await member.timeout(
            timedelta(minutes=minutes),
            reason=reason
        )

        await send_mod_log(
            ctx.guild,
            "⏳ Timeout",
            member,
            ctx.author,
            f"{minutes} minute(s) — {reason}"
        )

        embed = discord.Embed(
            title="⏳ Member Timed Out",
            description=(
                f"**{member}** has been timed out."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="⏱️ Duration",
            value=f"{minutes} minute(s)",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(
            text="Vexora • Moderation System"
        )

        await ctx.send(embed=embed)

    # =========================
    # UNBAN
    # =========================

    @commands.hybrid_command(
        name="unban",
        description="Unban a user from the server."
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(
        self,
        ctx: commands.Context,
        user_id: str,
        *,
        reason: str = "No reason provided"
    ):

        try:
            user = await self.bot.fetch_user(
                int(user_id)
            )

        except (ValueError, discord.NotFound):

            return await ctx.send(
                "❌ Invalid user ID."
            )

        try:

            await ctx.guild.unban(
                user,
                reason=reason
            )

        except discord.NotFound:

            return await ctx.send(
                "❌ That user is not currently banned."
            )

        except discord.Forbidden:

            return await ctx.send(
                "❌ I don't have permission to unban that user."
            )

        await send_mod_log(
            ctx.guild,
            "🔓 Unban",
            user,
            ctx.author,
            reason
        )

        embed = discord.Embed(
            title="🔓 User Unbanned",
            description=(
                f"**{user}** has been unbanned."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="👤 User",
            value=f"{user.mention}\n`{user.id}`",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(
            text="Vexora • Moderation System"
        )

        await ctx.send(embed=embed)

    # =========================
    # UNMUTE
    # =========================

    @commands.hybrid_command(
        name="unmute",
        description="Remove a timeout from a member."
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(
        self,
        ctx: commands.Context,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        if not await self.hierarchy_check(ctx, member):
            return

        if not member.is_timed_out():

            return await ctx.send(
                f"❌ **{member}** is not currently timed out."
            )

        await member.timeout(
            None,
            reason=reason
        )

        await send_mod_log(
            ctx.guild,
            "🔓 Unmute",
            member,
            ctx.author,
            reason
        )

        embed = discord.Embed(
            title="🔓 Member Unmuted",
            description=(
                f"**{member}** is no longer timed out."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="👤 Member",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(
            text="Vexora • Moderation System"
        )

        await ctx.send(embed=embed)

    # =========================
    # PURGE
    # =========================

    @commands.hybrid_command(
        name="purge",
        description="Delete multiple messages."
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(
        self,
        ctx: commands.Context,
        amount: int
    ):

        if amount < 1 or amount > 100:

            return await ctx.send(
                "❌ Amount must be between **1 and 100**."
            )

        deleted = await ctx.channel.purge(
            limit=amount + 1
        )

        count = max(
            len(deleted) - 1,
            0
        )

        message = await ctx.send(
            f"🧹 Deleted **{count} messages**."
        )

        await message.delete(
            delay=3
        )

    # =========================
    # WARN
    # =========================

    @commands.hybrid_command(
        name="warn",
        description="Warn a member."
    )
    @commands.has_permissions(moderate_members=True)
    async def warn(
        self,
        ctx: commands.Context,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        if not await self.hierarchy_check(ctx, member):
            return

        warning_id = add_warning(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            reason
        )

        await send_mod_log(
            ctx.guild,
            "⚠️ Warning",
            member,
            ctx.author,
            f"Warning #{warning_id} — {reason}"
        )

        embed = discord.Embed(
            title="⚠️ Member Warned",
            description=(
                f"**{member}** has received a warning."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="⚠️ Warning",
            value=f"`#{warning_id}`",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(
            text="Vexora • Moderation System"
        )

        await ctx.send(embed=embed)

    # =========================
    # WARNINGS
    # =========================

    @commands.hybrid_command(
        name="warnings",
        description="View a member's warnings."
    )
    @commands.has_permissions(moderate_members=True)
    async def warnings(
        self,
        ctx: commands.Context,
        member: discord.Member
    ):

        rows = get_warnings(
            ctx.guild.id,
            member.id
        )

        if not rows:

            return await ctx.send(
                f"✅ **{member}** has no warnings."
            )

        embed = discord.Embed(
            title="⚠️ Warning History",
            description=(
                f"Warnings for {member.mention}"
            ),
            color=CRIMSON
        )

        for (
            warning_id,
            moderator_id,
            reason,
            created_at
        ) in rows[:10]:

            embed.add_field(
                name=f"Warning #{warning_id}",
                value=(
                    f"**Reason:** {reason}\n"
                    f"**Moderator:** <@{moderator_id}>\n"
                    f"**Date:** {created_at}"
                ),
                inline=False
            )

        embed.set_footer(
            text=(
                f"Total warnings: {len(rows)} • "
                "Vexora"
            )
        )

        await ctx.send(
            embed=embed
        )

    # =========================
    # CLEAR WARNINGS
    # =========================

    @commands.hybrid_command(
        name="clearwarnings",
        description="Clear all warnings from a member."
    )
    @commands.has_permissions(moderate_members=True)
    async def clearwarnings(
        self,
        ctx: commands.Context,
        member: discord.Member
    ):

        if not await self.hierarchy_check(ctx, member):
            return

        deleted = clear_warnings(
            ctx.guild.id,
            member.id
        )

        if deleted == 0:

            return await ctx.send(
                f"ℹ️ **{member}** has no warnings to clear."
            )

        await send_mod_log(
            ctx.guild,
            "🧹 Clear Warnings",
            member,
            ctx.author,
            f"Cleared {deleted} warning(s)."
        )

        embed = discord.Embed(
            title="🧹 Warnings Cleared",
            description=(
                f"Cleared **{deleted} warning(s)** "
                f"from **{member}**."
            ),
            color=CRIMSON
        )

        embed.set_footer(
            text="Vexora • Moderation System"
        )

        await ctx.send(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Moderation(bot)
    )