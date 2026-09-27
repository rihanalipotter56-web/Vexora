import discord
from discord.ext import commands
from discord.ui import Select, Button, View


CRIMSON = discord.Color.from_rgb(150, 25, 35)


class NameplateView(View):

    FONTS = {
        "Default": "11",
        "Tempo": "1",
        "Sakura": "3",
        "Jellybean": "4",
        "Modern": "6",
        "Medieval": "7",
        "8Bit": "8",
        "Vampyre": "10",
    }

    EFFECTS = {
        "None": "0",
        "Solid": "1",
        "Gradient": "2",
        "Neon": "3",
        "Toon": "4",
        "Pop": "5",
        "Glow": "6",
    }

    COLORS = {
        "Pink": "16738740",
        "Red": "16711680",
        "Purple": "9115620",
        "Blue": "3447003",
        "Cyan": "1752220",
        "Green": "5763719",
        "Yellow": "16705372",
        "Orange": "16738816",
        "White": "16777215",
        "Black": "0",
        "Gold": "16766720",
        "Violet": "15627106",
    }

    def __init__(self, cog):
        super().__init__(timeout=300)

        self.cog = cog

        self.selected_font = "3"
        self.selected_effect = "6"
        self.selected_color = "16738740"

        self.add_item(FontSelect(self))
        self.add_item(EffectSelect(self))
        self.add_item(ColorSelect(self))
        self.add_item(ApplyButton(self))
        self.add_item(RemoveButton(self))


class FontSelect(Select):

    def __init__(self, view):

        self.parent_view = view

        options = [
            discord.SelectOption(
                label=name,
                value=value,
                description=f"{name} font"
            )
            for name, value in view.FONTS.items()
        ]

        super().__init__(
            placeholder="Select a font...",
            options=options,
            min_values=1,
            max_values=1,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):

        self.parent_view.selected_font = self.values[0]

        await interaction.response.send_message(
            f"🔤 Font selected: **{self.values[0]}**",
            ephemeral=True
        )


class EffectSelect(Select):

    def __init__(self, view):

        self.parent_view = view

        options = [
            discord.SelectOption(
                label=name,
                value=value,
                description=f"{name} effect"
            )
            for name, value in view.EFFECTS.items()
        ]

        super().__init__(
            placeholder="Select an effect...",
            options=options,
            min_values=1,
            max_values=1,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):

        self.parent_view.selected_effect = self.values[0]

        await interaction.response.send_message(
            f"✨ Effect selected: **{self.values[0]}**",
            ephemeral=True
        )


class ColorSelect(Select):

    def __init__(self, view):

        self.parent_view = view

        options = [
            discord.SelectOption(
                label=name,
                value=value,
                description=f"{name} color"
            )
            for name, value in view.COLORS.items()
        ]

        super().__init__(
            placeholder="Select a color...",
            options=options,
            min_values=1,
            max_values=1,
            row=2
        )

    async def callback(self, interaction: discord.Interaction):

        self.parent_view.selected_color = self.values[0]

        await interaction.response.send_message(
            f"🎨 Color selected: **{self.values[0]}**",
            ephemeral=True
        )


class ApplyButton(Button):

    def __init__(self, view):

        self.parent_view = view

        super().__init__(
            label="Save & Apply",
            emoji="💾",
            style=discord.ButtonStyle.success,
            row=3
        )

    async def callback(self, interaction: discord.Interaction):

        view = self.parent_view

        await interaction.response.defer(ephemeral=True)

        success, message = await view.cog.apply_nameplate(
            interaction.guild.id,
            view.selected_font,
            view.selected_effect,
            [view.selected_color]
        )

        if success:

            embed = discord.Embed(
                title="✅ Vexora Nameplate",
                description=(
                    "The selected nameplate configuration "
                    "was sent to Discord.\n\n"
                    f"🔤 **Font:** `{view.selected_font}`\n"
                    f"✨ **Effect:** `{view.selected_effect}`\n"
                    f"🎨 **Color:** `{view.selected_color}`"
                ),
                color=CRIMSON
            )

            embed.set_footer(
                text="Vexora • Nameplate System"
            )

            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )

        else:

            await interaction.followup.send(
                f"❌ {message}",
                ephemeral=True
            )


