import discord
from discord.ext import commands

from core.logger import (
    send_log,
    get_audit_executor,
    executor_text
)


# ═════════════════════════════════════════════════════════════
# VEXORA LOG COLORS
# ═════════════════════════════════════════════════════════════

HIGH = discord.Color.from_rgb(150, 25, 35)       # 🔴 #961923
MEDIUM = discord.Color.from_rgb(241, 196, 15)   # 🟡 Yellow
LOW = discord.Color.from_rgb(46, 204, 113)       # 🟢 Green


class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ═════════════════════════════════════════════════════════
    # MEMBER JOIN
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_member_join(self, member):

        await send_log(
            member.guild,
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
                    str(member.guild.member_count),
                    True
                )
            ],
            thumbnail=member.display_avatar.url
        )

    # ═════════════════════════════════════════════════════════
    # MEMBER LEAVE
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        await send_log(
            member.guild,
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

    # ═════════════════════════════════════════════════════════
    # MESSAGE DELETE 🔴
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if not message.guild:
            return

        if message.author.bot:
            return

        content = message.content or "*No text content*"

        if len(content) > 1000:
            content = content[:997] + "..."

        await send_log(
            message.guild,
            "🗑️ Message Deleted",
            f"A message was deleted in {message.channel.mention}.",
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

    # ═════════════════════════════════════════════════════════
    # MESSAGE EDIT 🟡
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if not before.guild:
            return

        if before.author.bot:
            return

        if before.content == after.content:
            return

        old_content = before.content or "*Empty*"
        new_content = after.content or "*Empty*"

        if len(old_content) > 700:
            old_content = old_content[:697] + "..."

        if len(new_content) > 700:
            new_content = new_content[:697] + "..."

        await send_log(
            before.guild,
            "✏️ Message Edited",
            f"A message was edited in {before.channel.mention}.",
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

    # ═════════════════════════════════════════════════════════
    # BAN 🔴
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):

        executor = await get_audit_executor(
            guild,
            discord.AuditLogAction.ban,
            user.id
        )

        await send_log(
            guild,
            "🔨 Member Banned",
            f"**{user}** was banned.",
            color=HIGH,
            fields=[
                (
                    "👤 User",
                    f"{user}\n`{user.id}`",
                    True
                ),
                (
                    "🛡️ Banned By",
                    executor_text(executor),
                    True
                )
            ]
        )

    # ═════════════════════════════════════════════════════════
    # UNBAN 🟢
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):

        executor = await get_audit_executor(
            guild,
            discord.AuditLogAction.unban,
            user.id
        )

        await send_log(
            guild,
            "🔓 Member Unbanned",
            f"**{user}** was unbanned.",
            color=LOW,
            fields=[
                (
                    "👤 User",
                    f"{user}\n`{user.id}`",
                    True
                ),
                (
                    "🛡️ Unbanned By",
                    executor_text(executor),
                    True
                )
            ]
        )

    # ═════════════════════════════════════════════════════════
    # CHANNEL CREATE 🟡
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):

        executor = await get_audit_executor(
            channel.guild,
            discord.AuditLogAction.channel_create,
            channel.id
        )

        await send_log(
            channel.guild,
            "📁 Channel Created",
            f"{channel.mention} was created.",
            color=MEDIUM,
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
                    "🛡️ Created By",
                    executor_text(executor),
                    True
                )
            ]
        )

    # ═════════════════════════════════════════════════════════
    # CHANNEL DELETE 🔴
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        executor = await get_audit_executor(
            channel.guild,
            discord.AuditLogAction.channel_delete,
            channel.id
        )

        await send_log(
            channel.guild,
            "🗑️ Channel Deleted",
            f"**#{channel.name}** was deleted.",
            color=HIGH,
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
                    "🛡️ Deleted By",
                    executor_text(executor),
                    True
                )
            ]
        )

    # ═════════════════════════════════════════════════════════
    # CHANNEL UPDATE 🟡
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):

        changes = []

        if before.name != after.name:
            changes.append(
                f"**Name:** `{before.name}` → `{after.name}`"
            )

        if before.position != after.position:
            changes.append(
                f"**Position:** `{before.position}` → `{after.position}`"
            )

        if before.category != after.category:

            before_category = (
                before.category.name
                if before.category
                else "None"
            )

            after_category = (
                after.category.name
                if after.category
                else "None"
            )

            changes.append(
                f"**Category:** `{before_category}` → "
                f"`{after_category}`"
            )

        if not changes:
            return

        executor = await get_audit_executor(
            after.guild,
            discord.AuditLogAction.channel_update,
            after.id
        )

        await send_log(
            after.guild,
            "✏️ Channel Updated",
            f"{after.mention} was updated.",
            color=MEDIUM,
            fields=[
                (
                    "📢 Channel",
                    f"{after.name}\n`{after.id}`",
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

    # ═════════════════════════════════════════════════════════
    # ROLE CREATE 🟡
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):

        executor = await get_audit_executor(
            role.guild,
            discord.AuditLogAction.role_create,
            role.id
        )

        await send_log(
            role.guild,
            "🎭 Role Created",
            f"{role.mention} was created.",
            color=MEDIUM,
            fields=[
                (
                    "🎭 Role",
                    f"{role.name}\n`{role.id}`",
                    True
                ),
                (
                    "🎨 Color",
                    str(role.color),
                    True
                ),
                (
                    "🛡️ Created By",
                    executor_text(executor),
                    True
                )
            ]
        )

    # ═════════════════════════════════════════════════════════
    # ROLE DELETE 🔴
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):

        executor = await get_audit_executor(
            role.guild,
            discord.AuditLogAction.role_delete,
            role.id
        )

        await send_log(
            role.guild,
            "🗑️ Role Deleted",
            f"**{role.name}** was deleted.",
            color=HIGH,
            fields=[
                (
                    "🎭 Role",
                    f"{role.name}\n`{role.id}`",
                    True
                ),
                (
                    "🛡️ Deleted By",
                    executor_text(executor),
                    True
                )
            ]
        )

    # ═════════════════════════════════════════════════════════
    # ROLE UPDATE 🟡
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):

        changes = []

        if before.name != after.name:
            changes.append(
                f"**Name:** `{before.name}` → `{after.name}`"
            )

        if before.color != after.color:
            changes.append(
                f"**Color:** `{before.color}` → `{after.color}`"
            )

        if before.hoist != after.hoist:
            changes.append(
                f"**Displayed separately:** "
                f"`{before.hoist}` → `{after.hoist}`"
            )

        if before.mentionable != after.mentionable:
            changes.append(
                f"**Mentionable:** "
                f"`{before.mentionable}` → `{after.mentionable}`"
            )

        if before.permissions != after.permissions:
            changes.append(
                "**Permissions:** Updated"
            )

        if not changes:
            return

        executor = await get_audit_executor(
            after.guild,
            discord.AuditLogAction.role_update,
            after.id
        )

        await send_log(
            after.guild,
            "✏️ Role Updated",
            f"{after.mention} was updated.",
            color=MEDIUM,
            fields=[
                (
                    "🎭 Role",
                    f"{after.name}\n`{after.id}`",
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

    # ═════════════════════════════════════════════════════════
    # MEMBER UPDATE
    # ═════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        # ─────────────────────────────────────────────────────
        # ROLE CHANGES 🟢
        # ─────────────────────────────────────────────────────

        if before.roles != after.roles:

            before_roles = {
                role.id
                for role in before.roles
            }

            after_roles = {
                role.id
                for role in after.roles
            }

            added = after_roles - before_roles
            removed = before_roles - after_roles

            changes = []

            if added:

                added_names = []

                for role_id in added:

                    role = after.guild.get_role(role_id)

                    if role:
                        added_names.append(
                            role.mention
                        )

                if added_names:
                    changes.append(
                        "🟢 **Role Added:** "
                        + ", ".join(added_names)
                    )

            if removed:

                removed_names = []

                for role_id in removed:

                    role = before.guild.get_role(role_id)

                    if role:
                        removed_names.append(
                            f"`{role.name}`"
                        )

                if removed_names:
                    changes.append(
                        "🟢 **Role Removed:** "
                        + ", ".join(removed_names)
                    )

            if changes:

                executor = await get_audit_executor(
                    after.guild,
                    discord.AuditLogAction.member_role_update,
                    after.id
                )

                await send_log(
                    after.guild,
                    "🎭 Member Roles Updated",
                    f"{after.mention}'s roles were changed.",
                    color=LOW,
                    fields=[
                        (
                            "👤 Member",
                            f"{after}\n`{after.id}`",
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

        # ─────────────────────────────────────────────────────
        # NICKNAME CHANGE 🟡
        # ─────────────────────────────────────────────────────

        if before.nick != after.nick:

            old_nick = before.nick or before.name
            new_nick = after.nick or after.name

            executor = await get_audit_executor(
                after.guild,
                discord.AuditLogAction.member_update,
                after.id
            )

            await send_log(
                after.guild,
                "🏷️ Nickname Changed",
                f"{after.mention}'s nickname was changed.",
                color=MEDIUM,
                fields=[
                    (
                        "👤 Member",
                        f"{after}\n`{after.id}`",
                        True
                    ),
                    (
                        "🛡️ Changed By",
                        executor_text(executor),
                        True
                    ),
                    (
                        "⬅️ Before",
                        f"`{old_nick}`",
                        True
                    ),
                    (
                        "➡️ After",
                        f"`{new_nick}`",
                        True
                    )
                ]
            )


# ═════════════════════════════════════════════════════════════
# SETUP
# ═════════════════════════════════════════════════════════════

async def setup(bot):
    await bot.add_cog(Logging(bot))