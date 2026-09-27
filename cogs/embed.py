import discord
from discord.ext import commands
from discord.ui import View, Modal, TextInput, Select, Button


CRIMSON = discord.Color.from_rgb(150, 25, 35)


# =========================
# EMBED DATA
# =========================

class EmbedData:

    def __init__(self):
        self.title = ""
        self.description = ""
        self.color = CRIMSON

        self.thumbnail = ""
        self.image = ""

        self.author = ""
        self.footer = ""
        self.url = ""

        self.fields = []


# =========================
# EMBED BUILDER
# =========================

def build_embed(data: EmbedData):

    embed = discord.Embed(
        title=data.title or None,
        description=data.description or None,
        color=data.color,
        url=data.url or None
    )

    if data.author:
        embed.set_author(name=data.author)

    if data.thumbnail:
        embed.set_thumbnail(url=data.thumbnail)

    if data.image:
        embed.set_image(url=data.image)

    if data.footer:
        embed.set_footer(text=data.footer)

    for name, value, inline in data.fields:
        embed.add_field(
            name=name,
            value=value,
            inline=inline
        )

    return embed


# =========================
# BASIC MODAL
# =========================

class BasicEmbedModal(Modal, title="📝 Basic Embed Settings"):

    title_input = TextInput(
        label="Title",
        placeholder="Enter your embed title...",
        required=False,
        max_length=256
    )

    description_input = TextInput(
        label="Description",
        placeholder="Write your embed description...",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=4000
    )

    color_input = TextInput(
        label="HEX Color",
        placeholder="#961923",
        required=False,
        max_length=7
    )

    url_input = TextInput(
        label="Embed URL",
        placeholder="https://example.com",
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):

        view = self.view

        view.data.title = self.title_input.value
        view.data.description = self.description_input.value
        view.data.url = self.url_input.value

        color = self.color_input.value.strip()

        if color:

            if color.startswith("#"):
                color = color[1:]

            try:
                if len(color) != 6:
                    raise ValueError

                view.data.color = discord.Color(
                    int(color, 16)
                )

            except ValueError:

                await interaction.response.send_message(
                    "❌ Invalid HEX color.\n\n"
                    "Example: `#961923`",
                    ephemeral=True
                )

                return

        await interaction.response.edit_message(
            content="",
            embed=build_embed(view.data),
            view=view
        )


# =========================
# MEDIA MODAL
# =========================

class MediaEmbedModal(Modal, title="🖼️ Media & Branding"):

    thumbnail_input = TextInput(
        label="Thumbnail URL",
        placeholder="https://...",
        required=False,
        max_length=500
    )

    image_input = TextInput(
        label="Image URL",
        placeholder="https://...",
        required=False,
        max_length=500
    )

    author_input = TextInput(
        label="Author Name",
        placeholder="Example: Vexora",
        required=False,
        max_length=256
    )

    footer_input = TextInput(
        label="Footer",
        placeholder="Example: Vexora • Developed by Potter",
        required=False,
        max_length=2048
    )

    async def on_submit(self, interaction: discord.Interaction):

        view = self.view

        view.data.thumbnail = self.thumbnail_input.value
        view.data.image = self.image_input.value
        view.data.author = self.author_input.value
        view.data.footer = self.footer_input.value

        await interaction.response.edit_message(
            embed=build_embed(view.data),
            view=view
        )


# =========================
# FIELD MODAL
# =========================

class FieldModal(Modal, title="📑 Add Embed Field"):

    name_input = TextInput(
        label="Field Name",
        placeholder="Example: Rules",
        max_length=256
    )

    value_input = TextInput(
        label="Field Content",
        placeholder="Enter field content...",
        style=discord.TextStyle.paragraph,
        max_length=1024
    )

    inline_input = TextInput(
        label="Inline",
        placeholder="yes / no",
        default="yes",
        required=False,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):

        view = self.view

        if len(view.data.fields) >= 5:

            await interaction.response.send_message(
                "❌ You can add a maximum of **5 fields**.",
                ephemeral=True
            )

            return

        inline = (
            self.inline_input.value.lower()
            in ("yes", "y", "true")
        )

        view.data.fields.append(
            (
                self.name_input.value,
                self.value_input.value,
                inline
            )
        )

        await interaction.response.edit_message(
            embed=build_embed(view.data),
            view=view
        )


# =========================
# EMOJI SELECT
# =========================

