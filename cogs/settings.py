import discord
from discord.ext import commands

from core.database import (
    get_guild_settings,
    get_automod_settings,
    set_automod_settings,
    clear_automod_role,
)


CRIMSON = discord.Color.from_rgb(150, 25, 35)


# =========================================================
# SETTINGS EMBED
# =========================================================

def create_settings_embed(guild: discord.Guild):

    embed = discord.Embed(
        title="⚙️ Vexora Server Settings",
        description=(
            "Manage your server's Vexora systems from this panel.\n\n"
            "Choose a system below to configure it."
        ),
        color=CRIMSON
    )

    embed.add_field(
        name="👋 Welcome System",
        value="Configure your custom welcome messages.",
        inline=False
    )

    embed.add_field(
        name="🚨 AutoMod",
        value="Configure spam, repeats, mentions and blocked words.",
        inline=False
    )

    embed.add_field(
        name="📊 Server Information",
        value="View server statistics and information.",
        inline=False
    )

    embed.add_field(
        name="🟢 System Status",
        value="Check the current status of Vexora systems.",
        inline=False
    )

    embed.set_thumbnail(
        url=guild.icon.url
        if guild.icon
        else discord.Embed.Empty
    )

    embed.set_footer(
        text="Vexora • Server Settings • Developed by Potter"
    )

    return embed


# =========================================================
# AUTOMOD EMBED
# =========================================================

def create_automod_embed(guild: discord.Guild):

    settings = get_automod_settings(guild.id)

    if settings:

        (
            enabled,
            role_id,
            timeout_minutes,
            spam_enabled,
            repeat_enabled,
            mention_enabled
        ) = settings

    else:

        enabled = 1
        role_id = None
        timeout_minutes = 5
        spam_enabled = 1
        repeat_enabled = 1
        mention_enabled = 1

    automod_status = (
        "🟢 Enabled"
        if enabled
        else "🔴 Disabled"
    )

    spam_status = (
        "🟢 ON"
        if spam_enabled
        else "🔴 OFF"
    )

    repeat_status = (
        "🟢 ON"
        if repeat_enabled
        else "🔴 OFF"
    )

    mention_status = (
        "🟢 ON"
        if mention_enabled
        else "🔴 OFF"
    )

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

    embed = discord.Embed(
        title="🚨 Vexora AutoMod",
        description=(
            "Configure Vexora's automatic moderation system.\n\n"
            "AutoMod can detect spam, repeated messages, "
            "mention spam and blocked words."
        ),
        color=CRIMSON
    )

    embed.add_field(
        name="🛡️ Status",
        value=automod_status,
        inline=True
    )

    embed.add_field(
        name="🔇 Timeout",
        value=f"`{timeout_minutes} minutes`",
        inline=True
    )

    embed.add_field(
        name="👮 Staff Notification Role",
        value=role_text,
        inline=True
    )

    embed.add_field(
        name="💬 Spam Protection",
        value=spam_status,
        inline=True
    )

    embed.add_field(
        name="🔁 Repeat Protection",
        value=repeat_status,
        inline=True
    )

    embed.add_field(
        name="📢 Mention Protection",
        value=mention_status,
        inline=True
    )

    embed.add_field(
        name="🚫 Blocked Words",
        value=(
            "Default blocked-word protection is **ON**.\n"
            "Messages containing configured blocked words "
            "are automatically removed."
        ),
        inline=False
    )

    embed.set_footer(
        text="Vexora • AutoMod System • Developed by Potter"
    )

    return embed


# =========================================================
# SETTINGS VIEW
# =========================================================

