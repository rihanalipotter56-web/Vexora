import discord
from discord import app_commands


async def handle_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ You don't have permission to use this command."

    elif isinstance(error, app_commands.BotMissingPermissions):
        message = "⚠️ I don't have the required permissions for this action."

    elif isinstance(error, app_commands.CheckFailure):
        message = "❌ You are not allowed to use this command."

    elif isinstance(error, app_commands.CommandOnCooldown):
        message = (
            f"⏳ Please wait **{error.retry_after:.1f}s** "
            "before using this again."
        )

    else:
        print(f"❌ App command error: {error}")
        message = "⚠️ Something went wrong while executing that command."

    if interaction.response.is_done():
        await interaction.followup.send(
            message,
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            message,
            ephemeral=True
        )
