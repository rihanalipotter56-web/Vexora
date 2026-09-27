import discord
from discord.ext import commands

from core.database import (
    get_guild_settings,
    set_welcome_settings
)


CRIMSON = discord.Color.from_rgb(150, 25, 35)


def replace_variables(text, member):
    guild = member.guild

    return (
        text.replace("{user}", member.mention)
        .replace("{username}", member.name)
        .replace("{server}", guild.name)
        .replace("{membercount}", str(guild.member_count))
    )


class WelcomeBuilder(discord.ui.View):

    def __init__(self, bot, guild_id):
        super().__init__(timeout=180)

        self.bot = bot
        self.guild_id = guild_id

        self.title_text = "Welcome!"
        self.description = "Welcome {user} to **{server}**! 🎉"
        self.footer = "Vexora Welcome System"
        self.color = CRIMSON.value
        self.image_url = None
        self.thumbnail_url = None

    def build_embed(self, member=None):

        title = self.title_text
        description = self.description
        footer = self.footer

        if member:
            title = replace_variables(title, member)
            description = replace_variables(description, member)
            footer = replace_variables(footer, member)

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color(self.color)
        )

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        if self.image_url:
            embed.set_image(url=self.image_url)

        if footer:
            embed.set_footer(text=footer)

        return embed

    @discord.ui.button(
        label="Edit Message",
        emoji="📝",
        style=discord.ButtonStyle.danger
    )
    async def edit_message(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        modal = WelcomeMessageModal(self)

        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Color",
        emoji="🎨",
        style=discord.ButtonStyle.secondary
    )
    async def edit_color(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        modal = ColorModal(self)

        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Images",
        emoji="🖼️",
        style=discord.ButtonStyle.secondary
    )
    async def edit_images(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        modal = ImageModal(self)

        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Preview",
        emoji="👀",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def preview(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = self.build_embed(interaction.user)

        await interaction.response.send_message(
            content="👀 **Welcome Preview**",
            embed=embed,
            ephemeral=True
        )

    @discord.ui.button(
        label="Save",
        emoji="💾",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def save(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        set_welcome_settings(
    self.guild_id,
    message=self.description,
    title=self.title_text,
    description=self.description,
    color=self.color,
    thumbnail=self.thumbnail_url,
    image=self.image_url,
    footer=self.footer
)

        await interaction.response.send_message(
            "✅ **Welcome message saved!**",
            ephemeral=True
        )

    @discord.ui.button(
        label="Close",
        emoji="✖️",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.message.delete()


class WelcomeMessageModal(discord.ui.Modal, title="Welcome Message"):

    def __init__(self, builder):
        super().__init__()

        self.builder = builder

        self.title_input = discord.ui.TextInput(
            label="Embed Title",
            placeholder="Welcome to {server}! 🎉",
            default=builder.title_text,
            max_length=256,
            required=True
        )

        self.description_input = discord.ui.TextInput(
            label="Welcome Message",
            placeholder="Welcome {user} to {server}!",
            default=builder.description,
            style=discord.TextStyle.paragraph,
            max_length=4000,
            required=True
        )

        self.footer_input = discord.ui.TextInput(
            label="Footer",
            placeholder="Vexora Welcome System",
            default=builder.footer,
            max_length=2048,
            required=False
        )

        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.footer_input)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        self.builder.title_text = self.title_input.value
        self.builder.description = self.description_input.value
        self.builder.footer = self.footer_input.value

        await interaction.response.edit_message(
            content="🛠️ **Welcome Builder**\n\nMessage updated successfully.",
            embed=self.builder.build_embed(),
            view=self.builder
        )


class ColorModal(discord.ui.Modal, title="Embed Color"):

    def __init__(self, builder):
        super().__init__()

        self.builder = builder

        self.color_input = discord.ui.TextInput(
            label="Hex Color",
            placeholder="#96232B",
            default="#96232B",
            max_length=7,
            required=True
        )

        self.add_item(self.color_input)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        value = self.color_input.value.strip().replace("#", "")

        try:
            color = int(value, 16)

            if not 0 <= color <= 0xFFFFFF:
                raise ValueError

        except ValueError:

            await interaction.response.send_message(
                "❌ Invalid hex color. Example: `#96232B`",
                ephemeral=True
            )
            return

        self.builder.color = color

        await interaction.response.edit_message(
            content="🎨 **Embed color updated!**",
            embed=self.builder.build_embed(),
            view=self.builder
        )


class ImageModal(discord.ui.Modal, title="Welcome Images"):

    def __init__(self, builder):
        super().__init__()

        self.builder = builder

        self.thumbnail_input = discord.ui.TextInput(
            label="Thumbnail URL",
            placeholder="https://example.com/image.png",
            default=builder.thumbnail_url or "",
            required=False
        )

        self.image_input = discord.ui.TextInput(
            label="Main Image URL",
            placeholder="https://example.com/banner.png",
            default=builder.image_url or "",
            required=False
        )

        self.add_item(self.thumbnail_input)
        self.add_item(self.image_input)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        self.builder.thumbnail_url = (
            self.thumbnail_input.value.strip()
            or None
        )

        self.builder.image_url = (
            self.image_input.value.strip()
            or None
        )

        await interaction.response.edit_message(
            content="🖼️ **Images updated!**",
            embed=self.builder.build_embed(),
            view=self.builder
        )

class WelcomeConfigView(discord.ui.View):

    def __init__(self, bot, guild_id):
        super().__init__(timeout=180)

        self.bot = bot
        self.guild_id = guild_id

    @discord.ui.button(
        label="Set Channel",
        emoji="📢",
        style=discord.ButtonStyle.primary
    )
    async def set_channel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        modal = ChannelModal(self.guild_id)

        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Embed Builder",
        emoji="🎨",
        style=discord.ButtonStyle.danger
    )
    async def builder(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        view = WelcomeBuilder(
            self.bot,
            self.guild_id
        )

        await interaction.response.edit_message(
            content="🎨 **Vexora Welcome Embed Builder**",
            embed=view.build_embed(),
            view=view
        )

    @discord.ui.button(
        label="Enable",
        emoji="🟢",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def enable(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        set_welcome_settings(
            self.guild_id,
            enabled=True
        )

        await interaction.response.send_message(
            "🟢 **Welcome system enabled!**",
            ephemeral=True
        )

    @discord.ui.button(
        label="Disable",
        emoji="🔴",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def disable(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        set_welcome_settings(
            self.guild_id,
            enabled=False
        )

        await interaction.response.send_message(
            "🔴 **Welcome system disabled!**",
            ephemeral=True
        )

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
        await interaction.message.delete()

class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="welcome",
        description="Configure Vexora's welcome system."
    )
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def welcome(self, ctx: commands.Context):

        settings = get_guild_settings(ctx.guild.id)

        enabled = bool(settings[0])
        channel_id = settings[1]

        channel_text = (
            f"<#{channel_id}>"
            if channel_id
            else "Not configured"
        )

        embed = discord.Embed(
            title="👋 Vexora Welcome System",
            description=(
                "Configure your server's welcome system.\n\n"
                f"**Status:** "
                f"{'🟢 Enabled' if enabled else '🔴 Disabled'}\n"
                f"**Channel:** {channel_text}\n\n"
                "**Variables:**\n"
                "`{user}` → Member mention\n"
                "`{username}` → Username\n"
                "`{server}` → Server name\n"
                "`{membercount}` → Member count"
            ),
            color=CRIMSON
        )

        embed.set_footer(
            text="Vexora • Welcome Configuration"
        )

        view = WelcomeConfigView(self.bot, ctx.guild.id)

        await ctx.send(
            embed=embed,
            view=view
        )
      
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        settings = get_guild_settings(member.guild.id)

        enabled = bool(settings[0])
        channel_id = settings[1]

        if not enabled or not channel_id:return

        channel = member.guild.get_channel(channel_id)

        if not channel:return

        message = settings[2] or "Welcome {user} to **{server}**! 🎉"
        title = settings[3] or "Welcome!"
        description = settings[4] or message
        color = settings[5] or CRIMSON.value
        thumbnail = settings[6]
        image = settings[7]
        footer = settings[8] or "Vexora Welcome System"

        title = replace_variables(title, member)
        description = replace_variables(description, member)
        footer = replace_variables(footer, member)

        embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color(color)
    )

        if thumbnail:
           embed.set_thumbnail(url=thumbnail)

        if image:
           embed.set_image(url=image)

        if footer:
           embed.set_footer(text=footer)

        try:
           await channel.send(embed=embed)

        except discord.Forbidden:
         print(
            f"❌ Cannot send welcome message in "
            f"{channel.name}"
        )
      
    @discord.ui.button(
        label="Set Channel",
        emoji="📢",
        style=discord.ButtonStyle.primary
    )
    async def set_channel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        modal = ChannelModal(self.guild_id)

        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Embed Builder",
        emoji="🎨",
        style=discord.ButtonStyle.danger
    )
    async def builder(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        view = WelcomeBuilder(
            self.bot,
            self.guild_id
        )

        await interaction.response.edit_message(
            content="🎨 **Vexora Welcome Embed Builder**",
            embed=view.build_embed(),
            view=view
        )

    @discord.ui.button(
        label="Enable",
        emoji="🟢",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def enable(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        set_welcome_settings(
            self.guild_id,
            enabled=True
        )

        await interaction.response.send_message(
            "🟢 **Welcome system enabled!**",
            ephemeral=True
        )

    @discord.ui.button(
        label="Disable",
        emoji="🔴",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def disable(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        set_welcome_settings(
            self.guild_id,
            enabled=False
        )

        await interaction.response.send_message(
            "🔴 **Welcome system disabled!**",
            ephemeral=True
        )

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

        await interaction.message.delete()


class ChannelModal(discord.ui.Modal, title="Welcome Channel"):

    def __init__(self, guild_id):
        super().__init__()

        self.guild_id = guild_id

        self.channel_input = discord.ui.TextInput(
            label="Channel ID",
            placeholder="Enter the welcome channel ID",
            max_length=25
        )

        self.add_item(self.channel_input)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:
            channel_id = int(
                self.channel_input.value.strip()
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Invalid channel ID.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(
            channel_id
        )

        if not channel:

            await interaction.response.send_message(
                "❌ I couldn't find that channel.",
                ephemeral=True
            )
            return

        if not isinstance(
            channel,
            discord.TextChannel
        ):

            await interaction.response.send_message(
                "❌ Please select a text channel.",
                ephemeral=True
            )
            return

        set_welcome_settings(
            self.guild_id,
            channel_id=channel.id
        )

        await interaction.response.send_message(
            f"📢 Welcome channel set to {channel.mention}",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Welcome(bot))
