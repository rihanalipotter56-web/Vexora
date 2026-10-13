import re
import time
from collections import defaultdict, deque
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands

from core.database import (
    get_automod_settings,
    set_automod_settings,
    set_automod_role,
    get_automod_words,
    add_automod_word,
    remove_automod_word,
)
from core.logger import send_log


CRIMSON = discord.Color.from_rgb(150, 25, 35)


# ═════════════════════════════════════════════
# AUTOMOD LIMITS
# ═════════════════════════════════════════════

SPAM_WINDOW = 7
SPAM_MESSAGE_LIMIT = 6

REPEAT_WINDOW = 15
REPEAT_MESSAGE_LIMIT = 3

MENTION_LIMIT = 6

PUNISHMENT_COOLDOWN = 10


# ═════════════════════════════════════════════
# SMALL HELPERS
# ═════════════════════════════════════════════

def status_text(enabled):
    return "🟢 Enabled" if enabled else "🔴 Disabled"


def toggle_text(enabled):
    return "🟢 ON" if enabled else "🔴 OFF"


# ═════════════════════════════════════════════
# ADD WORD MODAL
# ═════════════════════════════════════════════

class AddWordModal(discord.ui.Modal):

    def __init__(self, cog, guild_id):
        super().__init__(title="Add Forbidden Word")

        self.cog = cog
        self.guild_id = guild_id

        self.word = discord.ui.TextInput(
            label="Forbidden word",
            placeholder="Enter a word to block",
            required=True,
            min_length=1,
            max_length=50
        )

        self.add_item(self.word)

    async def on_submit(self, interaction):

        word = self.word.value.strip().lower()

        if not word:
            await interaction.response.send_message(
                "❌ Please enter a valid word.",
                ephemeral=True
            )
            return

        if len(word.split()) > 1:
            await interaction.response.send_message(
                "❌ Please add one word at a time.",
                ephemeral=True
            )
            return

        added = add_automod_word(
            self.guild_id,
            word
        )

        if added:
            message = (
                f"✅ Added `{word}` to the forbidden-word list."
            )
        else:
            message = (
                f"⚠️ `{word}` is already in the forbidden-word list."
            )

        await interaction.response.send_message(
            message,
            ephemeral=True
        )


# ═════════════════════════════════════════════
# REMOVE WORD MODAL
# ═════════════════════════════════════════════

class RemoveWordModal(discord.ui.Modal):

    def __init__(self, cog, guild_id):
        super().__init__(title="Remove Forbidden Word")

        self.cog = cog
        self.guild_id = guild_id

        self.word = discord.ui.TextInput(
            label="Forbidden word",
            placeholder="Enter the word to remove",
            required=True,
            min_length=1,
            max_length=50
        )

        self.add_item(self.word)

    async def on_submit(self, interaction):

        word = self.word.value.strip().lower()

        removed = remove_automod_word(
            self.guild_id,
            word
        )

        if removed:
            message = (
                f"✅ Removed `{word}` from the forbidden-word list."
            )
        else:
            message = (
                f"⚠️ `{word}` was not found in the forbidden-word list."
            )

        await interaction.response.send_message(
            message,
            ephemeral=True
        )


# ═════════════════════════════════════════════
# TIMEOUT MODAL
# ═════════════════════════════════════════════

class TimeoutModal(discord.ui.Modal):

    def __init__(self, cog, guild_id):
        super().__init__(title="AutoMod Timeout")

        self.cog = cog
        self.guild_id = guild_id

        self.duration = discord.ui.TextInput(
            label="Timeout duration in minutes",
            placeholder="Example: 5",
            required=True,
            min_length=1,
            max_length=5
        )

        self.add_item(self.duration)

    async def on_submit(self, interaction):

        try:
            minutes = int(
                self.duration.value.strip()
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Please enter a valid number.",
                ephemeral=True
            )
            return

        if minutes < 1 or minutes > 40320:

            await interaction.response.send_message(
                "❌ Duration must be between **1 and 40320 minutes**.",
                ephemeral=True
            )
            return

        set_automod_settings(
            self.guild_id,
            timeout=minutes
        )

        await interaction.response.send_message(
            f"🔇 AutoMod timeout set to **{minutes} minutes**.",
            ephemeral=True
        )


# ═════════════════════════════════════════════
# AUTOMOD VIEW
# ═════════════════════════════════════════════

