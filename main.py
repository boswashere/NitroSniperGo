"""
Main bot entry point for NitroSniper
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands, tasks

# Local imports
from config import Settings, load_settings
from utils import Logger
import sniper
import giveaway
import invite
import privnote


class NitroSniperBot(commands.Bot):
    """Main bot class for NitroSniper"""
    
    def __init__(self, settings: Settings):
        """Initialize the bot"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        intents.dm_messages = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )
        
        self.settings = settings
        self.main_session: Optional[discord.Client] = None
        self.alt_sessions: list[discord.Client] = []
        self.start_time = None
    
    async def setup_hook(self) -> None:
        """Called before the bot connects to Discord"""
        # Load cogs
        await sniper.setup(self, self.settings)
        Logger.success("✓ Nitro sniper loaded")
        
        await giveaway.setup(self, self.settings)
        Logger.success("✓ Giveaway joiner loaded")
        
        if self.settings.invite.enable:
            await invite.setup(self, self.settings)
            Logger.success("✓ Invite sniper loaded")
        
        if self.settings.privnote.enable:
            await privnote.setup(self, self.settings)
            Logger.success("✓ Privnote sniper loaded")
    
    async def on_ready(self) -> None:
        """Called when the bot is ready"""
        if self.start_time is None:
            self.start_time = asyncio.get_event_loop().time()
            Logger.success(f"Bot logged in as {self.user}")
            Logger.success(f"Connected to {len(self.guilds)} servers")
            Logger.success(f"Watching {len(self.users)} users")
            
            # Show alt accounts
            if self.settings.tokens.alts:
                Logger.success(f"Alt accounts loaded: {len(self.settings.tokens.alts)}")
                for i, alt in enumerate(self.settings.tokens.alts, 1):
                    masked = alt[:10] + "..." + alt[-5:] if len(alt) > 15 else "***"
                    Logger.info(f"  ALT {i}: {masked}")
            
            print()
            print("=" * 60)
            print("NitroSniper 2026 - Modern Python Rewrite")
            print("=" * 60)
            print(f"✓ Main Account: {self.user}")
            print(f"✓ Alt Accounts: {len(self.settings.tokens.alts)} loaded")
            print(f"✓ Sniper Module: {'ENABLED' if self.settings.nitro else 'DISABLED'}")
            print(f"✓ Giveaway Module: {'ENABLED' if self.settings.giveaway.enable else 'DISABLED'}")
            print(f"✓ Invite Module: {'ENABLED' if self.settings.invite.enable else 'DISABLED'}")
            print(f"✓ Privnote Module: {'ENABLED' if self.settings.privnote.enable else 'DISABLED'}")
            print(f"✓ Webhook Integration: {'ENABLED' if self.settings.webhook.url else 'DISABLED'}")
            print("=" * 60)
            print()

    
    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        """Called when an error occurs"""
        Logger.error(f"Error in {event_method}: {sys.exc_info()[1]}")
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Called when a command error occurs"""
        Logger.error(f"Command error: {error}")


async def run_bot(settings: Settings) -> None:
    """Run the main bot"""
    bot = NitroSniperBot(settings)
    
    try:
        await bot.start(settings.tokens.main)
    except discord.LoginFailure:
        Logger.error("Invalid main token. Check your settings.json")
        sys.exit(1)
    except Exception as e:
        Logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


async def run_alts(settings: Settings) -> None:
    """Run alt accounts (if enabled)"""
    if not settings.tokens.alts or not settings.nitro.main_sniper:
        return
    
    for i, alt_token in enumerate(settings.tokens.alts):
        try:
            client = discord.Client(intents=discord.Intents.default())
            await client.start(alt_token)
        except discord.LoginFailure:
            Logger.error(f"Invalid alt token {i+1}. Check your settings.json")
        except Exception as e:
            Logger.error(f"Failed to start alt {i+1}: {e}")


async def main() -> None:
    """Main entry point"""
    # Load settings
    settings_file = Path("settings.json")
    
    if not settings_file.exists():
        Logger.error("settings.json not found!")
        Logger.info("Creating default settings.json...")
        
        default_settings = Settings(
            tokens={"main": "", "alts": []},
        )
        default_settings.save_to_json(settings_file)
        Logger.info("Default settings.json created. Please fill in your tokens.")
        return
    
    try:
        settings = load_settings(settings_file)
    except json.JSONDecodeError as e:
        Logger.error(f"Failed to parse settings.json: {e}")
        return
    except Exception as e:
        Logger.error(f"Failed to load settings.json: {e}")
        return
    
    # Validate settings
    if not settings.tokens.main:
        Logger.error("Main token is not configured in settings.json")
        return
    
    Logger.success("Settings loaded successfully")
    
    # Run bot
    try:
        await run_bot(settings)
    except KeyboardInterrupt:
        Logger.info("Bot shutdown requested")
    except Exception as e:
        Logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 10):
        Logger.error("Python 3.10 or higher is required")
        sys.exit(1)
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        Logger.info("Goodbye!")
