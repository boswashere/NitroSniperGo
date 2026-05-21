"""
Nitro code sniping module
"""
import asyncio
import time
import json
from typing import Optional
from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks

from utils import (
    Logger, CodeCache, HTTPClient, extract_gift_code,
    NITRO_TYPE_PATTERN, send_webhook
)
from config import Settings


class NitroSniperCog(commands.Cog):
    """Cog for Nitro code sniping"""
    
    def __init__(self, bot: commands.Bot, settings: Settings):
        """Initialize the cog"""
        self.bot = bot
        self.settings = settings
        self.code_cache = CodeCache(ttl=3600)
        self.nitro_count = 0
        self.sniper_running = True
        self.cooldown_end: Optional[datetime] = None
        self.payment_source_id = "null"
        self.start_time = time.time()
        
        # Play startup sound
        asyncio.create_task(self._initialize())
    
    async def _initialize(self) -> None:
        """Initialize the cog"""
        await self.bot.wait_until_ready()
        
        # Get payment source ID
        await self._get_payment_source_id()
        
        Logger.success("Nitro sniper initialized and ready")
    
    async def _get_payment_source_id(self) -> None:
        """Get payment source ID for the main account"""
        try:
            async with HTTPClient(self.settings.tokens.main) as client:
                sources = await client.get_payment_sources()
                if sources:
                    self.payment_source_id = str(sources[0].get("id", "null"))
                    Logger.info(f"Payment source ID: {self.payment_source_id}")
        except Exception as e:
            Logger.error(f"Failed to get payment source ID: {e}")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listen for messages and snipe Nitro codes"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Check if sniper is on cooldown
        if not self.sniper_running:
            if self.cooldown_end and datetime.now() >= self.cooldown_end:
                self.sniper_running = True
                self.nitro_count = 0
                Logger.success("Nitro sniper cooldown ended, resuming...")
            else:
                return
        
        # Check if server is blacklisted
        if message.guild and message.guild.id in [int(x) for x in self.settings.blacklist_servers if x]:
            return
        
        # Extract and process Nitro code
        code = extract_gift_code(message.content)
        if not code:
            return
        
        # Check for duplicate
        if self.code_cache.exists(code):
            Logger.warning(f"Duplicate code detected: {code} from {message.author}")
            return
        
        # Validate code length
        if len(code) < 16:
            Logger.warning(f"Auto-detected fake code: {code} from {message.author}")
            return
        
        # Add to cache
        self.code_cache.add(code)
        
        # Determine which token to use
        token = self.settings.tokens.main
        use_main = self.settings.nitro.main_sniper
        
        if not use_main and message.author != self.bot.user:
            # Use alt account
            if self.settings.tokens.alts:
                token = self.settings.tokens.alts[0]
            else:
                token = self.settings.tokens.main
        
        # Redeem the code
        await self._redeem_code(code, message, token)
    
    async def _redeem_code(
        self,
        code: str,
        message: discord.Message,
        token: str
    ) -> None:
        """Redeem a Nitro code"""
        start_time = time.time()
        
        try:
            async with HTTPClient(token) as client:
                channel_id = message.channel.id if token == self.settings.tokens.main else "null"
                
                response = await client.redeem_nitro(
                    code=code,
                    channel_id=str(channel_id),
                    payment_source_id=self.payment_source_id,
                )
            
            diff_ms = (time.time() - start_time) * 1000
            
            # Parse response
            await self._handle_redeem_response(
                response, code, message, diff_ms
            )
        
        except Exception as e:
            Logger.error(f"Failed to redeem code {code}: {e}")
    
    async def _handle_redeem_response(
        self,
        response: dict,
        code: str,
        message: discord.Message,
        delay_ms: float
    ) -> None:
        """Handle the response from redeeming a code"""
        
        response_msg = response.get("message", "")
        
        if "redeemed" in response_msg:
            Logger.warning(f"Code already redeemed: {code}")
            if self.settings.webhook.url and not self.settings.webhook.good_only:
                await send_webhook(
                    self.settings.webhook.url,
                    f"Code {code} already redeemed\nDelay: {delay_ms:.1f}ms",
                    "Code Already Redeemed",
                    0xFFFF00
                )
        
        elif "nitro" in response_msg:
            # Successfully redeemed!
            nitro_type = ""
            response_str = json.dumps(response)
            
            match = NITRO_TYPE_PATTERN.search(response_str)
            if match:
                nitro_type = match.group(1).strip()
            
            self.nitro_count += 1
            
            log_msg = f"Nitro redeemed! Type: {nitro_type} | Delay: {delay_ms:.1f}ms"
            Logger.success(log_msg)
            
            # Send webhook
            if self.settings.webhook.url:
                await send_webhook(
                    self.settings.webhook.url,
                    f"Code: {code}\nType: {nitro_type}\nDelay: {delay_ms:.1f}ms",
                    "Nitro Redeemed!",
                    0x00FF00
                )
            
            # Check cooldown
            if self.nitro_count >= self.settings.nitro.max:
                self.sniper_running = False
                cooldown_hours = self.settings.nitro.cooldown
                self.cooldown_end = datetime.now() + timedelta(hours=cooldown_hours)
                Logger.warning(
                    f"Max nitro reached ({self.nitro_count}), "
                    f"cooldown for {cooldown_hours} hours"
                )
        
        elif "Unknown Gift Code" in response_msg:
            Logger.error(f"Invalid code: {code}")
            if self.settings.webhook.url and not self.settings.webhook.good_only:
                await send_webhook(
                    self.settings.webhook.url,
                    f"Code {code} is invalid",
                    "Invalid Code",
                    0xFF0000
                )
        
        else:
            Logger.debug(f"Unknown response for code {code}: {response_msg}")
            if self.settings.webhook.url and not self.settings.webhook.good_only:
                await send_webhook(
                    self.settings.webhook.url,
                    f"Unknown response: {response_msg}",
                    "Unknown Response",
                    0xFF8800
                )
    
    @tasks.loop(minutes=5)
    async def cleanup_cache(self) -> None:
        """Periodically clean up expired cache entries"""
        self.code_cache.cleanup()
    
    async def cog_load(self) -> None:
        """Called when cog is loaded"""
        self.cleanup_cache.start()
    
    async def cog_unload(self) -> None:
        """Called when cog is unloaded"""
        self.cleanup_cache.cancel()


async def setup(bot: commands.Bot, settings: Settings) -> None:
    """Setup the sniper cog"""
    await bot.add_cog(NitroSniperCog(bot, settings))
