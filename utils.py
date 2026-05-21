"""
Utility functions for NitroSniper
"""
import re
import time
import asyncio
import aiohttp
from datetime import datetime
from typing import Optional, Any
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class Logger:
    """Logging utility with timestamps and colors"""
    
    @staticmethod
    def info(message: str) -> None:
        """Log info message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.CYAN}[{timestamp}] [INFO]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def success(message: str) -> None:
        """Log success message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.GREEN}[{timestamp}] [+]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def error(message: str) -> None:
        """Log error message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.RED}[{timestamp}] [x]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def warning(message: str) -> None:
        """Log warning message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.YELLOW}[{timestamp}] [-]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def debug(message: str) -> None:
        """Log debug message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.MAGENTA}[{timestamp}] [?]{Style.RESET_ALL} {message}")


# Regex patterns for code detection and parsing
NITRO_CODE_PATTERN = re.compile(r"(discord\.com/gifts/|discordapp\.com/gifts/|discord\.gift/)([a-zA-Z0-9]+)")
PRIVNOTE_PATTERN = re.compile(r"(https://privnote\.com/[0-9A-Za-z]+)#([0-9A-Za-z]+)")
PRIVNOTE_DATA_PATTERN = re.compile(r'"data": "(.*?)",')
SERVER_NAME_PATTERN = re.compile(r'"name": "(.*?)", "splash"')
GIVEAWAY_PATTERN = re.compile(r"You won the \*\*(.+?)\*\*")
GIVEAWAY_MESSAGE_PATTERN = re.compile(r"<https://discordapp\.com/channels/(.+?)/(.+?)/(.+?)>")
PAYMENT_SOURCE_PATTERN = re.compile(r'("id": ")([0-9]+)"')
INVITE_LINK_PATTERN = re.compile(r"https://discord\.gg/([0-9a-zA-Z]+)")
NITRO_TYPE_PATTERN = re.compile(r'"name": "([ a-zA-Z]+)", "features"')


class CodeCache:
    """Thread-safe cache for codes to prevent duplicates"""
    
    def __init__(self, ttl: int = 3600):
        """Initialize cache with TTL in seconds"""
        self.cache: dict[str, float] = {}
        self.ttl = ttl
    
    def add(self, code: str) -> None:
        """Add code to cache"""
        self.cache[code] = time.time()
    
    def exists(self, code: str) -> bool:
        """Check if code exists in cache"""
        if code in self.cache:
            # Check if expired
            if time.time() - self.cache[code] < self.ttl:
                return True
            else:
                # Remove expired entry
                del self.cache[code]
                return False
        return False
    
    def cleanup(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_codes = [
            code for code, timestamp in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        for code in expired_codes:
            del self.cache[code]


class HTTPClient:
    """Async HTTP client for Discord API requests"""
    
    def __init__(self, token: str):
        """Initialize HTTP client"""
        self.token = token
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def redeem_nitro(
        self,
        code: str,
        channel_id: str = "null",
        payment_source_id: str = "null",
    ) -> dict[str, Any]:
        """Redeem a Nitro code"""
        if not self.session:
            raise RuntimeError("HTTP client not initialized")
        
        url = f"https://discordapp.com/api/v8/entitlements/gift-codes/{code}/redeem"
        headers = {
            "authorization": self.token,
            "Content-Type": "application/json",
        }
        payload = {
            "channel_id": channel_id,
            "payment_source_id": payment_source_id,
        }
        
        try:
            async with self.session.post(url, json=payload, headers=headers) as resp:
                return await resp.json()
        except Exception as e:
            Logger.error(f"Failed to redeem Nitro code: {e}")
            return {"error": str(e)}
    
    async def join_server(self, invite_code: str) -> dict[str, Any]:
        """Join a server using invite code"""
        if not self.session:
            raise RuntimeError("HTTP client not initialized")
        
        url = f"https://discord.com/api/v8/invites/{invite_code}"
        headers = {"authorization": self.token}
        
        try:
            async with self.session.post(url, headers=headers) as resp:
                return await resp.json()
        except Exception as e:
            Logger.error(f"Failed to join server: {e}")
            return {"error": str(e)}
    
    async def get_payment_sources(self) -> list[dict[str, Any]]:
        """Get payment sources for the account"""
        if not self.session:
            raise RuntimeError("HTTP client not initialized")
        
        url = "https://discord.com/api/v8/users/@me/billing/payment-sources"
        headers = {"authorization": self.token}
        
        try:
            async with self.session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data if isinstance(data, list) else []
        except Exception as e:
            Logger.error(f"Failed to get payment sources: {e}")
            return []


def extract_gift_code(text: str) -> Optional[str]:
    """Extract gift code from text"""
    match = NITRO_CODE_PATTERN.search(text)
    if match:
        code = match.group(2)
        # Validate code length (should be at least 16 chars)
        return code if len(code) >= 16 else None
    return None


def extract_invite_code(text: str) -> Optional[str]:
    """Extract invite code from text"""
    match = INVITE_LINK_PATTERN.search(text)
    return match.group(1) if match else None


def extract_privnote_link(text: str) -> Optional[tuple[str, str]]:
    """Extract privnote link and hash from text"""
    match = PRIVNOTE_PATTERN.search(text)
    if match:
        return (match.group(1), match.group(2))
    return None


def filter_matches(text: str, words: list[str], include: bool = True) -> bool:
    """Filter text by word list"""
    text_lower = text.lower()
    
    if include:  # Whitelist mode
        if not words:
            return True
        return any(word.lower() in text_lower for word in words)
    else:  # Blacklist mode
        return not any(word.lower() in text_lower for word in words)


async def send_webhook(
    webhook_url: str,
    message: str,
    title: str = "NitroSniper",
    color: int = 0x00FF00,
) -> bool:
    """Send a Discord webhook message"""
    if not webhook_url:
        return False
    
    embed = {
        "title": title,
        "description": message,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    payload = {"embeds": [embed]}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as resp:
                return resp.status in (200, 204)
    except Exception as e:
        Logger.error(f"Failed to send webhook: {e}")
        return False


async def sleep_with_jitter(base_seconds: float, jitter_percent: float = 0.1) -> None:
    """Sleep with random jitter to avoid detection"""
    jitter = base_seconds * jitter_percent
    import random
    delay = base_seconds + random.uniform(-jitter, jitter)
    await asyncio.sleep(max(0, delay))
