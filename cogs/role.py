import re
import sqlite3
from pathlib import Path

import discord
from discord.ext import commands

from core.logger import send_log


CRIMSON = discord.Color.from_rgb(150, 25, 35)

DB_PATH = Path("data/vexora.db")

# =========================================================
# AESTHETIC HEX PALETTE
# =========================================================

HEX_COLORS = [
    ("🩷", "Soft Pink", "#FFB6C1"),
    ("🌸", "Sakura Pink", "#FF69B4"),
    ("❤️", "Crimson", "#DC143C"),
    ("🍷", "Burgundy", "#800020"),
    ("💜", "Lavender", "#B57EDC"),
    ("💟", "Pastel Purple", "#C8A2C8"),
    ("🔮", "Mystic Violet", "#8F00FF"),
    ("💙", "Sky Blue", "#87CEEB"),
    ("🩵", "Baby Blue", "#89CFF0"),
    ("🌊", "Ocean Blue", "#0077B6"),
    ("💚", "Mint Green", "#98FF98"),
    ("🌿", "Sage Green", "#A3B18A"),
    ("🍃", "Emerald", "#50C878"),
    ("💛", "Pastel Yellow", "#FDFD96"),
    ("🧡", "Peach", "#FFCBA4"),
]


# =========================================================
# PERSISTENT STORAGE
# =========================================================

def initialize_hex_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS hex_reaction_roles (
                guild_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                emoji TEXT NOT NULL,
                PRIMARY KEY (message_id, emoji)
            )
        """)
        connection.commit()


def save_hex_mapping(guild_id, message_id, role_id, emoji):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            INSERT OR REPLACE INTO hex_reaction_roles
            (guild_id, message_id, role_id, emoji)
            VALUES (?, ?, ?, ?)
        """, (guild_id, message_id, role_id, emoji))
        connection.commit()


def get_hex_mapping(guild_id, message_id, emoji):
    with sqlite3.connect(DB_PATH) as connection:
        return connection.execute("""
            SELECT role_id
            FROM hex_reaction_roles
            WHERE guild_id = ?
              AND message_id = ?
              AND emoji = ?
        """, (guild_id, message_id, emoji)).fetchone()


def get_hex_roles(guild_id):
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("""
            SELECT DISTINCT role_id
            FROM hex_reaction_roles
            WHERE guild_id = ?
        """, (guild_id,)).fetchall()

    return {row[0] for row in rows}


# =========================================================
# ROLE CREATOR MODAL
# =========================================================

