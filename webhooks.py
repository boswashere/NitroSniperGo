"""
Webhook integration module
"""
import asyncio
from datetime import datetime
from typing import Optional
import aiohttp

from utils import Logger


class WebhookManager:
    """Manage webhook notifications"""
    
    def __init__(self, webhook_url: str):
        """Initialize webhook manager"""
        self.webhook_url = webhook_url
    
    async def send_nitro_redeemed(
        self,
        code: str,
        nitro_type: str,
        delay_ms: float,
        account: str = "Main"
    ) -> bool:
        """Send webhook for redeemed Nitro"""
        embed = {
            "title": "🎉 Nitro Redeemed!",
            "description": f"**Account:** {account}\n**Code:** {code}\n**Type:** {nitro_type}",
            "fields": [
                {
                    "name": "Delay",
                    "value": f"{delay_ms:.1f}ms",
                    "inline": True
                },
                {
                    "name": "Timestamp",
                    "value": f"<t:{int(datetime.now().timestamp())}:R>",
                    "inline": True
                }
            ],
            "color": 0x00FF00,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self._send_embed(embed)
    
    async def send_giveaway_won(
        self,
        giveaway_name: str,
        guild_name: str,
        channel_name: str,
        account: str = "Main"
    ) -> bool:
        """Send webhook for won giveaway"""
        embed = {
            "title": "🎊 Giveaway Won!",
            "description": f"**Account:** {account}\n**Prize:** {giveaway_name}",
            "fields": [
                {
                    "name": "Guild",
                    "value": guild_name,
                    "inline": True
                },
                {
                    "name": "Channel",
                    "value": channel_name,
                    "inline": True
                },
                {
                    "name": "Timestamp",
                    "value": f"<t:{int(datetime.now().timestamp())}:R>",
                    "inline": True
                }
            ],
            "color": 0x00FF00,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self._send_embed(embed)
    
    async def send_server_joined(
        self,
        server_name: str,
        invite_code: str,
        account: str = "Main"
    ) -> bool:
        """Send webhook for joined server"""
        embed = {
            "title": "🔗 Server Joined",
            "description": f"**Account:** {account}\n**Server:** {server_name}",
            "fields": [
                {
                    "name": "Invite Code",
                    "value": f"`{invite_code}`",
                    "inline": True
                },
                {
                    "name": "Timestamp",
                    "value": f"<t:{int(datetime.now().timestamp())}:R>",
                    "inline": True
                }
            ],
            "color": 0x0099FF,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self._send_embed(embed)
    
    async def send_error(
        self,
        error_type: str,
        error_message: str
    ) -> bool:
        """Send webhook for error"""
        embed = {
            "title": f"❌ Error: {error_type}",
            "description": error_message,
            "color": 0xFF0000,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self._send_embed(embed)
    
    async def _send_embed(self, embed: dict) -> bool:
        """Send embed to webhook"""
        if not self.webhook_url:
            return False
        
        payload = {"embeds": [embed]}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status in (200, 204):
                        return True
                    else:
                        Logger.warning(f"Webhook request failed with status {resp.status}")
                        return False
        except asyncio.TimeoutError:
            Logger.error("Webhook request timed out")
            return False
        except Exception as e:
            Logger.error(f"Failed to send webhook: {e}")
            return False