class AutoModView(discord.ui.View):

    def __init__(self, cog, guild_id):

        super().__init__(timeout=300)

        self.cog = cog
        self.guild_id = guild_id

    # ═════════════════════════════════════════
    # ENABLE / DISABLE
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="Enable / Disable",
        emoji="⚡",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def toggle(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        settings = get_automod_settings(
            self.guild_id
        )

        if not settings:
            return

        enabled = bool(settings[0])

        set_automod_settings(
            self.guild_id,
            enabled=0 if enabled else 1
        )

        await self.cog.update_dashboard(
            interaction,
            self.guild_id,
            self
        )

    # ═════════════════════════════════════════
    # SPAM
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="Spam",
        emoji="🛑",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def spam(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        settings = get_automod_settings(
            self.guild_id
        )

        if not settings:
            return

        current = bool(settings[3])

        set_automod_settings(
            self.guild_id,
            spam_enabled=0 if current else 1
        )

        await self.cog.update_dashboard(
            interaction,
            self.guild_id,
            self
        )

    # ═════════════════════════════════════════
    # REPEAT
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="Repeats",
        emoji="🔁",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def repeats(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        settings = get_automod_settings(
            self.guild_id
        )

        if not settings:
            return

        current = bool(settings[4])

        set_automod_settings(
            self.guild_id,
            repeat_enabled=0 if current else 1
        )

        await self.cog.update_dashboard(
            interaction,
            self.guild_id,
            self
        )

    # ═════════════════════════════════════════
    # MENTIONS
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="Mentions",
        emoji="📢",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def mentions(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        settings = get_automod_settings(
            self.guild_id
        )

        if not settings:
            return

        current = bool(settings[5])

        set_automod_settings(
            self.guild_id,
            mention_enabled=0 if current else 1
        )

        await self.cog.update_dashboard(
            interaction,
            self.guild_id,
            self
        )

    # ═════════════════════════════════════════
    # ADD WORD
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="Add Word",
        emoji="➕",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def add_word(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            AddWordModal(
                self.cog,
                self.guild_id
            )
        )

    # ═════════════════════════════════════════
    # REMOVE WORD
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="Remove Word",
        emoji="➖",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def remove_word(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            RemoveWordModal(
                self.cog,
                self.guild_id
            )
        )

    # ═════════════════════════════════════════
    # VIEW WORDS
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="View Words",
        emoji="📋",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def view_words(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        words = get_automod_words(
            self.guild_id
        )

        if not words:

            text = (
                "📭 No forbidden words have been configured."
            )

        else:

            formatted = [
                f"`{word}`"
                for word in words
            ]

            text = " • ".join(formatted)

            if len(text) > 3900:
                text = (
                    "⚠️ Too many words to display here. "
                    "Use the database or remove some words."
                )

        embed = discord.Embed(
            title="🚫 Forbidden Words",
            description=text,
            color=CRIMSON
        )

        embed.set_footer(
            text="Vexora AutoMod • Server-specific list"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ═════════════════════════════════════════
    # TIMEOUT
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="Timeout",
        emoji="🔇",
        style=discord.ButtonStyle.primary,
        row=2
    )
    async def timeout_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            TimeoutModal(
                self.cog,
                self.guild_id
            )
        )

    # ═════════════════════════════════════════
    # REFRESH
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="Refresh",
        emoji="🔄",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def refresh(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.cog.update_dashboard(
            interaction,
            self.guild_id,
            self
        )

    # ═════════════════════════════════════════
    # STAFF ROLE SELECT
    # ═════════════════════════════════════════

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="👮 Select AutoMod staff notification role",
        min_values=0,
        max_values=1,
        row=3
    )
    async def role_select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.RoleSelect
    ):

        if select.values:

            role = select.values[0]

            set_automod_role(
                self.guild_id,
                role.id
            )

            message = (
                f"👮 Staff notification role set to "
                f"{role.mention}."
            )

        else:

            set_automod_role(
                self.guild_id,
                None
            )

            message = (
                "👮 Staff notification role cleared."
            )

        await self.cog.update_dashboard(
            interaction,
            self.guild_id,
            self
        )

    # ═════════════════════════════════════════
    # CLOSE
    # ═════════════════════════════════════════

    @discord.ui.button(
        label="Close",
        emoji="✖️",
        style=discord.ButtonStyle.secondary,
        row=4
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="🛡️ **Vexora AutoMod panel closed.**",
            embed=None,
            view=self
        )

        self.stop()


# ═════════════════════════════════════════════
# AUTOMOD COG
# ═════════════════════════════════════════════

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

        # guild_id -> user_id -> last punishment
        self.punishment_cooldowns = defaultdict(dict)

    # ═════════════════════════════════════════
    # EXEMPT USERS
    # ═════════════════════════════════════════

    def is_exempt(self, message):

        if not message.guild:
            return True

        if message.author.bot:
            return True

        if not isinstance(
            message.author,
            discord.Member
        ):
            return True

        permissions = message.author.guild_permissions

        if permissions.administrator:
            return True

        if permissions.manage_messages:
            return True

        return False

    # ═════════════════════════════════════════
    # CUSTOM WORD DETECTION
    # ═════════════════════════════════════════

    def contains_bad_word(
        self,
        content,
        forbidden_words
    ):

        if not content:
            return False

        if not forbidden_words:
            return False

        cleaned = re.sub(
            r"[^a-zA-Z0-9]+",
            " ",
            content.lower()
        )

        words = set(
            cleaned.split()
        )

        forbidden_set = {
            word.lower()
            for word in forbidden_words
        }

        return bool(
            words.intersection(
                forbidden_set
            )
        )

    # ═════════════════════════════════════════
    # COOLDOWN
    # ═════════════════════════════════════════

    def is_on_punishment_cooldown(
        self,
        guild_id,
        user_id
    ):

        last = (
            self.punishment_cooldowns
            .get(guild_id, {})
            .get(user_id)
        )

        if last is None:
            return False

        return (
            time.monotonic() - last
            < PUNISHMENT_COOLDOWN
        )

    # ═════════════════════════════════════════
    # CLEAR HISTORY
    # ═════════════════════════════════════════

    def clear_user_history(
        self,
        guild_id,
        user_id
    ):

        self.message_history[
            guild_id
        ].pop(
            user_id,
            None
        )

        self.recent_messages[
            guild_id
        ].pop(
            user_id,
            None
        )

    # ═════════════════════════════════════════
    # PUNISH
    # ═════════════════════════════════════════

    async def punish(
        self,
        message,
        reason,
        timeout_minutes,
        role_id
    ):

        if not message.guild:
            return

        member = message.author

        guild_id = message.guild.id
        user_id = member.id

        if self.is_on_punishment_cooldown(
            guild_id,
            user_id
        ):
            return

        self.punishment_cooldowns[
            guild_id
        ][user_id] = time.monotonic()

        # ─────────────────────────────────────
        # DELETE MESSAGE
        # ─────────────────────────────────────

        try:

            await message.delete()

        except (
            discord.NotFound,
            discord.Forbidden,
            discord.HTTPException
        ):
            pass

        # ─────────────────────────────────────
        # TIMEOUT
        # ─────────────────────────────────────

        timeout_success = False

        bot_member = message.guild.me

        if (
            isinstance(
                member,
                discord.Member
            )
            and bot_member
            and member != message.guild.owner
            and member != bot_member
            and member.top_role < bot_member.top_role
            and bot_member.guild_permissions.moderate_members
        ):

            try:

                await member.timeout(
                    timedelta(
                        minutes=timeout_minutes
                    ),
                    reason=(
                        f"Vexora AutoMod: {reason}"
                    )
                )

                timeout_success = True

            except (
                discord.Forbidden,
                discord.HTTPException
            ):
                pass

        # ─────────────────────────────────────
        # STAFF ROLE
        # ─────────────────────────────────────

        staff_role = None

        if role_id:

            staff_role = (
                message.guild.get_role(
                    role_id
                )
            )

        if staff_role:

            staff_mention = (
                staff_role.mention
            )

            allowed_mentions = (
                discord.AllowedMentions(
                    roles=True,
                    users=True
                )
            )

        else:

            staff_mention = ""

            allowed_mentions = (
                discord.AllowedMentions(
                    roles=False,
                    users=True
                )
            )

        # ─────────────────────────────────────
        # RESULT MESSAGE
        # ─────────────────────────────────────

        if timeout_success:

            timeout_text = (
                f"🔇 **{timeout_minutes}-minute "
                f"timeout applied.**"
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

        except (
            discord.Forbidden,
            discord.HTTPException
        ):
            pass

        # ─────────────────────────────────────
        # LOG
        # ─────────────────────────────────────

        await send_log(
            message.guild,
            "🚨 AutoMod Action",
            (
                "Vexora automatically detected "
                f"a violation from {member.mention}."
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

        self.clear_user_history(
            guild_id,
            user_id
        )

    # ═════════════════════════════════════════
    # MESSAGE LISTENER
    # ═════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):

        if self.is_exempt(message):
            return

        if not message.guild:
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

        if not enabled:
            return

        if (
            not timeout_minutes
            or timeout_minutes < 1
        ):
            timeout_minutes = 5

        guild_id = message.guild.id
        user_id = message.author.id

        now = time.monotonic()

        timestamps = (
            self.message_history[
                guild_id
            ][user_id]
        )

        recent = (
            self.recent_messages[
                guild_id
            ][user_id]
        )

        # ═════════════════════════════════════
        # FORBIDDEN WORDS
        # ═════════════════════════════════════

        forbidden_words = get_automod_words(
            guild_id
        )

        if self.contains_bad_word(
            message.content,
            forbidden_words
        ):

            await self.punish(
                message,
                "Forbidden word detected.",
                timeout_minutes,
                role_id
            )

            return

        # ═════════════════════════════════════
        # SPAM
        # ═════════════════════════════════════

        if spam_enabled:

            timestamps.append(now)

            while (
                timestamps
                and now - timestamps[0]
                > SPAM_WINDOW
            ):

                timestamps.popleft()

            if (
                len(timestamps)
                >= SPAM_MESSAGE_LIMIT
            ):

                await self.punish(
                    message,
                    "Sending messages too quickly.",
                    timeout_minutes,
                    role_id
                )

                return

        # ═════════════════════════════════════
        # REPEATED MESSAGES
        # ═════════════════════════════════════

        if repeat_enabled:

            content = (
                message.content
                .strip()
                .lower()
            )

            if content:

                recent.append(
                    (
                        content,
                        now
                    )
                )

                while (
                    recent
                    and now - recent[0][1]
                    > REPEAT_WINDOW
                ):

                    recent.popleft()

                same_count = sum(
                    1
                    for text, timestamp
                    in recent
                    if text == content
                )

                if (
                    same_count
                    >= REPEAT_MESSAGE_LIMIT
                ):

                    await self.punish(
                        message,
                        "Repeated messages detected.",
                        timeout_minutes,
                        role_id
                    )

                    return

        # ═════════════════════════════════════
        # MENTION SPAM
        # ═════════════════════════════════════

        if mention_enabled:

            mention_count = (
                len(message.mentions)
                + len(message.role_mentions)
            )

            if (
                mention_count
                >= MENTION_LIMIT
            ):

                await self.punish(
                    message,
                    "Too many users or roles were mentioned.",
                    timeout_minutes,
                    role_id
                )

                return

    # ═════════════════════════════════════════
    # /AUTOMOD
    # ═════════════════════════════════════════

    @app_commands.command(
        name="automod",
        description="Configure Vexora AutoMod."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    @app_commands.guild_only()
    async def automod(
        self,
        interaction: discord.Interaction
    ):

        settings = get_automod_settings(
            interaction.guild.id
        )

        embed = self.build_dashboard(
            interaction.guild,
            settings
        )

        view = AutoModView(
            self,
            interaction.guild.id
        )

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

    # ═════════════════════════════════════════
    # DASHBOARD EMBED
    # ═════════════════════════════════════════

    def build_dashboard(
        self,
        guild,
        settings
    ):

        (
            enabled,
            role_id,
            timeout_minutes,
            spam_enabled,
            repeat_enabled,
            mention_enabled
        ) = settings

        role = (
            guild.get_role(role_id)
            if role_id
            else None
        )

        role_text = (
            role.mention
            if role
            else "Not configured"
        )

        words = get_automod_words(
            guild.id
        )

        word_count = len(words)

        embed = discord.Embed(
            title="🛡️ Vexora AutoMod",
            description=(
                "Advanced automatic protection "
                "for your server."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="⚡ Status",
            value=status_text(enabled),
            inline=True
        )

        embed.add_field(
            name="🔇 Timeout",
            value=f"`{timeout_minutes} minutes`",
            inline=True
        )

        embed.add_field(
            name="👮 Staff Role",
            value=role_text,
            inline=True
        )

        embed.add_field(
            name="🛡️ Protection",
            value=(
                f"🛑 Spam: {toggle_text(spam_enabled)}\n"
                f"🔁 Repeats: {toggle_text(repeat_enabled)}\n"
                f"📢 Mentions: {toggle_text(mention_enabled)}"
            ),
            inline=False
        )

        embed.add_field(
            name="🚫 Forbidden Words",
            value=(
                f"**{word_count}** word"
                f"{'s' if word_count != 1 else ''} configured"
            ),
            inline=False
        )

        embed.set_footer(
            text="Vexora AutoMod • Developed by Potter"
        )

        return embed

    # ═════════════════════════════════════════
    # UPDATE DASHBOARD
    # ═════════════════════════════════════════

    async def update_dashboard(
        self,
        interaction,
        guild_id,
        view
    ):

        settings = get_automod_settings(
            guild_id
        )

        guild = interaction.guild

        embed = self.build_dashboard(
            guild,
            settings
        )

        if interaction.response.is_done():

            await interaction.edit_original_response(
                embed=embed,
                view=view
            )

        else:

            await interaction.response.edit_message(
                embed=embed,
                view=view
            )


# ═════════════════════════════════════════════
# SETUP
# ═════════════════════════════════════════════

async def setup(bot):

    await bot.add_cog(
        AutoMod(bot)
    )