class EmojiSelect(Select):

    def __init__(self, builder_view):

        self.builder_view = builder_view

        guild = builder_view.guild

        emojis = [
            emoji
            for emoji in guild.emojis
            if emoji.available
        ]

        options = []

        # Unicode / normal emoji presets
        presets = [
            ("🔥 Fire", "🔥"),
            ("🎉 Party", "🎉"),
            ("✨ Sparkles", "✨"),
            ("✅ Check", "✅"),
            ("❌ Cross", "❌"),
            ("⚡ Lightning", "⚡"),
            ("🛡️ Shield", "🛡️"),
            ("❤️ Heart", "❤️"),
        ]

        for name, emoji in presets:
            options.append(
                discord.SelectOption(
                    label=name,
                    value=emoji,
                    description="Insert this emoji"
                )
            )

        # Server custom emojis
        for emoji in emojis[:12]:

            emoji_text = str(emoji)

            options.append(
                discord.SelectOption(
                    label=emoji.name[:100],
                    value=emoji_text,
                    description="Server custom emoji"
                )
            )

        super().__init__(
            placeholder="😀 Select an emoji...",
            options=options[:25],
            min_values=1,
            max_values=1,
            row=0
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        emoji = self.values[0]

        await interaction.response.send_message(
            f"😀 **Emoji:** {emoji}\n\n"
            "Copy it into your title, description, "
            "field or footer.",
            ephemeral=True
        )


# =========================
# EMOJI VIEW
# =========================

class EmojiView(View):

    def __init__(self, builder_view):

        super().__init__(timeout=120)

        self.add_item(
            EmojiSelect(builder_view)
        )


# =========================
# MAIN BUILDER
# =========================

class EmbedBuilderView(View):

    def __init__(self, author_id, guild):

        super().__init__(timeout=600)

        self.author_id = author_id
        self.guild = guild

        self.data = EmbedData()

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(
                "🔒 This embed builder belongs to "
                "another administrator.",
                ephemeral=True
            )

            return False

        return True

    # =====================
    # BASIC
    # =====================

    @discord.ui.button(
        label="Basic",
        emoji="📝",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def basic(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        modal = BasicEmbedModal()
        modal.view = self

        await interaction.response.send_modal(modal)

    # =====================
    # MEDIA
    # =====================

    @discord.ui.button(
        label="Media",
        emoji="🖼️",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def media(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        modal = MediaEmbedModal()
        modal.view = self

        await interaction.response.send_modal(modal)

    # =====================
    # FIELD
    # =====================

    @discord.ui.button(
        label="Field",
        emoji="📑",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def add_field(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        modal = FieldModal()
        modal.view = self

        await interaction.response.send_modal(modal)

    # =====================
    # EMOJI
    # =====================

    @discord.ui.button(
        label="Emoji",
        emoji="😀",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def emoji_picker(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "😀 **Vexora Emoji Picker**\n\n"
            "Choose an emoji to use in your embed.",
            view=EmojiView(self),
            ephemeral=True
        )

    # =====================
    # SEND
    # =====================

    @discord.ui.button(
        label="Send",
        emoji="📤",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def send_embed(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if (
            not self.data.title
            and not self.data.description
            and not self.data.fields
        ):

            await interaction.response.send_message(
                "❌ Your embed is empty.\n"
                "Add a title, description or field first.",
                ephemeral=True
            )

            return

        embed = build_embed(self.data)

        try:

            await interaction.channel.send(
                embed=embed
            )

            await interaction.response.send_message(
                "✅ **Embed sent successfully!**",
                ephemeral=True
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ I don't have permission to send "
                "embeds in this channel.",
                ephemeral=True
            )

    # =====================
    # RESET
    # =====================

    @discord.ui.button(
        label="Reset",
        emoji="🔄",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def reset(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.data = EmbedData()

        await interaction.response.edit_message(
            content="",
            embed=build_embed(self.data),
            view=self
        )

    # =====================
    # CLOSE
    # =====================

    @discord.ui.button(
        label="Close",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.message.delete()


# =========================
# EMBED COG
# =========================

class Embed(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    @commands.hybrid_command(
        name="embed",
        description="Create a custom Discord embed."
    )
    @commands.has_permissions(
        administrator=True
    )
    async def embed(
        self,
        ctx: commands.Context
    ):

        view = EmbedBuilderView(
            ctx.author.id,
            ctx.guild
        )

        preview = build_embed(
            view.data
        )

        preview.title = "🎨 Vexora Embed Builder"

        preview.description = (
            "**Create your custom embed using the "
            "controls below.**\n\n"

            "📝 **Basic**\n"
            "Title • Description • Color • URL\n\n"

            "🖼️ **Media**\n"
            "Images • Thumbnail • Author • Footer\n\n"

            "📑 **Field**\n"
            "Add information sections\n\n"

            "😀 **Emoji**\n"
            "Use Unicode or server emojis\n\n"

            "📤 **Send** when you're finished."
        )

        preview.color = CRIMSON

        preview.set_footer(
            text="Vexora • Custom Embed System • Developed by Potter"
        )

        await ctx.send(
            embed=preview,
            view=view
        )


async def setup(bot):

    await bot.add_cog(
        Embed(bot)
    )