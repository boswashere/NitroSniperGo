"""
Configuration management for NitroSniper
"""
import json
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()



@dataclass
class TokenConfig:
    """Token configuration"""
    main: str
    alts: list[str] = field(default_factory=list)


@dataclass
class StatusConfig:
    """Status configuration"""
    main: str = "online"
    alts: str = "invisible"


@dataclass
class NitroConfig:
    """Nitro sniping configuration"""
    max: int = 2
    cooldown: int = 24  # hours
    main_sniper: bool = True
    delay: bool = True


@dataclass
class GiveawayConfig:
    """Giveaway joiner configuration"""
    enable: bool = True
    delay: int = 5  # seconds
    dm: str = "Hey, I won a giveaway!"
    dm_delay: int = 10  # seconds
    blacklist_words: list[str] = field(default_factory=lambda: ["bot", "test", "ban"])
    whitelist_words: list[str] = field(default_factory=lambda: ["nitro"])
    blacklist_servers: list[str] = field(default_factory=list)


@dataclass
class InviteConfig:
    """Invite link sniping configuration"""
    enable: bool = True
    delay_min: int = 10  # minutes
    delay_max: int = 20  # minutes
    max: int = 10
    cooldown: int = 6  # hours


@dataclass
class PrivnoteConfig:
    """Privnote sniping configuration"""
    enable: bool = False


@dataclass
class WebhookConfig:
    """Webhook configuration"""
    url: str = ""
    good_only: bool = False


@dataclass
class Settings:
    """Main settings class"""
    tokens: TokenConfig
    status: StatusConfig = field(default_factory=StatusConfig)
    nitro: NitroConfig = field(default_factory=NitroConfig)
    giveaway: GiveawayConfig = field(default_factory=GiveawayConfig)
    invite: InviteConfig = field(default_factory=InviteConfig)
    privnote: PrivnoteConfig = field(default_factory=PrivnoteConfig)
    webhook: WebhookConfig = field(default_factory=WebhookConfig)
    blacklist_servers: list[str] = field(default_factory=list)

    @classmethod
    def from_json(cls, filepath: str | Path) -> "Settings":
        """Load settings from JSON file"""
        with open(filepath, "r") as f:
            data = json.load(f)
        
        return cls(
            tokens=TokenConfig(**data.get("tokens", {})),
            status=StatusConfig(**data.get("status", {})),
            nitro=NitroConfig(**data.get("nitro", {})),
            giveaway=GiveawayConfig(**data.get("giveaway", {})),
            invite=InviteConfig(**data.get("invite", {})),
            privnote=PrivnoteConfig(**data.get("privnote", {})),
            webhook=WebhookConfig(**data.get("webhook", {})),
            blacklist_servers=data.get("blacklist_servers", []),
        )

    def save_to_json(self, filepath: str | Path) -> None:
        """Save settings to JSON file"""
        data = {
            "tokens": {
                "main": self.tokens.main,
                "alts": self.tokens.alts,
            },
            "status": {
                "main": self.status.main,
                "alts": self.status.alts,
            },
            "nitro": {
                "max": self.nitro.max,
                "cooldown": self.nitro.cooldown,
                "main_sniper": self.nitro.main_sniper,
                "delay": self.nitro.delay,
            },
            "giveaway": {
                "enable": self.giveaway.enable,
                "delay": self.giveaway.delay,
                "dm": self.giveaway.dm,
                "dm_delay": self.giveaway.dm_delay,
                "blacklist_words": self.giveaway.blacklist_words,
                "whitelist_words": self.giveaway.whitelist_words,
                "blacklist_servers": self.giveaway.blacklist_servers,
            },
            "invite": {
                "enable": self.invite.enable,
                "delay": {
                    "min": self.invite.delay_min,
                    "max": self.invite.delay_max,
                },
                "max": self.invite.max,
                "cooldown": self.invite.cooldown,
            },
            "privnote": {
                "enable": self.privnote.enable,
            },
            "webhook": {
                "url": self.webhook.url,
                "good_only": self.webhook.good_only,
            },
            "blacklist_servers": self.blacklist_servers,
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)


def load_settings(filepath: str | Path = "settings.json") -> Settings:
    """Load settings from file, with env variable fallbacks"""
    settings = Settings.from_json(filepath)
    
    # Override with environment variables if set
    if os.getenv("DISCORD_TOKEN_MAIN"):
        settings.tokens.main = os.getenv("DISCORD_TOKEN_MAIN", "")
    
    # Load alts from alts.txt if file exists
    alts_file = Path("alts.txt")
    if alts_file.exists():
        with open(alts_file, "r") as f:
            alts = [line.strip() for line in f if line.strip()]
            if alts:
                settings.tokens.alts = alts
    
    # Override with env variable if set (space-separated or comma-separated)
    if os.getenv("DISCORD_TOKENS_ALTS"):
        alts_env = os.getenv("DISCORD_TOKENS_ALTS", "")
        alts = [token.strip() for token in alts_env.replace(",", " ").split() if token.strip()]
        if alts:
            settings.tokens.alts = alts
    
    return settings