class CreateRoleModal(discord.ui.Modal, title="🎭 Create Vexora Role"):

    role_name = discord.ui.TextInput(
        label="Role Name",
        placeholder="Enter the role name...",
        required=True,
        max_length=100
    )

    role_color = discord.ui.TextInput(
        label="Role Color",
        placeholder="Example: #961923",
        required=False,
        max_length=7
    )

    def __init__(self, creator: discord.Member):
        super().__init__()
        self.creator = creator

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                "❌ This can only be used inside a server.",
                ephemeral=True
            )
            return

        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ You need **Manage Roles** permission.",
                ephemeral=True
            )
            return

        bot_member = guild.me

        if bot_member is None or not bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ I need **Manage Roles** permission.",
                ephemeral=True
            )
            return

        name = self.role_name.value.strip()

        if not name:
            await interaction.response.send_message(
                "❌ Role name cannot be empty.",
                ephemeral=True
            )
            return

        color_text = self.role_color.value.strip()

        if not color_text:
            color = CRIMSON
        else:
            if not color_text.startswith("#"):
                color_text = "#" + color_text

            if not re.fullmatch(r"#[0-9a-fA-F]{6}", color_text):
                await interaction.response.send_message(
                    "❌ Invalid HEX color. Example: `#961923`",
                    ephemeral=True
                )
                return

            color = discord.Color(int(color_text[1:], 16))

        await interaction.response.defer(ephemeral=True)

        try:
            role = await guild.create_role(
                name=name,
                color=color,
                hoist=False,
                mentionable=False,
                reason=f"Vexora role creation by {interaction.user}"
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I cannot create this role. Check my permissions "
                "and role hierarchy.",
                ephemeral=True
            )
            return

        except discord.HTTPException:
            await interaction.followup.send(
                "⚠️ Discord rejected the role creation.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🎭 Role Created",
            description=f"Successfully created {role.mention}.",
            color=color
        )

        embed.add_field(
            name="🎨 HEX Color",
            value=f"`#{role.color.value:06X}`",
            inline=True
        )

        embed.add_field(
            name="🛡️ Created By",
            value=interaction.user.mention,
            inline=True
        )

        embed.set_footer(
            text="Vexora • Role Management • Developed by Potter"
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

        await send_log(
            guild,
            "🎭 Role Created",
            f"{role.mention} was created using Vexora.",
            color=color
        )


# =========================================================
# ROLE CREATOR VIEW
# =========================================================

class RoleCreatorView(discord.ui.View):

    def __init__(self, author: discord.Member):
        super().__init__(timeout=180)
        self.author = author

    async def interaction_check(self, interaction):

        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ This panel belongs to another administrator.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(
        label="Create Role",
        emoji="🎭",
        style=discord.ButtonStyle.danger
    )
    async def create_role(self, interaction, button):
        await interaction.response.send_modal(
            CreateRoleModal(interaction.user)
        )

    @discord.ui.button(
        label="Close",
        emoji="✖️",
        style=discord.ButtonStyle.secondary
    )
    async def close(self, interaction, button):
        await interaction.response.edit_message(
            content="🔒 Role creator closed.",
            embed=None,
            view=None
        )


# =========================================================
# HEX ROLE SYSTEM
# =========================================================

class Role(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        initialize_hex_database()

    # =====================================================
    # BUILD HEX EMBED
    # =====================================================

    def build_hex_embed(self, guild, roles):

        embed = discord.Embed(
            title="🎨 VEXORA  •  COLOUR ROLES",
            description=(
                "### Express yourself. Choose your aesthetic.\n"
                "React with an emoji below to receive its colour role.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
            ),
            color=CRIMSON
        )

        lines = []

        for emoji, name, hex_code in HEX_COLORS:
            role = roles.get(name)

            if role:
                lines.append(
                    f"{emoji}  **{name}** — {role.mention} "
                    f"`{hex_code}`"
                )

        embed.description += "\n".join(lines)

        embed.add_field(
            name="✨ How to use",
            value=(
                "React to choose a colour.\n"
                "React to a different colour to switch.\n"
                "Remove your reaction to remove your colour role."
            ),
            inline=False
        )

        embed.set_footer(
            text="Vexora • Aesthetic Role System • Developed by Potter"
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        return embed

    # =====================================================
    # HEX SETUP COMMAND
    # =====================================================

    @commands.hybrid_command(
        name="hexsetup",
        description="Create aesthetic HEX roles and a reaction panel."
    )
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(
        manage_roles=True,
        add_reactions=True,
        read_message_history=True,
        send_messages=True,
        embed_links=True
    )
    async def hexsetup(self, ctx: commands.Context):

        guild = ctx.guild

        if guild is None:
            return

        bot_member = guild.me

        if bot_member is None:
            await ctx.send("❌ I couldn't verify my server permissions.")
            return

        await ctx.defer()

        created_count = 0
        roles = {}

        # -------------------------------------------------
        # CREATE OR REUSE THE 15 COLOUR ROLES
        # -------------------------------------------------

        for emoji, name, hex_code in HEX_COLORS:

            role_name = f"Hex • {name}"
            colour = discord.Color(int(hex_code[1:], 16))

            role = discord.utils.get(
                guild.roles,
                name=role_name
            )

            try:
                if role is None:
                    role = await guild.create_role(
                        name=role_name,
                        color=colour,
                        hoist=False,
                        mentionable=False,
                        reason=f"Vexora HEX setup by {ctx.author}"
                    )
                    created_count += 1

                elif role.color.value != colour.value:
                    if role >= bot_member.top_role:
                        await ctx.send(
                            f"❌ I cannot update {role.mention}. "
                            "Move my highest role above the HEX roles.",
                            ephemeral=True
                        )
                        return

                    await role.edit(
                        color=colour,
                        reason="Vexora HEX palette refresh"
                    )

                roles[name] = role

            except discord.Forbidden:
                await ctx.send(
                    "❌ I couldn't create or update the colour roles. "
                    "Give Vexora **Manage Roles** and move its highest "
                    "role above the HEX roles.",
                    ephemeral=True
                )
                return

            except discord.HTTPException:
                await ctx.send(
                    f"⚠️ Discord rejected the update for **{name}**. "
                    "Please try again.",
                    ephemeral=True
                )
                return

        # -------------------------------------------------
        # SEND THE REACTION PANEL
        # -------------------------------------------------

        panel_embed = self.build_hex_embed(guild, roles)

        try:
            panel_message = await ctx.send(embed=panel_embed)

            # Add the reactions and save each mapping.
            for emoji, name, hex_code in HEX_COLORS:
                await panel_message.add_reaction(emoji)

                save_hex_mapping(
                    guild.id,
                    panel_message.id,
                    roles[name].id,
                    emoji
                )

        except discord.Forbidden:
            await ctx.send(
                "⚠️ The roles were created, but I couldn't finish "
                "the reaction panel. Check Add Reactions and "
                "Read Message History permissions."
            )
            return

        except discord.HTTPException:
            await ctx.send(
                "⚠️ The roles were created, but Discord rejected "
                "part of the panel setup. Run `/hexsetup` again "
                "after checking the bot's permissions."
            )
            return

        # -------------------------------------------------
        # LOGGING
        # -------------------------------------------------

        await send_log(
            guild,
            "🎨 HEX Role System Created",
            (
                f"HEX reaction roles were configured by "
                f"{ctx.author.mention}.\n"
                f"**New roles created:** {created_count}\n"
                f"**Palette size:** {len(HEX_COLORS)}"
            ),
            color=CRIMSON
        )

        await ctx.send(
            f"✅ **Vexora HEX setup complete!**\n"
            f"🎨 New roles created: **{created_count}**\n"
            f"🌈 Total colours: **{len(HEX_COLORS)}**\n"
            f"📩 Panel: {panel_message.jump_url}",
            ephemeral=True
        )

    # =====================================================
    # REACTION ROLE HANDLER
    # =====================================================

    async def process_hex_reaction(self, payload, add_role: bool):

        if payload.guild_id is None:
            return

        if self.bot.user and payload.user_id == self.bot.user.id:
            return

        if str(payload.emoji) not in {
            emoji for emoji, _, _ in HEX_COLORS
        }:
            return

        mapping = get_hex_mapping(
            payload.guild_id,
            payload.message_id,
            str(payload.emoji)
        )

        if mapping is None:
            return

        guild = self.bot.get_guild(payload.guild_id)

        if guild is None:
            return

        member = guild.get_member(payload.user_id)

        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                return

        if member.bot:
            return

        role_id = mapping[0]
        role = guild.get_role(role_id)

        if role is None or role.is_default() or role.managed:
            return

        bot_member = guild.me

        if bot_member is None:
            return

        if not bot_member.guild_permissions.manage_roles:
            return

        if role >= bot_member.top_role:
            return

        hex_role_ids = get_hex_roles(guild.id)

        try:
            if add_role:
                # Remove other Vexora HEX roles first.
                old_roles = [
                    existing_role
                    for existing_role in member.roles
                    if existing_role.id in hex_role_ids
                    and existing_role.id != role.id
                    and existing_role < bot_member.top_role
                ]

                if old_roles:
                    await member.remove_roles(
                        *old_roles,
                        reason="Vexora HEX colour switched"
                    )

                if role not in member.roles:
                    await member.add_roles(
                        role,
                        reason="Vexora HEX reaction role"
                    )

            else:
                if role in member.roles:
                    await member.remove_roles(
                        role,
                        reason="Vexora HEX reaction removed"
                    )

        except (discord.Forbidden, discord.HTTPException):
            # A role hierarchy or API error should not crash the bot.
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.process_hex_reaction(payload, add_role=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.process_hex_reaction(payload, add_role=False)

    # =====================================================
    # EXISTING CREATE ROLE COMMAND
    # =====================================================

    @commands.hybrid_command(
        name="createrole",
        description="Open Vexora's role creator."
    )
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def createrole(self, ctx: commands.Context):

        embed = discord.Embed(
            title="🎭 Vexora Role Creator",
            description=(
                "**Create a new server role using Vexora.**\n\n"
                "Click **Create Role** below to configure your role.\n\n"
                "🎭 **Role Name** — choose the role name.\n"
                "🎨 **Role Color** — enter a HEX code like `#961923`.\n"
                "🔐 **Permissions** — roles start without extra permissions."
            ),
            color=CRIMSON
        )

        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.set_footer(
            text="Vexora • Role Management • Developed by Potter"
        )

        await ctx.send(
            embed=embed,
            view=RoleCreatorView(ctx.author)
        )

    # =====================================================
    # EXISTING ROLE TOGGLE COMMAND
    # =====================================================

    @commands.hybrid_command(
        name="role",
        description="Give or remove a role from a member."
    )
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(
        self,
        ctx: commands.Context,
        member: discord.Member,
        role: discord.Role
    ):

        guild = ctx.guild
        bot_member = guild.me

        if member == ctx.author:
            await ctx.send("❌ You cannot manage your own roles with this command.")
            return

        if role.is_default() or role.managed:
            await ctx.send("❌ That role cannot be manually managed.")
            return

        if (
            ctx.author.id != guild.owner_id
            and role >= ctx.author.top_role
        ):
            await ctx.send(
                "❌ You can only manage roles below your highest role."
            )
            return

        if bot_member is None or role >= bot_member.top_role:
            await ctx.send(
                "❌ I can only manage roles below my highest role."
            )
            return

        try:
            if role in member.roles:
                await member.remove_roles(
                    role,
                    reason=f"Vexora role command by {ctx.author}"
                )
                action = "removed"
                emoji = "➖"
            else:
                await member.add_roles(
                    role,
                    reason=f"Vexora role command by {ctx.author}"
                )
                action = "added"
                emoji = "➕"

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage that role.")
            return

        except discord.HTTPException:
            await ctx.send("⚠️ Discord rejected the role update.")
            return

        embed = discord.Embed(
            title=f"{emoji} Role {action.title()}",
            description=(
                f"Successfully **{action}** {role.mention} "
                f"{'to' if action == 'added' else 'from'} {member.mention}."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="👤 Member",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="🎭 Role",
            value=role.mention,
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=ctx.author.mention,
            inline=True
        )

        embed.set_footer(
            text="Vexora • Role Management • Developed by Potter"
        )

        await ctx.send(embed=embed)


async def setup(bot):
    initialize_hex_database()
    await bot.add_cog(Role(bot))