class RemoveButton(Button):

    def __init__(self, view):

        self.parent_view = view

        super().__init__(
            label="Remove Style",
            emoji="🗑️",
            style=discord.ButtonStyle.danger,
            row=3
        )

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        success, message = await self.parent_view.cog.remove_nameplate(
            interaction.guild.id
        )

        if success:

            await interaction.followup.send(
                "✅ **Vexora nameplate style removed.**",
                ephemeral=True
            )

        else:

            await interaction.followup.send(
                f"❌ {message}",
                ephemeral=True
            )


class Nameplate(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def apply_nameplate(
        self,
        guild_id,
        font_id,
        effect_id,
        colors
    ):
        """
        Attempts to apply Discord Display Name Style
        using the current guild-member endpoint.
        """

        try:

            route = discord.http.Route(
                "PATCH",
                f"/guilds/{guild_id}/members/@me"
            )

            payload = {
                "display_name_font_id": int(font_id),
                "display_name_effect_id": int(effect_id),
                "display_name_colors": [
                    int(color)
                    for color in colors
                ],
            }

            await self.bot.http.request(
                route,
                json=payload
            )

            print(
                f"Vexora nameplate request: {payload}"
            )

            return True, "Nameplate request completed."

        except discord.Forbidden:

            return (
                False,
                "Discord denied the nameplate request."
            )

        except discord.HTTPException as error:

            return (
                False,
                f"Discord returned an HTTP error: {error}"
            )

        except Exception as error:

            return (
                False,
                f"Unexpected error: {error}"
            )

    async def remove_nameplate(self, guild_id):

        try:

            route = discord.http.Route(
                "PATCH",
                f"/guilds/{guild_id}/members/@me"
            )

            payload = {
                "display_name_font_id": 0,
                "display_name_effect_id": 0,
                "display_name_colors": [],
            }

            await self.bot.http.request(
                route,
                json=payload
            )

            return True, "Style removed."

        except discord.Forbidden:

            return (
                False,
                "Discord denied the request."
            )

        except discord.HTTPException as error:

            return (
                False,
                f"Discord returned an HTTP error: {error}"
            )

        except Exception as error:

            return (
                False,
                f"Unexpected error: {error}"
            )

    @commands.hybrid_command(
        name="nameplate",
        description="Customize Vexora's display name style."
    )
    @commands.has_permissions(administrator=True)
    async def nameplate(
        self,
        ctx: commands.Context
    ):

        embed = discord.Embed(
            title="🎨 Vexora Nameplate",
            description=(
                "**Customize Vexora's display name style.**\n\n"
                "🔤 **Font**\n"
                "Choose the display font.\n\n"
                "✨ **Effect**\n"
                "Choose the display effect.\n\n"
                "🎨 **Color**\n"
                "Choose the display color.\n\n"
                "Then press **Save & Apply**."
            ),
            color=CRIMSON
        )

        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )

        embed.set_footer(
            text="Vexora • Developed by Potter"
        )

        view = NameplateView(self)

        await ctx.send(
            embed=embed,
            view=view
        )

    @commands.hybrid_command(
        name="removeplate",
        description="Remove Vexora's display name style."
    )
    @commands.has_permissions(administrator=True)
    async def removeplate(
        self,
        ctx: commands.Context
    ):

        success, message = await self.remove_nameplate(
            ctx.guild.id
        )

        if success:

            embed = discord.Embed(
                title="🗑️ Nameplate Removed",
                description=(
                    "Vexora's display name style "
                    "has been reset."
                ),
                color=CRIMSON
            )

            embed.set_footer(
                text="Vexora • Nameplate System"
            )

            await ctx.send(embed=embed)

        else:

            await ctx.send(
                f"❌ {message}"
            )


async def setup(bot):
    await bot.add_cog(Nameplate(bot))