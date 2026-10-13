import re
from datetime import datetime, timezone

import discord
from discord.ext import commands

from core.database import (
    get_counting_settings,
    set_counting_settings,
    update_counting_progress,
    update_high_score,
    increment_counting_reset,
    reset_counting_progress,
)

CRIMSON = discord.Color.from_rgb(150, 25, 35)

CUSTOM_EMOJI_REGEX = re.compile(
    r"^<(?P<animated>a?):(?P<name>[A-Za-z0-9_]+):(?P<id>\d+)>$"
)


def parse_custom_emoji(value):
    if not value:
        return None

    value = value.strip()

    match = CUSTOM_EMOJI_REGEX.fullmatch(value)

    if not match:
        return None

    try:
        return discord.PartialEmoji(
            name=match.group("name"),
            id=int(match.group("id")),
            animated=bool(match.group("animated"))
        )
    except (TypeError, ValueError):
        return None


class Counting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ═════════════════════════════════════════════
    # COUNTING ENGINE
    # ═════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message(self, message):

        if not message.guild:
            return

        if message.author.bot:
            return

        settings = get_counting_settings(message.guild.id)

        if not settings:
            return

        (
            channel_id,
            correct_emoji,
            wrong_emoji,
            daily_goal,
            current_number,
            last_user_id,
            goal_reached_date,
            high_score,
            high_score_user_id,
            total_correct,
            total_resets
        ) = settings

        if not channel_id:
            return

        if message.channel.id != channel_id:
            return

        content = message.content.strip()

        if not content.isdigit():
            return

        try:
            number = int(content)
        except ValueError:
            return

        if number > 10**18:
            return

        today = datetime.now(timezone.utc).date().isoformat()

        # New UTC day
        if goal_reached_date and goal_reached_date != today:
            current_number = 0
            last_user_id = None
            goal_reached_date = None

            reset_counting_progress(message.guild.id)

        expected = current_number + 1

        # Same person twice
        if last_user_id == message.author.id:

            await self.handle_failure(
                message,
                wrong_emoji,
                reason="The same person cannot count twice in a row."
            )

            increment_counting_reset(message.guild.id)
            reset_counting_progress(message.guild.id)
            return

        # Wrong number
        if number != expected:

            await self.handle_failure(
                message,
                wrong_emoji,
                reason=f"The next number was **{expected}**."
            )

            increment_counting_reset(message.guild.id)
            reset_counting_progress(message.guild.id)
            return

        # Correct number
        current_number = number

        goal_reached = False

        if (
            daily_goal
            and daily_goal > 0
            and current_number >= daily_goal
            and goal_reached_date != today
        ):
            goal_reached = True
            goal_reached_date = today

        # Save progress
        update_counting_progress(
            message.guild.id,
            current_number,
            message.author.id,
            goal_reached_date
        )

        # New high score
        if current_number > high_score:

            update_high_score(
                message.guild.id,
                current_number,
                message.author.id
            )

            high_score = current_number
            high_score_user_id = message.author.id

        # Correct reaction
        emoji = parse_custom_emoji(correct_emoji)

        try:
            if emoji:
                await message.add_reaction(emoji)
            else:
                await message.add_reaction("✅")
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Daily goal reached
        if goal_reached:

            embed = discord.Embed(
                title="🏆 Daily Counting Goal Reached!",
                description=(
                    f"🎯 Today's goal of **{daily_goal}** has been reached!\n\n"
                    f"🔥 Count: **{current_number}**\n"
                    f"👑 Reached by: {message.author.mention}"
                ),
                color=discord.Color.gold()
            )

            embed.set_footer(
                text="Vexora • Counting Game • Developed by Potter"
            )

            try:
                await message.channel.send(embed=embed)
            except discord.HTTPException:
                pass

    # ═════════════════════════════════════════════
    # FAILURE
    # ═════════════════════════════════════════════

    async def handle_failure(
        self,
        message,
        wrong_emoji,
        reason
    ):

        emoji = parse_custom_emoji(wrong_emoji)

        try:
            if emoji:
                await message.add_reaction(emoji)
            else:
                await message.add_reaction("❌")
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Delete broken number after reacting
        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass

        embed = discord.Embed(
            title="💥 Counting Reset!",
            description=(
                f"❌ {message.author.mention} broke the count.\n\n"
                f"📌 {reason}\n\n"
                "🔄 The next correct number is **1**."
            ),
            color=CRIMSON
        )

        embed.set_footer(
            text="Vexora • Counting Game • Developed by Potter"
        )

        try:
            await message.channel.send(
                embed=embed,
                delete_after=6
            )
        except discord.HTTPException:
            pass

    # ═════════════════════════════════════════════
    # COUNTING GROUP
    # ═════════════════════════════════════════════

    @commands.hybrid_group(
        name="counting",
        description="Manage Vexora's counting game."
    )
    @commands.guild_only()
    async def counting(self, ctx):

        if ctx.invoked_subcommand is None:
            await self.send_status(ctx)

    # ═════════════════════════════════════════════
    # SETUP
    # ═════════════════════════════════════════════

    @counting.command(
        name="setup",
        description="Configure the counting game."
    )
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(
        add_reactions=True,
        send_messages=True,
        embed_links=True,
        manage_messages=True
    )
    async def setup_counting(
        self,
        ctx,
        channel: discord.TextChannel,
        correct_emoji: str = None,
        wrong_emoji: str = None,
        daily_goal: int = 0
    ):

        if daily_goal < 0:
            await ctx.send(
                "❌ Daily goal cannot be negative."
            )
            return

        correct = parse_custom_emoji(correct_emoji)
        wrong = parse_custom_emoji(wrong_emoji)

        if correct_emoji and not correct:
            await ctx.send(
                "❌ Invalid correct emoji.\n\n"
                "Example:\n"
                "`<:correct:123456789>`"
            )
            return

        if wrong_emoji and not wrong:
            await ctx.send(
                "❌ Invalid wrong emoji.\n\n"
                "Example:\n"
                "`<:wrong:123456789>`"
            )
            return

        for emoji in (correct, wrong):

            if emoji and emoji.guild_id:

                if emoji.guild_id != ctx.guild.id:
                    await ctx.send(
                        "❌ Please use custom emojis from this server."
                    )
                    return

        set_counting_settings(
            ctx.guild.id,
            channel_id=channel.id,
            correct_emoji=str(correct) if correct else None,
            wrong_emoji=str(wrong) if wrong else None,
            daily_goal=daily_goal
        )

        reset_counting_progress(ctx.guild.id)

        embed = discord.Embed(
            title="🔢 Counting Game Configured",
            description=(
                "Vexora's counting game is now active."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="📢 Channel",
            value=channel.mention,
            inline=True
        )

        embed.add_field(
            name="🎯 Daily Goal",
            value=(
                f"`{daily_goal}`"
                if daily_goal > 0
                else "`Disabled`"
            ),
            inline=True
        )

        embed.add_field(
            name="📈 Starting Number",
            value="`1`",
            inline=True
        )

        embed.add_field(
            name="✅ Correct",
            value=str(correct) if correct else "✅",
            inline=True
        )

        embed.add_field(
            name="❌ Wrong",
            value=str(wrong) if wrong else "❌",
            inline=True
        )

        embed.add_field(
            name="📜 Rules",
            value=(
                "• Numbers must be consecutive.\n"
                "• The same person cannot count twice.\n"
                "• Wrong numbers reset the count.\n"
                "• Broken messages are automatically deleted.\n"
                "• The next correct number is `1`."
            ),
            inline=False
        )

        embed.set_footer(
            text="Vexora • Counting Game • Developed by Potter"
        )

        await ctx.send(embed=embed)

    # ═════════════════════════════════════════════
    # GOAL
    # ═════════════════════════════════════════════

    @counting.command(
        name="goal",
        description="Set or change the daily counting goal."
    )
    @commands.has_permissions(manage_guild=True)
    async def goal(self, ctx, goal: int):

        if goal < 0:
            await ctx.send(
                "❌ Goal cannot be negative."
            )
            return

        set_counting_settings(
            ctx.guild.id,
            daily_goal=goal
        )

        if goal == 0:
            await ctx.send(
                "🎯 Daily counting goal **disabled**."
            )
            return

        await ctx.send(
            f"🎯 Daily counting goal set to **{goal}**."
        )

    # ═════════════════════════════════════════════
    # RESET
    # ═════════════════════════════════════════════

    @counting.command(
        name="reset",
        description="Reset the current counting score."
    )
    @commands.has_permissions(manage_guild=True)
    async def reset(self, ctx):

        reset_counting_progress(ctx.guild.id)

        embed = discord.Embed(
            title="🔄 Counting Reset",
            description=(
                "The current counting chain has been reset.\n\n"
                "The next correct number is **1**."
            ),
            color=CRIMSON
        )

        embed.set_footer(
            text="Vexora • Counting Game"
        )

        await ctx.send(embed=embed)

    # ═════════════════════════════════════════════
    # STATUS
    # ═════════════════════════════════════════════

    @counting.command(
        name="status",
        description="View the counting game status."
    )
    @commands.has_permissions(manage_guild=True)
    async def status_command(self, ctx):

        await self.send_status(ctx)

    async def send_status(self, ctx):

        settings = get_counting_settings(ctx.guild.id)

        (
            channel_id,
            correct_emoji,
            wrong_emoji,
            daily_goal,
            current_number,
            last_user_id,
            goal_reached_date,
            high_score,
            high_score_user_id,
            total_correct,
            total_resets
        ) = settings

        if not channel_id:

            embed = discord.Embed(
                title="🔢 Counting Game",
                description=(
                    "The counting game is **not configured**.\n\n"
                    "Use:\n"
                    "`/counting setup`"
                ),
                color=CRIMSON
            )

            await ctx.send(embed=embed)
            return

        channel = ctx.guild.get_channel(channel_id)

        if channel:
            channel_text = channel.mention
        else:
            channel_text = "`Channel unavailable`"

        high_score_user = None

        if high_score_user_id:
            high_score_user = ctx.guild.get_member(
                high_score_user_id
            )

        high_score_text = (
            f"**{high_score}** — "
            f"{high_score_user.mention}"
            if high_score_user
            else f"**{high_score}**"
        )

        embed = discord.Embed(
            title="🔢 Counting Game Status",
            color=CRIMSON
        )

        embed.add_field(
            name="📢 Channel",
            value=channel_text,
            inline=True
        )

        embed.add_field(
            name="🔥 Current Count",
            value=f"`{current_number}`",
            inline=True
        )

        embed.add_field(
            name="➡️ Next Number",
            value=f"`{current_number + 1}`",
            inline=True
        )

        embed.add_field(
            name="🎯 Daily Goal",
            value=(
                f"`{daily_goal}`"
                if daily_goal > 0
                else "`Disabled`"
            ),
            inline=True
        )

        embed.add_field(
            name="🏆 All-Time High",
            value=high_score_text,
            inline=True
        )

        embed.add_field(
            name="📈 Correct Counts",
            value=f"`{total_correct}`",
            inline=True
        )

        embed.add_field(
            name="💥 Total Resets",
            value=f"`{total_resets}`",
            inline=True
        )

        if last_user_id:
            member = ctx.guild.get_member(last_user_id)

            last_counter = (
                member.mention
                if member
                else f"`{last_user_id}`"
            )
        else:
            last_counter = "Nobody yet"

        embed.add_field(
            name="👤 Last Counter",
            value=last_counter,
            inline=True
        )

        embed.set_footer(
            text="Vexora • Counting Game • Developed by Potter"
        )

        await ctx.send(embed=embed)

    # ═════════════════════════════════════════════
    # LEADERBOARD
    # ═════════════════════════════════════════════

    @counting.command(
        name="leaderboard",
        description="View the counting leaderboard."
    )
    async def leaderboard(self, ctx):

        settings = get_counting_settings(ctx.guild.id)

        if not settings[0]:

            await ctx.send(
                "❌ Counting is not configured in this server."
            )
            return

        high_score = settings[7]
        high_score_user_id = settings[8]

        embed = discord.Embed(
            title="🏆 Vexora Counting Leaderboard",
            description=(
                "The current all-time server record."
            ),
            color=CRIMSON
        )

        if high_score and high_score_user_id:

            member = ctx.guild.get_member(
                high_score_user_id
            )

            user_text = (
                member.mention
                if member
                else f"`{high_score_user_id}`"
            )

            embed.add_field(
                name="🥇 #1 Record Holder",
                value=(
                    f"{user_text}\n"
                    f"🔥 **{high_score}**"
                ),
                inline=False
            )

        else:

            embed.description = (
                "No counting record has been set yet.\n\n"
                "Start counting to claim the first record! 🔥"
            )

        embed.set_footer(
            text="Vexora • Counting Game • Developed by Potter"
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Counting(bot))