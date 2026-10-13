import asyncio
from datetime import datetime, timezone

import discord


# ═════════════════════════════════════════════════════════════
# VEXORA LOG COLORS
# ═════════════════════════════════════════════════════════════

HIGH = discord.Color.from_rgb(150, 25, 35)       # 🔴 #961923
MEDIUM = discord.Color.from_rgb(241, 196, 15)    # 🟡
LOW = discord.Color.from_rgb(46, 204, 113)       # 🟢

CRIMSON = HIGH


# ═════════════════════════════════════════════════════════════
# AUDIT LOG EXECUTOR
# ═════════════════════════════════════════════════════════════

async def get_audit_executor(
    guild,
    action,
    target_id=None,
    retries=2
):
    if not guild:
        return None

    for attempt in range(retries + 1):

        try:

            async for entry in guild.audit_logs(
                limit=10,
                action=action
            ):

                if entry.created_at:

                    age = (
                        datetime.now(timezone.utc)
                        - entry.created_at
                    ).total_seconds()

                    if age > 20:
                        continue

                if target_id is not None:

                    entry_target = entry.target

                    if not entry_target:
                        continue

                    if getattr(
                        entry_target,
                        "id",
                        None
                    ) != target_id:
                        continue

                return entry.user

        except discord.Forbidden:

            return None

        except discord.HTTPException:
            pass

        except Exception as error:

            print(
                f"⚠️ Audit log lookup failed: {error}"
            )

        if attempt < retries:
            await asyncio.sleep(1)

    return None


def executor_text(executor):

    if executor:

        return (
            f"{executor.mention}\n"
            f"`{executor.id}`"
        )

    return "Unknown / Audit Log unavailable"


# ═════════════════════════════════════════════════════════════
# MOD LOG CHANNEL
# ═════════════════════════════════════════════════════════════

async def get_mod_log_channel(guild):

    if not guild:
        return None

    channel = discord.utils.get(
        guild.text_channels,
        name="mod-logs"
    )

    if channel:
        return channel

    bot_member = guild.me

    if not bot_member:
        return None

    overwrites = {

        guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),

        bot_member:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                embed_links=True,
                read_message_history=True
            )
    }

    try:

        channel = await guild.create_text_channel(
            "mod-logs",
            overwrites=overwrites,
            reason="Vexora moderation log setup"
        )

        return channel

    except discord.Forbidden:

        print(
            f"❌ Vexora cannot create mod-logs "
            f"in {guild.name}"
        )

        return None

    except discord.HTTPException as error:

        print(
            f"❌ Failed to create mod-logs: {error}"
        )

        return None


# ═════════════════════════════════════════════════════════════
# GENERIC LOG SENDER
# ═════════════════════════════════════════════════════════════

async def send_log(
    guild,
    title,
    description,
    *,
    color=CRIMSON,
    fields=None,
    thumbnail=None
):

    channel = await get_mod_log_channel(guild)

    if not channel:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )

    if fields:

        for name, value, inline in fields:

            embed.add_field(
                name=name,
                value=value,
                inline=inline
            )

    if thumbnail:

        try:
            embed.set_thumbnail(
                url=thumbnail
            )

        except Exception:
            pass

    embed.set_footer(
        text="Vexora • Logging System"
    )

    try:

        await channel.send(
            embed=embed
        )

    except discord.Forbidden:

        print(
            f"❌ Cannot send logs in "
            f"#{channel.name}"
        )

    except discord.HTTPException as error:

        print(
            f"❌ Log message failed: {error}"
        )


# ═════════════════════════════════════════════════════════════
# MODERATION LOG
# ═════════════════════════════════════════════════════════════

async def send_mod_log(
    guild,
    action,
    target,
    moderator,
    reason=None
):

    action_lower = str(action).lower().strip()

    # ─────────────────────────────────────────────────────────
    # 🔴 HIGH SEVERITY
    # ─────────────────────────────────────────────────────────

    high_actions = {
        "ban",
        "banned",

        "kick",
        "kicked",

        "timeout",
        "timed out",

        "mute",
        "muted",

        "warn",
        "warned",

        "purge",
        "purged",

        "softban",
        "softbanned"
    }

    # ─────────────────────────────────────────────────────────
    # 🟢 LOW SEVERITY
    # ─────────────────────────────────────────────────────────

    low_actions = {
        "unban",
        "unbanned",

        "unmute",
        "unmuted",

        "untimeout",
        "untimeouted",

        "unwarn",
        "unwarned"
    }

    if action_lower in high_actions:

        color = HIGH
        icon = "🔴"

    elif action_lower in low_actions:

        color = LOW
        icon = "🟢"

    else:

        # Unknown moderation action
        # defaults to Vexora crimson
        color = HIGH
        icon = "🔴"

    target_text = (
        f"{target.mention}\n`{target.id}`"
        if hasattr(target, "mention")
        else str(target)
    )

    moderator_text = (
        f"{moderator.mention}\n`{moderator.id}`"
        if moderator
        else "Unknown"
    )

    await send_log(
        guild,

        f"{icon} Vexora Moderation Log",

        f"**Action:** `{action}`",

        color=color,

        fields=[
            (
                "👤 Target",
                target_text,
                True
            ),
            (
                "🛡️ Moderator",
                moderator_text,
                True
            ),
            (
                "📝 Reason",
                reason or "No reason provided",
                False
            )
        ]
    )


