import re
from datetime import datetime, timezone

import discord
from discord.ext import commands

from core.database import (
    get_counting_settings,
    set_counting_settings,
    update_counting_progress,
    reset_counting_progress
)
from core.logger import send_log


CRIMSON = discord.Color.from_rgb(150, 25, 35)


# =========================================================
# EMOJI PARSER
# =========================================================

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
        emoji = discord.PartialEmoji(
            name=match.group("name"),
            id=int(match.group("id")),
            animated=bool(match.group("animated"))
        )

        return emoji

    except (TypeError, ValueError):
        return None


# =========================================================
# COUNTING COG
# =========================================================

class Counting(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # =====================================================
    # MAIN COUNTING ENGINE
    # =====================================================

    @commands.Cog.listener()
    async def on_message(self, message):

        # Ignore DMs
        if not message.guild:
            return

        # Ignore bots
        if message.author.bot:
            return

        settings = get_counting_settings(
            message.guild.id
        )

        if not settings:
            return

        (
            channel_id,
            correct_emoji,
            wrong_emoji,
            daily_goal,
            current_number,
            last_user_id,
            goal_reached_date
        ) = settings

        # Counting not configured
        if not channel_id:
            return

        # Wrong channel
        if message.channel.id != channel_id:
            return

        # Only accept plain positive integers
        content = message.content.strip()

        if not content.isdigit():
            return

        try:
            number = int(content)

        except ValueError:
            return

        # Protect against absurdly huge numbers
        if number > 10**18:
            return

        today = datetime.now(
            timezone.utc
        ).date().isoformat()

        # -------------------------------------------------
        # New day
        # -------------------------------------------------

        if goal_reached_date and goal_reached_date != today:

            current_number = 0
            last_user_id = None
            goal_reached_date = None

        # -------------------------------------------------
        # Expected number
        # -------------------------------------------------

        expected = current_number + 1

        # -------------------------------------------------
        # WRONG NUMBER
        # -------------------------------------------------

        if number != expected:

            await self.handle_failure(
                message,
                wrong_emoji
            )

            reset_counting_progress(
                message.guild.id
            )

            return

        # -------------------------------------------------
        # SAME USER TWICE
        # -------------------------------------------------

        if last_user_id == message.author.id:

            await self.handle_failure(
                message,
                wrong_emoji
            )

            reset_counting_progress(
                message.guild.id
            )

            return

        # -------------------------------------------------
        # CORRECT NUMBER
        # -------------------------------------------------

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

        update_counting_progress(
            message.guild.id,
            current_number,
            message.author.id,
            goal_reached_date
        )

        # -------------------------------------------------
        # Correct reaction
        # -------------------------------------------------

        emoji = parse_custom_emoji(
            correct_emoji
        )

        try:

            if emoji:

                await message.add_reaction(
                    emoji
                )

            else:

                await message.add_reaction(
                    "✅"
                )

        except (
            discord.Forbidden,
            discord.HTTPException
        ):
            pass

        # -------------------------------------------------
        # Daily goal reached
        # -------------------------------------------------

        if goal_reached:

            embed = discord.Embed(
                title="🏆 Daily Counting Goal Reached!",
                description=(
                    f"{message.guild.default_role.mention}\n\n"
                    f"🎯 Today's goal of **{daily_goal}** "
                    f"has been reached!\n\n"
                    f"🔥 Current count: **{current_number}**\n"
                    f"👑 Reached by: {message.author.mention}"
                ),
                color=discord.Color.gold()
            )

            embed.set_footer(
                text="Vexora • Counting Game"
            )

            try:

                await message.channel.send(
                    embed=embed,
                    allowed_mentions=discord.AllowedMentions(
                        everyone=False,
                        roles=False,
                        users=True
                    )
                )

            except discord.HTTPException:
                pass

    # =====================================================
    # FAILURE HANDLER
    # =====================================================

    async def handle_failure(
        self,
        message,
        wrong_emoji
    ):

        emoji = parse_custom_emoji(
            wrong_emoji
        )

        try:

            if emoji:

                await message.add_reaction(
                    emoji
                )

            else:

                await message.add_reaction(
                    "❌"
                )

        except (
            discord.Forbidden,
            discord.HTTPException
        ):
            pass

        # Small reset notice
        embed = discord.Embed(
            title="💥 Counting Reset!",
            description=(
                f"{message.author.mention} broke the count.\n\n"
                "🔄 The next number is **1** again."
            ),
            color=CRIMSON
        )

        embed.set_footer(
            text="Vexora • Counting Game"
        )

        try:

            await message.channel.send(
                embed=embed,
                delete_after=6
            )

        except discord.HTTPException:
            pass

    # =====================================================
    # COUNTING SETUP
    # =====================================================

    @commands.hybrid_group(
        name="counting",
        description="Manage Vexora's counting game."
    )
    @commands.guild_only()
    async def counting(self, ctx):

        if ctx.invoked_subcommand is None:

            await self.status(
                ctx
            )

    # =====================================================
    # SETUP
    # =====================================================

    @counting.command(
        name="setup",
        description="Configure the counting game."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    @commands.bot_has_permissions(
        add_reactions=True,
        send_messages=True,
        embed_links=True
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
                "❌ Daily goal cannot be negative.",
                ephemeral=True
            )
            return

        # -------------------------------------------------
        # Validate emojis
        # -------------------------------------------------

        correct = parse_custom_emoji(
            correct_emoji
        )

        wrong = parse_custom_emoji(
            wrong_emoji
        )

        if correct_emoji and not correct:

            await ctx.send(
                "❌ Invalid correct emoji.\n\n"
                "Use a server custom emoji like:\n"
                "`<:correct:123456789>`",
                ephemeral=True
            )
            return

        if wrong_emoji and not wrong:

            await ctx.send(
                "❌ Invalid wrong emoji.\n\n"
                "Use a server custom emoji like:\n"
                "`<:wrong:123456789>`",
                ephemeral=True
            )
            return

        # -------------------------------------------------
        # Ensure emojis belong to this server
        # -------------------------------------------------

        for emoji in (correct, wrong):

            if emoji and emoji.guild_id:

                if emoji.guild_id != ctx.guild.id:

                    await ctx.send(
                        "❌ Please use custom emojis "
                        "from this server.",
                        ephemeral=True
                    )
                    return

        set_counting_settings(
            ctx.guild.id,
            channel_id=channel.id,
            correct_emoji=(
                str(correct)
                if correct
                else None
            ),
            wrong_emoji=(
                str(wrong)
                if wrong
                else None
            ),
            daily_goal=daily_goal
        )

        reset_counting_progress(
            ctx.guild.id
        )

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
            value=(
                str(correct)
                if correct
                else "✅"
            ),
            inline=True
        )

        embed.add_field(
            name="❌ Wrong / Reset",
            value=(
                str(wrong)
                if wrong
                else "❌"
            ),
            inline=True
        )

        embed.add_field(
            name="📜 Rules",
            value=(
                "• Numbers must be consecutive.\n"
                "• The same person cannot count twice.\n"
                "• A mistake resets the count to `0`.\n"
                "• The next correct number is `1`."
            ),
            inline=False
        )

        embed.set_footer(
            text="Vexora • Counting Game • Developed by Potter"
        )

        await ctx.send(
            embed=embed
        )

    # =====================================================
    # SET DAILY GOAL
    # =====================================================

    @counting.command(
        name="goal",
        description="Set or change the daily counting goal."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def goal(
        self,
        ctx,
        goal: int
    ):

        if goal < 0:

            await ctx.send(
                "❌ Goal cannot be negative.",
                ephemeral=True
            )
            return

        set_counting_settings(
            ctx.guild.id,
            daily_goal=goal
        )

        if goal == 0:

            await ctx.send(
                "🎯 Daily counting goal **disabled**.",
                ephemeral=True
            )
            return

        await ctx.send(
            f"🎯 Daily counting goal set to **{goal}**.",
            ephemeral=True
        )

    # =====================================================
    # RESET
    # =====================================================

    @counting.command(
        name="reset",
        description="Reset the current counting score."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def reset(
        self,
        ctx
    ):

        reset_counting_progress(
            ctx.guild.id
        )

        embed = discord.Embed(
            title="🔄 Counting Reset",
            description=(
                "The counting game has been reset.\n\n"
                "The next correct number is **1**."
            ),
            color=CRIMSON
        )

        embed.set_footer(
            text="Vexora • Counting Game"
        )

        await ctx.send(
            embed=embed
        )

    # =====================================================
    # STATUS
    # =====================================================

    async def status(
        self,
        ctx
    ):

        settings = get_counting_settings(
            ctx.guild.id
        )

        (
            channel_id,
            correct_emoji,
            wrong_emoji,
            daily_goal,
            current_number,
            last_user_id,
            goal_reached_date
        ) = settings

        if not channel_id:

            embed = discord.Embed(
                title="🔢 Counting Game",
                description=(
                    "The counting game is **not configured**.\n\n"
                    "A server administrator can use:\n"
                    "`/counting setup`"
                ),
                color=CRIMSON
            )

            await ctx.send(
                embed=embed
            )
            return

        channel = ctx.guild.get_channel(
            channel_id
        )

        embed = discord.Embed(
            title="🔢 Counting Game Status",
            color=CRIMSON
        )

        embed.add_field(
            name="📢 Channel",
            value=(
                channel.mention
                if channel
                else "`Channel unavailable`"
            ),
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
            name="📊 Progress",
            value=(
                f"`{current_number} / {daily_goal}`"
                if daily_goal > 0
                else "`No goal set`"
            ),
            inline=True
        )

        if last_user_id:

            member = ctx.guild.get_member(
                last_user_id
            )

            last_user_text = (
                member.mention
                if member
                else f"`{last_user_id}`"
            )

        else:

            last_user_text = "Nobody yet"

        embed.add_field(
            name="👤 Last Counter",
            value=last_user_text,
            inline=True
        )

        embed.set_footer(
            text="Vexora • Counting Game • Developed by Potter"
        )

        await ctx.send(
            embed=embed
        )


async def setup(bot):

    await bot.add_cog(
        Counting(bot)
    )