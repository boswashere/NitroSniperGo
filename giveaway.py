"""
Giveaway joiner module
"""
import asyncio
import json
import re
from typing import Optional
import discord
from discord.ext import commands

from utils import (
    Logger, GIVEAWAY_PATTERN, GIVEAWAY_MESSAGE_PATTERN,
    filter_matches, send_webhook, sleep_with_jitter
)
from config import Settings


class GiveawayCog(commands.Cog):
    """Cog for giveaway joining"""
    
    def __init__(self, bot: commands.Bot, settings: Settings):
        """Initialize the cog"""
        self.bot = bot
        self.settings = settings
        self.giveaway_count = 0
    
    async def _find_giveaway_host(
        self,
        channel: discord.TextChannel,
        giveaway_message_id: str
    ) -> Optional[int]:
        """Find the host of a giveaway"""
        try:
            giveaway_message = await channel.fetch_message(int(giveaway_message_id))
            
            # Search for host in surrounding messages
            async for message in channel.history(limit=100):
                if "Hosted by:" in message.content:
                    # Extract host ID using regex
                    match = re.search(r"<@!?(\d+)>", message.content)
                    if match:
                        return int(match.group(1))
        
        except Exception as e:
            Logger.debug(f"Failed to find giveaway host: {e}")
        
        return None
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listen for giveaway messages"""
        # Ignore bot messages and own messages
        if message.author.bot or message.author == self.bot.user:
            return
        
        # Check if giveaway module is enabled
        if not self.settings.giveaway.enable:
            return
        
        # Check if server is blacklisted
        if message.guild and message.guild.id in [
            int(x) for x in self.settings.giveaway.blacklist_servers if x
        ]:
            return
        
        # Check if it's a giveaway message
        if not self._is_giveaway_message(message.content):
            return
        
        # Apply filters
        if not filter_matches(
            message.content,
            self.settings.giveaway.blacklist_words,
            include=False
        ):
            Logger.debug(f"Giveaway filtered by blacklist")
            return
        
        if not filter_matches(
            message.content,
            self.settings.giveaway.whitelist_words,
            include=True
        ):
            Logger.debug(f"Giveaway filtered by whitelist")
            return
        
        # Join the giveaway
        await self._join_giveaway(message)
    
    def _is_giveaway_message(self, content: str) -> bool:
        """Check if message is a giveaway message"""
        # Common giveaway indicators
        indicators = [
            "🎉",
            "**GIVEAWAY**",
            "giveaway",
            "reaction",
            "react",
        ]
        
        content_lower = content.lower()
        return any(ind.lower() in content_lower for ind in indicators)
    
    async def _join_giveaway(self, message: discord.Message) -> None:
        """Join a giveaway"""
        try:
            # Add reaction
            await message.add_reaction("🎉")
            
            guild_name = message.guild.name if message.guild else "DM"
            channel_name = message.channel.name if hasattr(message.channel, "name") else "DM"
            
            Logger.info(f"Joined giveaway in {guild_name} > {channel_name}")
            
            # Send webhook
            if self.settings.webhook.url and not self.settings.webhook.good_only:
                await send_webhook(
                    self.settings.webhook.url,
                    f"Joined giveaway in {guild_name}\nChannel: {channel_name}",
                    "Giveaway Joined",
                    0x0080FF
                )
            
            self.giveaway_count += 1
        
        except Exception as e:
            Logger.error(f"Failed to join giveaway: {e}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        """Listen for giveaway win messages"""
        # Check if it's a win message
        if "won" in after.content.lower() and "giveaway" in after.content.lower():
            await self._handle_giveaway_win(after)
    
    async def _handle_giveaway_win(self, message: discord.Message) -> None:
        """Handle a giveaway win message"""
        # Extract giveaway details
        match = GIVEAWAY_PATTERN.search(message.content)
        giveaway_name = match.group(1) if match else "Unknown"
        
        guild_name = message.guild.name if message.guild else "DM"
        channel_name = message.channel.name if hasattr(message.channel, "name") else "DM"
        
        Logger.success(f"Won giveaway: {giveaway_name} in {guild_name} > {channel_name}")
        
        # Send webhook
        if self.settings.webhook.url:
            await send_webhook(
                self.settings.webhook.url,
                f"Won: {giveaway_name}\nGuild: {guild_name}\nChannel: {channel_name}",
                "Giveaway Won!",
                0x00FF00
            )
        
        # Send DM to host if configured
        if self.settings.giveaway.dm:
            await self._dm_giveaway_host(message)
    
    async def _dm_giveaway_host(self, message: discord.Message) -> None:
        """Send DM to giveaway host"""
        try:
            # Find host
            host_id = await self._find_giveaway_host(message.channel, message.id)
            
            if not host_id:
                Logger.warning("Could not find giveaway host")
                return
            
            # Wait before sending DM
            await asyncio.sleep(self.settings.giveaway.dm_delay)
            
            # Send DM
            host = await self.bot.fetch_user(host_id)
            await host.send(self.settings.giveaway.dm)
            
            Logger.success(f"Sent DM to giveaway host: {host}")
        
        except Exception as e:
            Logger.error(f"Failed to DM giveaway host: {e}")


async def setup(bot: commands.Bot, settings: Settings) -> None:
    """Setup the giveaway cog"""
    await bot.add_cog(GiveawayCog(bot, settings))
