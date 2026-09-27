import discord
from discord.ext import commands


CRIMSON = discord.Color.from_rgb(150, 25, 35)


# =========================================================
# HELP PANEL
# =========================================================

class HelpView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

    # -----------------------------------------------------
    # HOME
    # -----------------------------------------------------

    def home_embed(self):

        embed = discord.Embed(
            title="🤖 VEXORA",
            description=(
                "**Your powerful Discord server assistant.**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🛡️ **Moderation**\n"
                "Manage and protect your server.\n\n"
                "⚙️ **Utility**\n"
                "Information and server tools.\n\n"
                "🎭 **Role Management**\n"
                "Manage member roles safely.\n\n"
                "🤖 **Vexora**\n"
                "Information about the bot.\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Select a category below."
            ),
            color=CRIMSON
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.set_footer(
            text="Vexora • Developed by Potter"
        )

        return embed

    # -----------------------------------------------------
    # MODERATION
    # -----------------------------------------------------

    def moderation_embed(self):

        embed = discord.Embed(
            title="🛡️ Moderation",
            description="Commands for managing your server.",
            color=CRIMSON
        )

        embed.add_field(
            name="👮 Member Management",
            value=(
                "`kick` • `ban` • `unban`\n"
                "`timeout` • `unmute`"
            ),
            inline=False
        )

        embed.add_field(
            name="⚠️ Warnings",
            value=(
                "`warn` • `warnings`\n"
                "`clearwarnings`"
            ),
            inline=False
        )

        embed.add_field(
            name="🧹 Messages",
            value="`purge`",
            inline=False
        )

        embed.set_footer(
            text="Vexora • Moderation"
        )

        return embed

    # -----------------------------------------------------
    # UTILITY
    # -----------------------------------------------------

    def utility_embed(self):

        embed = discord.Embed(
            title="⚙️ Utility",
            description="Useful information and server tools.",
            color=CRIMSON
        )

        embed.add_field(
            name="👤 Members",
            value=(
                "`userinfo` • `avatar`\n"
                "`membercount`"
            ),
            inline=False
        )

        embed.add_field(
            name="🌐 Server",
            value=(
                "`serverinfo` • `servericon`\n"
                "`roleinfo` • `channelinfo`"
            ),
            inline=False
        )

        embed.add_field(
            name="🔧 System",
            value=(
                "`ping` • `botinfo`"
            ),
            inline=False
        )

        embed.set_footer(
            text="Vexora • Utility"
        )

        return embed

    # -----------------------------------------------------
    # ROLE MANAGEMENT
    # -----------------------------------------------------

    def role_embed(self):

        embed = discord.Embed(
            title="🎭 Role Management",
            description=(
                "Manage member roles using Vexora's "
                "secure role system."
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="🎭 Role",
            value=(
                "`/role @user @role`\n"
                "`v!role @user @role`"
            ),
            inline=False
        )

        embed.add_field(
            name="🔄 How It Works",
            value=(
                "If the member doesn't have the role, "
                "Vexora gives it.\n\n"
                "If the member already has the role, "
                "Vexora removes it."
            ),
            inline=False
        )

        embed.add_field(
            name="🛡️ Security",
            value=(
                "Requires **Manage Roles** permission.\n"
                "Discord role hierarchy is enforced."
            ),
            inline=False
        )

        embed.set_footer(
            text="Vexora • Role Management"
        )

        return embed

    # -----------------------------------------------------
    # BOT INFORMATION
    # -----------------------------------------------------

    def bot_embed(self):

        embed = discord.Embed(
            title="🤖 About Vexora",
            description=(
                "**Vexora** is a custom Discord bot built "
                "to provide powerful moderation and utility "
                "features in one clean system."
            ),
            color=CRIMSON
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.add_field(
            name="📦 Version",
            value="`1.0.0`",
            inline=True
        )

        embed.add_field(
            name="🌐 Servers",
            value=f"`{len(self.bot.guilds)}`",
            inline=True
        )

        embed.add_field(
            name="👥 Users",
            value=f"`{len(self.bot.users)}`",
            inline=True
        )

        embed.add_field(
            name="👨‍💻 Developer",
            value="**Potter**",
            inline=True
        )

        embed.add_field(
            name="🐍 Library",
            value="`discord.py`",
            inline=True
        )

        embed.set_footer(
            text="Vexora • Developed by Potter"
        )

        return embed

    # =====================================================
    # BUTTONS
    # =====================================================

    @discord.ui.button(
        label="Home",
        emoji="🏠",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def home(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            embed=self.home_embed(),
            view=self
        )

    @discord.ui.button(
        label="Moderation",
        emoji="🛡️",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def moderation(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            embed=self.moderation_embed(),
            view=self
        )

    @discord.ui.button(
        label="Utility",
        emoji="⚙️",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def utility(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            embed=self.utility_embed(),
            view=self
        )

    @discord.ui.button(
        label="Roles",
        emoji="🎭",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def roles(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            embed=self.role_embed(),
            view=self
        )

    @discord.ui.button(
        label="Vexora",
        emoji="🤖",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def vexora(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            embed=self.bot_embed(),
            view=self
        )

    @discord.ui.button(
        label="Close",
        emoji="✖️",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.message.delete()


# =========================================================
# UTILITY COG
# =========================================================

class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # PING
    # =====================================================

    @commands.hybrid_command(
        name="ping",
        description="Check Vexora's latency."
    )
    async def ping(
        self,
        ctx: commands.Context
    ):

        latency = round(
            self.bot.latency * 1000
        )

        embed = discord.Embed(
            title="🏓 Pong!",
            description=(
                f"Vexora latency: **{latency}ms**"
            ),
            color=CRIMSON
        )

        embed.add_field(
            name="⚡ Status",
            value="🟢 Online",
            inline=True
        )

        embed.add_field(
            name="📡 WebSocket",
            value=f"`{latency}ms`",
            inline=True
        )

        embed.set_footer(
            text="Vexora • Utility"
        )

        await ctx.send(embed=embed)

    # =====================================================
    # USER INFO
    # =====================================================

    @commands.hybrid_command(
        name="userinfo",
        description="View detailed information about a member."
    )
    async def userinfo(
        self,
        ctx: commands.Context,
        member: discord.Member = None
    ):

        member = member or ctx.author

        embed = discord.Embed(
            title="👤 User Dashboard",
            description=(
                f"Detailed information about "
                f"**{member.display_name}**"
            ),
            color=CRIMSON
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        # -------------------------------------------------
        # BASIC
        # -------------------------------------------------

        embed.add_field(
            name="👤 Username",
            value=f"`{member}`",
            inline=True
        )

        embed.add_field(
            name="🏷️ Display Name",
            value=f"`{member.display_name}`",
            inline=True
        )

        embed.add_field(
            name="🆔 User ID",
            value=f"`{member.id}`",
            inline=True
        )

        # -------------------------------------------------
        # ACCOUNT
        # -------------------------------------------------

        embed.add_field(
            name="📅 Account Created",
            value=discord.utils.format_dt(
                member.created_at,
                style="D"
            ),
            inline=True
        )

        embed.add_field(
            name="⏰ Created",
            value=discord.utils.format_dt(
                member.created_at,
                style="R"
            ),
            inline=True
        )

        joined_text = (
            discord.utils.format_dt(
                member.joined_at,
                style="D"
            )
            if member.joined_at
            else "Unknown"
        )

        embed.add_field(
            name="📥 Joined Server",
            value=joined_text,
            inline=True
        )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        embed.add_field(
            name="🤖 Bot",
            value="Yes" if member.bot else "No",
            inline=True
        )

        embed.add_field(
            name="🎨 Color",
            value=str(member.color),
            inline=True
        )

        embed.add_field(
            name="🛡️ Top Role",
            value=member.top_role.mention,
            inline=True
        )

        # -------------------------------------------------
        # ROLES
        # -------------------------------------------------

        roles = [
            role.mention
            for role in reversed(member.roles)
            if not role.is_default()
        ]

        if roles:

            role_text = ", ".join(roles)

            if len(role_text) > 1000:
                role_text = (
                    role_text[:997] + "..."
                )

        else:
            role_text = "No roles"

        embed.add_field(
            name=f"🎭 Roles ({len(roles)})",
            value=role_text,
            inline=False
        )

        # -------------------------------------------------
        # PERMISSIONS
        # -------------------------------------------------

        permissions = []

        if member.guild_permissions.administrator:
            permissions.append("Administrator")

        else:

            permission_map = {
                "manage_guild": "Manage Server",
                "manage_channels": "Manage Channels",
                "manage_roles": "Manage Roles",
                "manage_messages": "Manage Messages",
                "kick_members": "Kick Members",
                "ban_members": "Ban Members",
                "moderate_members": "Timeout Members"
            }

            for permission, label in permission_map.items():

                if getattr(
                    member.guild_permissions,
                    permission,
                    False
                ):
                    permissions.append(label)

        permission_text = (
            ", ".join(permissions)
            if permissions
            else "No major permissions"
        )

        embed.add_field(
            name="🛡️ Key Permissions",
            value=permission_text,
            inline=False
        )

        embed.set_footer(
            text="Vexora • User Information"
        )

        await ctx.send(embed=embed)

    # =====================================================
    # AVATAR
    # =====================================================

    @commands.hybrid_command(
        name="avatar",
        description="View a member's avatar."
    )
    async def avatar(
        self,
        ctx: commands.Context,
        member: discord.Member = None
    ):

        member = member or ctx.author

        embed = discord.Embed(
            title=f"🖼️ {member.display_name}'s Avatar",
            color=CRIMSON
        )

        embed.set_image(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text="Vexora • Utility"
        )

        await ctx.send(embed=embed)

    # =====================================================
    # SERVER INFO
    # =====================================================

    @commands.hybrid_command(
        name="serverinfo",
        description="View detailed information about the server."
    )
    async def serverinfo(
        self,
        ctx: commands.Context
    ):

        guild = ctx.guild

        if guild is None:
            await ctx.send(
                "❌ This command can only be used inside a server."
            )
            return

        embed = discord.Embed(
            title="🌐 Server Dashboard",
            description=(
                f"Detailed information about "
                f"**{guild.name}**"
            ),
            color=CRIMSON
        )

        if guild.icon:

            embed.set_thumbnail(
                url=guild.icon.url
            )

        # -------------------------------------------------
        # BASIC
        # -------------------------------------------------

        embed.add_field(
            name="🏠 Server Name",
            value=f"`{guild.name}`",
            inline=True
        )

        embed.add_field(
            name="🆔 Server ID",
            value=f"`{guild.id}`",
            inline=True
        )

        embed.add_field(
            name="👑 Owner",
            value=(
                guild.owner.mention
                if guild.owner
                else f"<@{guild.owner_id}>"
            ),
            inline=True
        )

        # -------------------------------------------------
        # MEMBERS
        # -------------------------------------------------

        humans = sum(
            1
            for member in guild.members
            if not member.bot
        )

        bots = sum(
            1
            for member in guild.members
            if member.bot
        )

        embed.add_field(
            name="👥 Members",
            value=f"`{guild.member_count}`",
            inline=True
        )

        embed.add_field(
            name="👤 Humans",
            value=f"`{humans}`",
            inline=True
        )

        embed.add_field(
            name="🤖 Bots",
            value=f"`{bots}`",
            inline=True
        )

        # -------------------------------------------------
        # SERVER STRUCTURE
        # -------------------------------------------------

        text_channels = len(
            guild.text_channels
        )

        voice_channels = len(
            guild.voice_channels
        )

        categories = len(
            guild.categories
        )

        embed.add_field(
            name="📺 Text Channels",
            value=f"`{text_channels}`",
            inline=True
        )

        embed.add_field(
            name="🔊 Voice Channels",
            value=f"`{voice_channels}`",
            inline=True
        )

        embed.add_field(
            name="📂 Categories",
            value=f"`{categories}`",
            inline=True
        )

        # -------------------------------------------------
        # ROLES
        # -------------------------------------------------

        embed.add_field(
            name="🎭 Roles",
            value=f"`{len(guild.roles)}`",
            inline=True
        )

        embed.add_field(
            name="🚀 Boost Level",
            value=f"`Level {guild.premium_tier}`",
            inline=True
        )

        embed.add_field(
            name="💎 Boosts",
            value=f"`{guild.premium_subscription_count or 0}`",
            inline=True
        )

        # -------------------------------------------------
        # SERVER AGE
        # -------------------------------------------------

        embed.add_field(
            name="📅 Created",
            value=discord.utils.format_dt(
                guild.created_at,
                style="D"
            ),
            inline=True
        )

        embed.add_field(
            name="⏰ Server Age",
            value=discord.utils.format_dt(
                guild.created_at,
                style="R"
            ),
            inline=True
        )

        embed.add_field(
            name="🔐 Verification",
            value=str(
                guild.verification_level
            ).replace("_", " ").title(),
            inline=True
        )

        embed.set_footer(
            text="Vexora • Server Dashboard • Developed by Potter"
        )

        await ctx.send(embed=embed)

    # =====================================================
    # ROLE INFO
    # =====================================================

    @commands.hybrid_command(
        name="roleinfo",
        description="View detailed information about a role."
    )
    async def roleinfo(
        self,
        ctx: commands.Context,
        role: discord.Role
    ):

        embed = discord.Embed(
            title="🎭 Role Dashboard",
            description=f"Information about {role.mention}",
            color=role.color
            if role.color.value
            else CRIMSON
        )

        embed.add_field(
            name="🎭 Role",
            value=f"{role.mention}",
            inline=True
        )

        embed.add_field(
            name="🆔 ID",
            value=f"`{role.id}`",
            inline=True
        )

        embed.add_field(
            name="👥 Members",
            value=f"`{len(role.members)}`",
            inline=True
        )

        embed.add_field(
            name="📊 Position",
            value=f"`{role.position}`",
            inline=True
        )

        embed.add_field(
            name="🎨 Color",
            value=f"`{role.color}`",
            inline=True
        )

        embed.add_field(
            name="📌 Mentionable",
            value=(
                "Yes"
                if role.mentionable
                else "No"
            ),
            inline=True
        )

        embed.add_field(
            name="📋 Hoisted",
            value=(
                "Yes"
                if role.hoist
                else "No"
            ),
            inline=True
        )

        embed.add_field(
            name="🔒 Managed",
            value=(
                "Yes"
                if role.managed
                else "No"
            ),
            inline=True
        )

        embed.add_field(
            name="📅 Created",
            value=discord.utils.format_dt(
                role.created_at,
                style="D"
            ),
            inline=True
        )

        embed.set_footer(
            text="Vexora • Role Information"
        )

        await ctx.send(embed=embed)

    # =====================================================
    # CHANNEL INFO
    # =====================================================

    @commands.hybrid_command(
        name="channelinfo",
        description="View information about a channel."
    )
    async def channelinfo(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None
    ):

        channel = channel or ctx.channel

        embed = discord.Embed(
            title="📺 Channel Dashboard",
            description=f"Information about {channel.mention}",
            color=CRIMSON
        )

        embed.add_field(
            name="📢 Channel",
            value=f"{channel.mention}",
            inline=True
        )

        embed.add_field(
            name="🆔 ID",
            value=f"`{channel.id}`",
            inline=True
        )

        embed.add_field(
            name="📂 Category",
            value=(
                channel.category.name
                if channel.category
                else "None"
            ),
            inline=True
        )

        embed.add_field(
            name="📝 Topic",
            value=(
                channel.topic
                if channel.topic
                else "No topic set"
            ),
            inline=False
        )

        embed.add_field(
            name="📅 Created",
            value=discord.utils.format_dt(
                channel.created_at,
                style="D"
            ),
            inline=True
        )

        embed.add_field(
            name="📍 Position",
            value=f"`{channel.position}`",
            inline=True
        )

        embed.set_footer(
            text="Vexora • Channel Information"
        )

        await ctx.send(embed=embed)

    # =====================================================
    # MEMBER COUNT
    # =====================================================

    @commands.hybrid_command(
        name="membercount",
        description="View the server member count."
    )
    async def membercount(
        self,
        ctx: commands.Context
    ):

        guild = ctx.guild

        humans = sum(
            1
            for member in guild.members
            if not member.bot
        )

        bots = sum(
            1
            for member in guild.members
            if member.bot
        )

        embed = discord.Embed(
            title="👥 Member Statistics",
            color=CRIMSON
        )

        embed.add_field(
            name="👥 Total",
            value=f"`{guild.member_count}`",
            inline=True
        )

        embed.add_field(
            name="👤 Humans",
            value=f"`{humans}`",
            inline=True
        )

        embed.add_field(
            name="🤖 Bots",
            value=f"`{bots}`",
            inline=True
        )

        embed.set_footer(
            text="Vexora • Utility"
        )

        await ctx.send(embed=embed)

    # =====================================================
    # SERVER ICON
    # =====================================================

    @commands.hybrid_command(
        name="servericon",
        description="View the server icon."
    )
    async def servericon(
        self,
        ctx: commands.Context
    ):

        guild = ctx.guild

        if not guild.icon:

            await ctx.send(
                "❌ This server doesn't have a server icon."
            )
            return

        embed = discord.Embed(
            title="🖼️ Server Icon",
            color=CRIMSON
        )

        embed.set_image(
            url=guild.icon.url
        )

        embed.set_footer(
            text="Vexora • Utility"
        )

        await ctx.send(embed=embed)

    # =====================================================
    # BOT INFO
    # =====================================================

    @commands.hybrid_command(
        name="botinfo",
        description="View information about Vexora."
    )
    async def botinfo(
        self,
        ctx: commands.Context
    ):

        embed = discord.Embed(
            title="🤖 Vexora",
            description=(
                "**A powerful Discord bot built "
                "for modern servers.**\n\n"
                "🛡️ Moderation\n"
                "⚙️ Utility\n"
                "🎭 Role Management\n"
                "💾 Persistent Database\n"
                "📋 Advanced Logging"
            ),
            color=CRIMSON
        )

        if self.bot.user:

            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.add_field(
            name="📦 Version",
            value="`1.0.0`",
            inline=True
        )

        embed.add_field(
            name="🌐 Servers",
            value=f"`{len(self.bot.guilds)}`",
            inline=True
        )

        embed.add_field(
            name="👥 Users",
            value=f"`{len(self.bot.users)}`",
            inline=True
        )

        embed.add_field(
            name="👨‍💻 Developer",
            value="**Potter**",
            inline=True
        )

        embed.add_field(
            name="🐍 Library",
            value="`discord.py`",
            inline=True
        )

        embed.set_footer(
            text="Vexora • Developed by Potter"
        )

        await ctx.send(embed=embed)

    # =====================================================
    # HELP
    # =====================================================

    @commands.hybrid_command(
        name="help",
        description="Open the Vexora command panel."
    )
    async def help(
        self,
        ctx: commands.Context
    ):

        view = HelpView(self.bot)

        await ctx.send(
            embed=view.home_embed(),
            view=view
        )


# =========================================================
# SETUP
# =========================================================

async def setup(bot):
    await bot.add_cog(Utility(bot))