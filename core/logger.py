import discord
from datetime import datetime, timezone


CRIMSON = discord.Color.from_rgb(150, 25, 35)


# =========================
# AUDIT LOG HELPER
# =========================

async def get_audit_executor(
    guild: discord.Guild,
    action: discord.AuditLogAction,
    target_id: int | None = None
):
    """
    Finds the Discord user who performed an action
    through the server's Audit Log.
    """

    try:
        async for entry in guild.audit_logs(
            limit=8,
            action=action
        ):
            # Ignore old entries
            if entry.created_at:
                age = (
                    datetime.now(timezone.utc)
                    - entry.created_at
                ).total_seconds()

                if age > 15:
                    continue

            # Match target when possible
            if target_id is not None:

                entry_target = entry.target

                if not entry_target:
                    continue

                if getattr(entry_target, "id", None) != target_id:
                    continue

            return entry.user

    except discord.Forbidden:
        # Bot does not have View Audit Log
        return None

    except discord.HTTPException:
        return None

    except Exception as error:
        print(f"⚠️ Audit log lookup failed: {error}")
        return None

    return None


def executor_text(executor):
    if executor:
        return f"{executor.mention}\n`{executor.id}`"

    return "Unknown / Audit Log unavailable"


# =========================
# MOD LOG CHANNEL
# =========================

async def get_mod_log_channel(guild: discord.Guild):

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
        guild.default_role: discord.PermissionOverwrite(
            view_channel=False
        ),
        bot_member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            embed_links=True
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
            f"❌ Vexora cannot create mod-logs in {guild.name}"
        )

        return None

    except discord.HTTPException as error:

        print(
            f"❌ Failed to create mod-logs: {error}"
        )

        return None


# =========================
# GENERIC LOG
# =========================

async def send_log(
    guild: discord.Guild,
    title: str,
    description: str,
    *,
    color=CRIMSON,
    fields=None
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

    embed.set_footer(
        text="Vexora • Logging System"
    )

    try:

        await channel.send(embed=embed)

    except discord.Forbidden:

        print(
            f"❌ Cannot send logs in #{channel.name}"
        )

    except discord.HTTPException as error:

        print(
            f"❌ Log message failed: {error}"
        )


# =========================
# MODERATION LOG
# =========================

async def send_mod_log(
    guild: discord.Guild,
    action: str,
    target,
    moderator: discord.Member,
    reason: str
):

    await send_log(
        guild,
        "🛡️ Vexora Moderation Log",
        f"**Action:** {action}",
        fields=[
            (
                "👤 Target",
                f"{target.mention if hasattr(target, 'mention') else target}\n"
                f"`{target.id}`",
                True
            ),
            (
                "🛡️ Moderator",
                f"{moderator.mention}\n"
                f"`{moderator.id}`",
                True
            ),
            (
                "📝 Reason",
                reason or "No reason provided",
                False
            )
        ]
    )