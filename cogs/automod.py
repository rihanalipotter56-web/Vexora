import re
import time
from collections import defaultdict, deque
from datetime import timedelta

import discord
from discord.ext import commands

from core.database import get_automod_settings
from core.logger import send_log


CRIMSON = discord.Color.from_rgb(150, 25, 35)


# =========================
# DEFAULT BLOCKED WORDS
# =========================

DEFAULT_BAD_WORDS = {
    "fuck",
    "fucking",
    "fucked",
    "sex",
}


class AutoMod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # guild_id -> user_id -> timestamps
        self.message_history = defaultdict(
            lambda: defaultdict(deque)
        )

        # guild_id -> user_id -> repeated messages
        self.recent_messages = defaultdict(
            lambda: defaultdict(deque)
        )

    # =========================
    # EXEMPT USERS
    # =========================

    def is_exempt(self, message):

        if not message.guild:
            return True

        if message.author.bot:
            return True

        member = message.author

        if member.guild_permissions.administrator:
            return True

        if member.guild_permissions.manage_messages:
            return True

        return False

    # =========================
    # BAD WORD DETECTION
    # =========================

    def contains_bad_word(self, content):

        if not content:
            return False

        # Convert punctuation into spaces.
        # Example:
        # "fuck!" -> "fuck"
        # "sex." -> "sex"
        cleaned = re.sub(
            r"[^a-zA-Z0-9]+",
            " ",
            content.lower()
        )

        words = set(cleaned.split())

        return bool(words.intersection(DEFAULT_BAD_WORDS))

    # =========================
    # PUNISHMENT
    # =========================

    async def punish(
        self,
        message,
        reason,
        timeout_minutes,
        role_id
    ):

        member = message.author

        # -------------------------
        # Delete message
        # -------------------------

        try:
            await message.delete()

        except (
            discord.NotFound,
            discord.Forbidden,
            discord.HTTPException
        ):
            pass

        # -------------------------
        # Timeout
        # -------------------------

        timeout_success = False

        if (
            isinstance(member, discord.Member)
            and message.guild.me
            and member != message.guild.owner
            and member.top_role < message.guild.me.top_role
        ):

            try:

                await member.timeout(
                    timedelta(minutes=timeout_minutes),
                    reason=f"Vexora AutoMod: {reason}"
                )

                timeout_success = True

            except (
                discord.Forbidden,
                discord.HTTPException
            ):
                pass

        # -------------------------
        # Staff role
        # -------------------------

        staff_role = None

        if role_id:
            staff_role = message.guild.get_role(role_id)

        if staff_role:

            staff_mention = staff_role.mention

            allowed_mentions = discord.AllowedMentions(
                roles=True
            )

        else:

            staff_mention = ""

            allowed_mentions = discord.AllowedMentions(
                roles=False
            )

        # -------------------------
        # Result message
        # -------------------------

        if timeout_success:

            timeout_text = (
                f"🔇 **{timeout_minutes}-minute timeout applied.**"
            )

        else:

            timeout_text = (
                "⚠️ **Timeout could not be applied.**"
            )

        notification = (
            f"{staff_mention}\n"
            if staff_mention
            else ""
        )

        try:

            await message.channel.send(
                f"{notification}"
                f"🚨 **Vexora AutoMod**\n"
                f"👤 **User:** {member.mention}\n"
                f"⚠️ **Reason:** {reason}\n"
                f"{timeout_text}",
                allowed_mentions=allowed_mentions,
                delete_after=8
            )

        except discord.HTTPException:
            pass

        # -------------------------
        # Mod log
        # -------------------------

        await send_log(
            message.guild,
            "🚨 AutoMod Action",
            (
                f"Vexora automatically detected "
                f"an issue from {member.mention}."
            ),
            color=CRIMSON,
            fields=[
                (
                    "👤 User",
                    f"{member}\n`{member.id}`",
                    True
                ),
                (
                    "📢 Channel",
                    message.channel.mention,
                    True
                ),
                (
                    "⚠️ Reason",
                    reason,
                    False
                ),
                (
                    "🔇 Punishment",
                    (
                        f"{timeout_minutes}-minute timeout"
                        if timeout_success
                        else "Timeout failed"
                    ),
                    True
                ),
                (
                    "👮 Staff Notified",
                    (
                        staff_role.mention
                        if staff_role
                        else "No role configured"
                    ),
                    True
                )
            ]
        )

    # =========================
    # MESSAGE LISTENER
    # =========================

    @commands.Cog.listener()
    async def on_message(self, message):

        if self.is_exempt(message):
            return

        settings = get_automod_settings(
            message.guild.id
        )

        if not settings:
            return

        (
            enabled,
            role_id,
            timeout_minutes,
            spam_enabled,
            repeat_enabled,
            mention_enabled
        ) = settings

        # -------------------------
        # AutoMod disabled
        # -------------------------

        if not enabled:
            return

        # Safety fallback
        if not timeout_minutes or timeout_minutes < 1:
            timeout_minutes = 5

        guild_id = message.guild.id
        user_id = message.author.id

        now = time.monotonic()

        timestamps = (
            self.message_history[guild_id][user_id]
        )

        recent = (
            self.recent_messages[guild_id][user_id]
        )

        # =========================
        # BAD WORD FILTER
        # =========================

        if self.contains_bad_word(message.content):

            await self.punish(
                message,
                "Blocked word detected.",
                timeout_minutes,
                role_id
            )

            timestamps.clear()
            recent.clear()

            return

        # =========================
        # SPAM DETECTION
        # =========================

        if spam_enabled:

            timestamps.append(now)

            while (
                timestamps
                and now - timestamps[0] > 7
            ):
                timestamps.popleft()

            if len(timestamps) >= 6:

                await self.punish(
                    message,
                    "Sending messages too quickly.",
                    timeout_minutes,
                    role_id
                )

                timestamps.clear()
                recent.clear()

                return

        # =========================
        # REPEATED MESSAGE DETECTION
        # =========================

        if repeat_enabled:

            content = (
                message.content
                .strip()
                .lower()
            )

            if content:

                recent.append(
                    (content, now)
                )

                while (
                    recent
                    and now - recent[0][1] > 15
                ):
                    recent.popleft()

                same_count = sum(
                    1
                    for text, timestamp in recent
                    if text == content
                )

                if same_count >= 3:

                    await self.punish(
                        message,
                        "Repeated messages detected.",
                        timeout_minutes,
                        role_id
                    )

                    recent.clear()

                    return

        # =========================
        # MENTION SPAM
        # =========================

        if mention_enabled:

            mention_count = (
                len(message.mentions)
                + len(message.role_mentions)
            )

            if mention_count >= 6:

                await self.punish(
                    message,
                    "Too many users or roles were mentioned.",
                    timeout_minutes,
                    role_id
                )

                return


# =========================
# SETUP
# =========================

async def setup(bot):

    await bot.add_cog(
        AutoMod(bot)
    )