import re

import discord
from discord.ext import commands

from core.logger import send_log

CRIMSON = discord.Color.from_rgb(150, 25, 35)


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
        placeholder="Example: #961923 or leave empty for Vexora Crimson",
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

        # -------------------------------------------------
        # Permission check
        # -------------------------------------------------

        if not self.creator.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ You need **Manage Roles** permission to create roles.",
                ephemeral=True
            )
            return

        bot_member = guild.me

        if bot_member is None:
            await interaction.response.send_message(
                "❌ I couldn't verify my server permissions.",
                ephemeral=True
            )
            return

        if not bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ I need the **Manage Roles** permission to create roles.",
                ephemeral=True
            )
            return

        # -------------------------------------------------
        # Clean role name
        # -------------------------------------------------

        name = self.role_name.value.strip()

        if not name:
            await interaction.response.send_message(
                "❌ Role name cannot be empty.",
                ephemeral=True
            )
            return

        # -------------------------------------------------
        # Parse color
        # -------------------------------------------------

        color_text = self.role_color.value.strip()

        if not color_text:
            color = CRIMSON

        else:
            if not color_text.startswith("#"):
                color_text = "#" + color_text

            if not re.fullmatch(r"#[0-9a-fA-F]{6}", color_text):
                await interaction.response.send_message(
                    "❌ Invalid color.\n\n"
                    "Use a HEX color such as `#961923`.",
                    ephemeral=True
                )
                return

            try:
                color = discord.Color(
                    int(color_text[1:], 16)
                )
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid HEX color.",
                    ephemeral=True
                )
                return

        # -------------------------------------------------
        # Create role
        # -------------------------------------------------

        try:

            role = await guild.create_role(
                name=name,
                color=color,
                hoist=False,
                mentionable=False,
                reason=f"Vexora role creation by {interaction.user}"
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to create roles.",
                ephemeral=True
            )
            return

        except discord.HTTPException:
            await interaction.response.send_message(
                "⚠️ Discord rejected the role creation. "
                "Please try again.",
                ephemeral=True
            )
            return

        # -------------------------------------------------
        # Success embed
        # -------------------------------------------------

        embed = discord.Embed(
            title="🎭 Role Created",
            description=(
                f"Successfully created {role.mention}."
            ),
            color=color
        )

        embed.add_field(
            name="🎭 Role",
            value=f"{role.mention}\n`{role.id}`",
            inline=True
        )

        embed.add_field(
            name="🎨 Color",
            value=f"`#{role.color.value:06X}`",
            inline=True
        )

        embed.add_field(
            name="🛡️ Created By",
            value=(
                f"{interaction.user.mention}\n"
                f"`{interaction.user.id}`"
            ),
            inline=True
        )

        embed.add_field(
            name="🔐 Permissions",
            value="No special permissions",
            inline=False
        )

        embed.set_footer(
            text="Vexora • Role Management • Developed by Potter"
        )

        await interaction.response.send_message(
            embed=embed
        )

        # -------------------------------------------------
        # Logging
        # -------------------------------------------------

        await send_log(
            guild,
            "🎭 Role Created",
            f"{role.mention} was created using Vexora.",
            color=discord.Color.green(),
            fields=[
                (
                    "🎭 Role",
                    f"{role.name}\n`{role.id}`",
                    True
                ),
                (
                    "🎨 Color",
                    f"`#{role.color.value:06X}`",
                    True
                ),
                (
                    "🛡️ Created By",
                    f"{interaction.user.mention}\n"
                    f"`{interaction.user.id}`",
                    True
                )
            ]
        )


# =========================================================
# ROLE CREATOR VIEW
# =========================================================

class RoleCreatorView(discord.ui.View):

    def __init__(self, author: discord.Member):
        super().__init__(timeout=180)
        self.author = author

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ This role creator belongs to another administrator.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(
        label="Create Role",
        emoji="🎭",
        style=discord.ButtonStyle.danger
    )
    async def create_role(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            CreateRoleModal(interaction.user)
        )

    @discord.ui.button(
        label="Close",
        emoji="✖️",
        style=discord.ButtonStyle.secondary
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.message.delete()


# =========================================================
# ROLE COG
# =========================================================

class Role(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # CREATE ROLE
    # =====================================================

    @commands.hybrid_command(
        name="createrole",
        description="Open Vexora's role creator."
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def createrole(self, ctx: commands.Context):

        if ctx.guild is None:
            await ctx.send(
                "❌ This command can only be used inside a server."
            )
            return

        embed = discord.Embed(
            title="🎭 Vexora Role Creator",
            description=(
                "**Create a new server role using Vexora.**\n\n"
                "Click **Create Role** below to open the "
                "role configuration panel.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🎭 **Role Name**\n"
                "Choose the name of your new role.\n\n"
                "🎨 **Role Color**\n"
                "Enter a HEX color such as `#961923`.\n\n"
                "🔐 **Permissions**\n"
                "New roles start with **no special permissions**.\n"
                "━━━━━━━━━━━━━━━━━━━━"
            ),
            color=CRIMSON
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.set_footer(
            text="Vexora • Role Management • Developed by Potter"
        )

        view = RoleCreatorView(ctx.author)

        await ctx.send(
            embed=embed,
            view=view
        )

    # =====================================================
    # EXISTING ROLE TOGGLE
    # =====================================================

    @commands.hybrid_command(
        name="role",
        description="Give or remove a role from a member."
    )
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(
        self,
        ctx: commands.Context,
        member: discord.Member,
        role: discord.Role
    ):

        guild = ctx.guild

        if guild is None:
            await ctx.send(
                "❌ This command can only be used inside a server."
            )
            return

        bot_member = guild.me

        if member == ctx.author:
            await ctx.send(
                "❌ You cannot manage your own roles with this command."
            )
            return

        if role.is_default():
            await ctx.send(
                "❌ You cannot manage the `@everyone` role."
            )
            return

        if role.managed:
            await ctx.send(
                "❌ This role is managed by an integration "
                "and cannot be manually managed."
            )
            return

        if (
            isinstance(ctx.author, discord.Member)
            and ctx.author.id != guild.owner_id
            and role >= ctx.author.top_role
        ):
            await ctx.send(
                "❌ You can only manage roles **below your highest role**."
            )
            return

        if bot_member is None:
            await ctx.send(
                "❌ I couldn't verify my server permissions."
            )
            return

        if role >= bot_member.top_role:
            await ctx.send(
                "❌ I can only manage roles **below my highest role**."
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

            await ctx.send(
                "❌ I don't have permission to manage that role."
            )
            return

        except discord.HTTPException:

            await ctx.send(
                "⚠️ Discord rejected the role update. "
                "Please try again."
            )
            return

        embed = discord.Embed(
            title=f"{emoji} Role {action.title()}",
            color=CRIMSON
        )

        embed.description = (
            f"Successfully **{action}** "
            f"{role.mention} "
            f"{'to' if action == 'added' else 'from'} "
            f"{member.mention}."
        )

        embed.add_field(
            name="👤 Member",
            value=f"{member.mention}\n`{member.id}`",
            inline=True
        )

        embed.add_field(
            name="🎭 Role",
            value=f"{role.mention}\n`{role.id}`",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=f"{ctx.author.mention}\n`{ctx.author.id}`",
            inline=True
        )

        embed.set_footer(
            text="Vexora • Role Management • Developed by Potter"
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Role(bot))