# ═════════════════════════════════════════════════════════════
# MEMBER JOIN
# ═════════════════════════════════════════════════════════════

async def send_member_join_log(
    guild,
    member
):

    await send_log(
        guild,

        "📥 Member Joined",

        f"{member.mention} joined the server.",

        color=LOW,

        fields=[
            (
                "👤 Member",
                f"{member}\n`{member.id}`",
                True
            ),
            (
                "👥 Member Count",
                str(guild.member_count),
                True
            )
        ],

        thumbnail=member.display_avatar.url
    )


# ═════════════════════════════════════════════════════════════
# MEMBER LEAVE
# ═════════════════════════════════════════════════════════════

async def send_member_leave_log(
    guild,
    member
):

    await send_log(
        guild,

        "📤 Member Left",

        f"**{member}** left the server.",

        color=LOW,

        fields=[
            (
                "👤 Member",
                f"{member}\n`{member.id}`",
                True
            )
        ],

        thumbnail=member.display_avatar.url
    )


# ═════════════════════════════════════════════════════════════
# MESSAGE DELETE
# ═════════════════════════════════════════════════════════════

async def send_message_delete_log(
    guild,
    message
):

    content = (
        message.content
        or "*No text content*"
    )

    if len(content) > 1000:
        content = content[:997] + "..."

    await send_log(
        guild,

        "🗑️ Message Deleted",

        (
            f"A message was deleted in "
            f"{message.channel.mention}."
        ),

        color=HIGH,

        fields=[
            (
                "👤 Author",
                f"{message.author.mention}\n"
                f"`{message.author.id}`",
                True
            ),
            (
                "📢 Channel",
                message.channel.mention,
                True
            ),
            (
                "📝 Content",
                content,
                False
            )
        ]
    )


# ═════════════════════════════════════════════════════════════
# MESSAGE EDIT
# ═════════════════════════════════════════════════════════════

async def send_message_edit_log(
    guild,
    before,
    after
):

    old_content = (
        before.content
        or "*Empty*"
    )

    new_content = (
        after.content
        or "*Empty*"
    )

    if len(old_content) > 700:
        old_content = old_content[:697] + "..."

    if len(new_content) > 700:
        new_content = new_content[:697] + "..."

    await send_log(
        guild,

        "✏️ Message Edited",

        (
            f"A message was edited in "
            f"{before.channel.mention}."
        ),

        color=MEDIUM,

        fields=[
            (
                "👤 Author",
                f"{before.author.mention}\n"
                f"`{before.author.id}`",
                True
            ),
            (
                "📢 Channel",
                before.channel.mention,
                True
            ),
            (
                "⬅️ Before",
                old_content,
                False
            ),
            (
                "➡️ After",
                new_content,
                False
            )
        ]
    )


# ═════════════════════════════════════════════════════════════
# CHANNEL LOG
# ═════════════════════════════════════════════════════════════

async def send_channel_log(
    guild,
    action,
    channel,
    executor=None
):

    action_lower = str(action).lower()

    if "delete" in action_lower:

        color = HIGH
        icon = "🗑️"

    else:

        color = MEDIUM
        icon = "📁"

    await send_log(
        guild,

        f"{icon} Channel {action}",

        f"**#{channel.name}** was {action.lower()}.",

        color=color,

        fields=[
            (
                "📢 Channel",
                f"{channel.name}\n`{channel.id}`",
                True
            ),
            (
                "📂 Type",
                str(channel.type),
                True
            ),
            (
                "🛡️ Executor",
                executor_text(executor),
                True
            )
        ]
    )


# ═════════════════════════════════════════════════════════════
# ROLE LOG
# ═════════════════════════════════════════════════════════════

async def send_role_log(
    guild,
    action,
    role,
    executor=None
):

    action_lower = str(action).lower()

    if "delete" in action_lower:

        color = HIGH
        icon = "🗑️"

    else:

        color = MEDIUM
        icon = "🎭"

    await send_log(
        guild,

        f"{icon} Role {action}",

        f"**{role.name}** was {action.lower()}.",

        color=color,

        fields=[
            (
                "🎭 Role",
                f"{role.name}\n`{role.id}`",
                True
            ),
            (
                "🛡️ Executor",
                executor_text(executor),
                True
            )
        ]
    )


# ═════════════════════════════════════════════════════════════
# MEMBER UPDATE LOG
# ═════════════════════════════════════════════════════════════

async def send_member_update_log(
    guild,
    member,
    changes,
    executor=None,
    color=MEDIUM
):

    await send_log(
        guild,

        "👤 Member Updated",

        f"{member.mention} was updated.",

        color=color,

        fields=[
            (
                "👤 Member",
                f"{member}\n`{member.id}`",
                True
            ),
            (
                "🛡️ Changed By",
                executor_text(executor),
                True
            ),
            (
                "📝 Changes",
                "\n".join(changes),
                False
            )
        ]
    )


# ═════════════════════════════════════════════════════════════
# GUILD UPDATE LOG
# ═════════════════════════════════════════════════════════════

async def send_guild_update_log(
    guild,
    changes,
    executor=None
):

    await send_log(
        guild,

        "🏠 Server Updated",

        (
            f"**{guild.name}** "
            f"server settings were changed."
        ),

        color=MEDIUM,

        fields=[
            (
                "🛡️ Changed By",
                executor_text(executor),
                True
            ),
            (
                "📝 Changes",
                "\n".join(changes),
                False
            )
        ]
    )