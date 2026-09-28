import discord
from discord.ext import commands

from core.error_handler import handle_app_command_error


class VexoraBot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.default()

        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="v!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):

        print("⚙️ Loading Vexora systems...")

        await self.load_extension("cogs.utility")
        print("✅ Loaded: cogs.utility")

        await self.load_extension("cogs.moderation")
        print("✅ Loaded: cogs.moderation")

        await self.load_extension("cogs.role")
        print("✅ Loaded: cogs.role")

        await self.load_extension("cogs.welcome")
        print("✅ Loaded: cogs.welcome")

        await self.load_extension("cogs.nameplate")
        print("✅ Loaded: cogs.nameplate")

        await self.load_extension("cogs.embed")
        print("✅ Loaded: cogs.embed")

        await self.load_extension("cogs.settings")
        print("✅ Loaded: cogs.settings")

        await self.load_extension("cogs.logging")
        print("✅ Loaded: cogs.logging")

        await self.load_extension("cogs.automod")
        print("✅ Loaded: cogs.automod")

        await self.load_extension("cogs.counting")
        print("✅ Loaded: cogs.counting")

        # =============================================
        # GLOBAL SLASH COMMAND SYNC
        # =============================================

        print("🔄 Syncing global slash commands...")

        synced = await self.tree.sync()

        print(
            f"🌐 Global slash commands synced: {len(synced)}"
        )

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError
    ):

        await handle_app_command_error(
            interaction,
            error
        )

    async def on_ready(self):

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🤖 Logged in as: {self.user}")
        print(f"🆔 Bot ID: {self.user.id}")
        print(f"🌐 Servers: {len(self.guilds)}")
        print("🚀 Vexora is online!")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")