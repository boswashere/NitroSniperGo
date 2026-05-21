"""
Privnote sniping module
"""
import re
import base64
import aiohttp
from typing import Optional
import discord
from discord.ext import commands

from utils import (
    Logger, PRIVNOTE_PATTERN, PRIVNOTE_DATA_PATTERN,
    send_webhook
)
from config import Settings


class PrivnoteCog(commands.Cog):
    """Cog for Privnote sniping"""
    
    def __init__(self, bot: commands.Bot, settings: Settings):
        """Initialize the cog"""
        self.bot = bot
        self.settings = settings
        self.privnote_count = 0
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listen for Privnote links"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Check if privnote sniping is enabled
        if not self.settings.privnote.enable:
            return
        
        # Extract privnote link
        privnote_data = PRIVNOTE_PATTERN.search(message.content)
        if not privnote_data:
            return
        
        link = privnote_data.group(1)
        hash_val = privnote_data.group(2)
        
        # Snipe the privnote
        await self._snipe_privnote(link, hash_val, message)
    
    async def _snipe_privnote(
        self,
        link: str,
        hash_val: str,
        message: discord.Message
    ) -> None:
        """Snipe a privnote"""
        try:
            # Fetch privnote content
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    if resp.status != 200:
                        Logger.warning(f"Failed to fetch privnote: {resp.status}")
                        return
                    
                    html = await resp.text()
            
            # Extract data
            match = PRIVNOTE_DATA_PATTERN.search(html)
            if not match:
                Logger.warning("Could not extract privnote data")
                return
            
            encrypted_data = match.group(1)
            
            # Decrypt (simplified - actual decryption would be more complex)
            content = await self._decrypt_privnote(encrypted_data, hash_val)
            
            if content:
                Logger.success(f"Sniped Privnote: {content}")
                
                guild_name = message.guild.name if message.guild else "DM"
                channel_name = message.channel.name if hasattr(message.channel, "name") else "DM"
                
                # Send webhook
                if self.settings.webhook.url:
                    await send_webhook(
                        self.settings.webhook.url,
                        f"Content: {content}\nFrom: {guild_name} > {channel_name}",
                        "Privnote Sniped",
                        0x00FF00
                    )
                
                self.privnote_count += 1
        
        except Exception as e:
            Logger.error(f"Failed to snipe privnote: {e}")
    
    async def _decrypt_privnote(self, data: str, passphrase: str) -> Optional[str]:
        """Decrypt privnote data"""
        try:
            # This is a placeholder - actual decryption would use proper crypto
            decoded = base64.b64decode(data)
            # In reality, this would use AES-256 CBC decryption with proper key derivation
            return decoded.decode('utf-8', errors='ignore')
        except Exception as e:
            Logger.debug(f"Failed to decrypt privnote: {e}")
            return None


async def setup(bot: commands.Bot, settings: Settings) -> None:
    """Setup the privnote cog"""
    await bot.add_cog(PrivnoteCog(bot, settings))
