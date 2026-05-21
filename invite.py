"""
Invite link sniping module
"""
import asyncio
import random
import time
from typing import Optional
import discord
from discord.ext import commands

from utils import (
    Logger, HTTPClient, extract_invite_code,
    SERVER_NAME_PATTERN, send_webhook, sleep_with_jitter
)
from config import Settings


class InviteSniper(commands.Cog):
    """Cog for invite link sniping"""
    
    def __init__(self, bot: commands.Bot, settings: Settings):
        """Initialize the cog"""
        self.bot = bot
        self.settings = settings
        self.invite_count = 0
        self.sniper_running = True
        self.cooldown_end: Optional[float] = None
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listen for messages with invite links"""
        # Ignore own messages
        if message.author == self.bot.user:
            return
        
        # Check if invite sniping is enabled
        if not self.settings.invite.enable:
            return
        
        # Check if sniper is on cooldown
        if not self.sniper_running:
            if self.cooldown_end and time.time() >= self.cooldown_end:
                self.sniper_running = True
                self.invite_count = 0
                Logger.success("Invite sniper cooldown ended, resuming...")
            else:
                return
        
        # Extract invite code
        invite_code = extract_invite_code(message.content)
        if not invite_code:
            return
        
        # Use alt accounts for sniping (they have better success rate)
        if self.settings.tokens.alts:
            # Snipe with each alt account
            for i, alt_token in enumerate(self.settings.tokens.alts):
                asyncio.create_task(
                    self._snipe_with_alt(invite_code, message, alt_token, i)
                )
        else:
            # Fallback to main account with delayed join
            delay_minutes = random.randint(
                self.settings.invite.delay_min,
                self.settings.invite.delay_max
            )
            asyncio.create_task(
                self._join_with_delay(invite_code, message, delay_minutes)
            )
    
    async def _snipe_with_alt(
        self,
        invite_code: str,
        message: discord.Message,
        alt_token: str,
        alt_index: int
    ) -> None:
        """Immediately snipe server with alt account"""
        if not self.sniper_running:
            return
        
        try:
            # Small random delay to avoid detection
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            async with HTTPClient(alt_token) as client:
                response = await client.join_server(invite_code)
            
            # Check if join was successful
            if response.get("code") is not None or response.get("type") == "guild":
                server_name = response.get("guild", {}).get("name", "Unknown Server")
                
                Logger.success(f"[ALT {alt_index + 1}] Joined server: {server_name}")
                
                guild_name = message.guild.name if message.guild else "Unknown"
                channel_name = message.channel.name if hasattr(message.channel, "name") else "Unknown"
                
                # Send webhook
                if self.settings.webhook.url and not self.settings.webhook.good_only:
                    await send_webhook(
                        self.settings.webhook.url,
                        f"**ALT {alt_index + 1}** joined: {server_name}\nFrom: {guild_name}",
                        "🔗 Server Joined (ALT)",
                        0x00FF00
                    )
                
                self.invite_count += 1
                
                # Check cooldown
                if self.invite_count >= self.settings.invite.max:
                    self.sniper_running = False
                    cooldown_hours = self.settings.invite.cooldown
                    self.cooldown_end = time.time() + (cooldown_hours * 3600)
                    Logger.warning(
                        f"Max invites reached ({self.invite_count}), "
                        f"cooldown for {cooldown_hours} hours"
                    )
        
        except Exception as e:
            Logger.debug(f"[ALT {alt_index + 1}] Error joining server: {e}")
    
    async def _join_with_delay(
        self,
        invite_code: str,
        message: discord.Message,
        delay_minutes: int
    ) -> None:
        """Join server after a delay"""
        Logger.info(f"Scheduled invite join in {delay_minutes} minutes")
        
        # Add jitter to avoid detection
        await sleep_with_jitter(delay_minutes * 60, jitter_percent=0.15)
        
        # Join the server
        await self._join_server(invite_code, message)
    
    async def _join_server(
        self,
        invite_code: str,
        message: discord.Message
    ) -> None:
        """Join a server using invite code"""
        if not self.sniper_running:
            return
        
        try:
            token = self.settings.tokens.alts[0] if self.settings.tokens.alts else self.settings.tokens.main
            
            async with HTTPClient(token) as client:
                response = await client.join_server(invite_code)
            
            # Check if join was successful
            if response.get("code") is not None or response.get("type") == "guild":
                server_name = response.get("guild", {}).get("name", "Unknown Server")
                
                Logger.success(f"Joined server: {server_name}")
                
                guild_name = message.guild.name if message.guild else "Unknown"
                channel_name = message.channel.name if hasattr(message.channel, "name") else "Unknown"
                
                # Send webhook
                if self.settings.webhook.url and not self.settings.webhook.good_only:
                    await send_webhook(
                        self.settings.webhook.url,
                        f"Joined: {server_name}\nFrom: {guild_name}",
                        "Server Joined",
                        0x00FF00
                    )
                
                self.invite_count += 1
                
                # Check cooldown
                if self.invite_count >= self.settings.invite.max:
                    self.sniper_running = False
                    cooldown_hours = self.settings.invite.cooldown
                    self.cooldown_end = time.time() + (cooldown_hours * 3600)
                    Logger.warning(
                        f"Max invites reached ({self.invite_count}), "
                        f"cooldown for {cooldown_hours} hours"
                    )
            else:
                Logger.warning(f"Failed to join server: {response.get('message', 'Unknown error')}")
        
        except Exception as e:
            Logger.error(f"Error joining server: {e}")


async def setup(bot: commands.Bot, settings: Settings) -> None:
    """Setup the invite sniper cog"""
    await bot.add_cog(InviteSniper(bot, settings))