class SettingsView(discord.ui.View):

    def __init__(
        self,
        bot,
        guild_id,
        author_id
    ):

        super().__init__(timeout=180)

        self.bot = bot
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(
                "❌ Only the person who opened this settings panel can use it.",
                ephemeral=True
            )

            return False

        if not interaction.user.guild_permissions.manage_guild:

            await interaction.response.send_message(
                "❌ You need **Manage Server** permission to use this panel.",
                ephemeral=True
            )

            return False

        return True

    # =====================================================
    # WELCOME
    # =====================================================

    @discord.ui.button(
        label="Welcome",
        emoji="👋",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def welcome(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        from cogs.welcome import WelcomeConfigView

        embed = discord.Embed(
            title="👋 Vexora Welcome System",
            description=(
                "Configure your server's custom welcome system."
            ),
            color=CRIMSON
        )

        view = WelcomeConfigView(
            self.bot,
            self.guild_id
        )

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )

    # =====================================================
    # AUTOMOD
    # =====================================================

    @discord.ui.button(
        label="AutoMod",
        emoji="🚨",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def automod(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = create_automod_embed(
            interaction.guild
        )

        view = AutoModSettingsView(
            self.bot,
            self.guild_id,
            self.author_id
        )

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )

    # =====================================================
    # SERVER INFO
    # =====================================================

    @discord.ui.button(
        label="Server Info",
        emoji="📊",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def server_info(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild

        embed = discord.Embed(
            title="📊 Server Information",
            color=CRIMSON
        )

        embed.add_field(
            name="🏠 Server",
            value=guild.name,
            inline=True
        )

        embed.add_field(
            name="🆔 Server ID",
            value=f"`{guild.id}`",
            inline=True
        )

        embed.add_field(
            name="👥 Members",
            value=f"`{guild.member_count}`",
            inline=True
        )

        embed.add_field(
            name="💬 Channels",
            value=f"`{len(guild.channels)}`",
            inline=True
        )

        embed.add_field(
            name="🎭 Roles",
            value=f"`{len(guild.roles)}`",
            inline=True
        )

        embed.add_field(
            name="🚀 Boost Level",
            value=f"`{guild.premium_tier}`",
            inline=True
        )

        if guild.owner:
            embed.add_field(
                name="👑 Owner",
                value=guild.owner.mention,
                inline=False
            )

        embed.set_footer(
            text="Vexora • Server Information"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=SettingsView(
                self.bot,
                self.guild_id,
                self.author_id
            )
        )

    # =====================================================
    # SYSTEM STATUS
    # =====================================================

    @discord.ui.button(
        label="System Status",
        emoji="🟢",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def system_status(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild

        welcome_settings = get_guild_settings(
            guild.id
        )

        automod_settings = get_automod_settings(
            guild.id
        )

        welcome_enabled = (
            bool(welcome_settings[0])
            if welcome_settings
            else False
        )

        automod_enabled = (
            bool(automod_settings[0])
            if automod_settings
            else False
        )

        embed = discord.Embed(
            title="🟢 Vexora System Status",
            description="Current Vexora systems for this server.",
            color=CRIMSON
        )

        embed.add_field(
            name="👋 Welcome",
            value=(
                "🟢 Enabled"
                if welcome_enabled
                else "🔴 Disabled"
            ),
            inline=True
        )

        embed.add_field(
            name="🚨 AutoMod",
            value=(
                "🟢 Enabled"
                if automod_enabled
                else "🔴 Disabled"
            ),
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderation",
            value="🟢 Online",
            inline=True
        )

        embed.add_field(
            name="📋 Logging",
            value="🟢 Online",
            inline=True
        )

        embed.add_field(
            name="🎨 Embed Builder",
            value="🟢 Online",
            inline=True
        )

        embed.add_field(
            name="🤖 Core",
            value="🟢 Online",
            inline=True
        )

        embed.set_footer(
            text="Vexora • System Status"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=SettingsView(
                self.bot,
                self.guild_id,
                self.author_id
            )
        )

    # =====================================================
    # REFRESH
    # =====================================================

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

        embed = create_settings_embed(
            interaction.guild
        )

        await interaction.response.edit_message(
            embed=embed,
            view=SettingsView(
                self.bot,
                self.guild_id,
                self.author_id
            )
        )

    # =====================================================
    # CLOSE
    # =====================================================

    @discord.ui.button(
        label="Close",
        emoji="✖️",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="🔒 **Vexora settings panel closed.**",
            embed=None,
            view=self
        )


# =========================================================
# AUTOMOD SETTINGS VIEW
# =========================================================

class AutoModSettingsView(discord.ui.View):

    def __init__(
        self,
        bot,
        guild_id,
        author_id
    ):

        super().__init__(timeout=180)

        self.bot = bot
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(
                "❌ Only the person who opened this panel can use it.",
                ephemeral=True
            )

            return False

        if not interaction.user.guild_permissions.manage_guild:

            await interaction.response.send_message(
                "❌ You need **Manage Server** permission.",
                ephemeral=True
            )

            return False

        return True

    async def refresh_panel(
        self,
        interaction: discord.Interaction
    ):

        embed = create_automod_embed(
            interaction.guild
        )

        await interaction.response.edit_message(
            embed=embed,
            view=AutoModSettingsView(
                self.bot,
                self.guild_id,
                self.author_id
            )
        )

    # =====================================================
    # SELECT STAFF ROLE
    # =====================================================

    @discord.ui.button(
        label="Staff Role",
        emoji="👮",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def staff_role(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="👮 Select AutoMod Staff Role",
            description=(
                "Choose the role Vexora should mention when "
                "AutoMod detects a violation."
            ),
            color=CRIMSON
        )

        view = AutoModRoleView(
            self.bot,
            self.guild_id,
            self.author_id
        )

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )

    # =====================================================
    # ENABLE
    # =====================================================

    @discord.ui.button(
        label="Enable",
        emoji="🟢",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def enable(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        set_automod_settings(
            self.guild_id,
            enabled=1
        )

        await self.refresh_panel(interaction)

    # =====================================================
    # DISABLE
    # =====================================================

    @discord.ui.button(
        label="Disable",
        emoji="🔴",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def disable(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        set_automod_settings(
            self.guild_id,
            enabled=0
        )

        await self.refresh_panel(interaction)

    # =====================================================
    # SPAM TOGGLE
    # =====================================================

    @discord.ui.button(
        label="Toggle Spam",
        emoji="💬",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def toggle_spam(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        settings = get_automod_settings(
            self.guild_id
        )

        current = settings[3]

        set_automod_settings(
            self.guild_id,
            spam_enabled=0 if current else 1
        )

        await self.refresh_panel(interaction)

    # =====================================================
    # REPEAT TOGGLE
    # =====================================================

    @discord.ui.button(
        label="Toggle Repeat",
        emoji="🔁",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def toggle_repeat(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        settings = get_automod_settings(
            self.guild_id
        )

        current = settings[4]

        set_automod_settings(
            self.guild_id,
            repeat_enabled=0 if current else 1
        )

        await self.refresh_panel(interaction)

    # =====================================================
    # MENTION TOGGLE
    # =====================================================

    @discord.ui.button(
        label="Toggle Mentions",
        emoji="📢",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def toggle_mentions(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        settings = get_automod_settings(
            self.guild_id
        )

        current = settings[5]

        set_automod_settings(
            self.guild_id,
            mention_enabled=0 if current else 1
        )

        await self.refresh_panel(interaction)

    # =====================================================
    # CLEAR ROLE
    # =====================================================

    @discord.ui.button(
        label="Clear Role",
        emoji="🗑️",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def clear_role(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        clear_automod_role(
            self.guild_id
        )

        await self.refresh_panel(interaction)

    # =====================================================
    # BACK
    # =====================================================

    @discord.ui.button(
        label="Back",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = create_settings_embed(
            interaction.guild
        )

        await interaction.response.edit_message(
            embed=embed,
            view=SettingsView(
                self.bot,
                self.guild_id,
                self.author_id
            )
        )

    # =====================================================
    # CLOSE
    # =====================================================

    @discord.ui.button(
        label="Close",
        emoji="✖️",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="🔒 **Vexora AutoMod panel closed.**",
            embed=None,
            view=self
        )


# =========================================================
# AUTOMOD ROLE SELECT VIEW
# =========================================================

class AutoModRoleView(discord.ui.View):

    def __init__(
        self,
        bot,
        guild_id,
        author_id
    ):

        super().__init__(timeout=180)

        self.bot = bot
        self.guild_id = guild_id
        self.author_id = author_id

        self.role_select = discord.ui.RoleSelect(
            placeholder="👮 Select the staff notification role",
            min_values=1,
            max_values=1
        )

        self.role_select.callback = self.role_selected

        self.add_item(self.role_select)

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(
                "❌ Only the person who opened this panel can use it.",
                ephemeral=True
            )

            return False

        if not interaction.user.guild_permissions.manage_guild:

            await interaction.response.send_message(
                "❌ You need **Manage Server** permission.",
                ephemeral=True
            )

            return False

        return True

    async def role_selected(
        self,
        interaction: discord.Interaction
    ):

        role = self.role_select.values[0]

        set_automod_settings(
            self.guild_id,
            role_id=role.id
        )

        embed = create_automod_embed(
            interaction.guild
        )

        view = AutoModSettingsView(
            self.bot,
            self.guild_id,
            self.author_id
        )

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )

    # =====================================================
    # BACK
    # =====================================================

    @discord.ui.button(
        label="Back",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = create_automod_embed(
            interaction.guild
        )

        view = AutoModSettingsView(
            self.bot,
            self.guild_id,
            self.author_id
        )

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )

    # =====================================================
    # CLOSE
    # =====================================================

    @discord.ui.button(
        label="Close",
        emoji="✖️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="🔒 **Vexora AutoMod panel closed.**",
            embed=None,
            view=self
        )


# =========================================================
# /settings COMMAND
# =========================================================

class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="settings",
        description="Open the Vexora server settings panel."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def settings(
        self,
        ctx: commands.Context
    ):

        embed = create_settings_embed(
            ctx.guild
        )

        view = SettingsView(
            self.bot,
            ctx.guild.id,
            ctx.author.id
        )

        await ctx.send(
            embed=embed,
            view=view
        )


async def setup(bot):

    await bot.add_cog(
        Settings(bot)
    )