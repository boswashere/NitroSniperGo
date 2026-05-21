"""
Modern configuration for NitroSniper Python edition
"""

# Discord API settings
DISCORD_API_VERSION = "v8"
DISCORD_API_BASE = "https://discordapp.com/api"

# HTTP settings
HTTP_TIMEOUT = 10
HTTP_RETRIES = 3
USER_AGENT = "Discord Client"

# Cache settings
CACHE_TTL = 3600  # seconds
CACHE_MAX_SIZE = 10000

# Rate limiting
RATE_LIMIT_DELAY = 0.1  # seconds

# Logging
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
LOG_LEVEL = "INFO"

# Performance
MAX_CONCURRENT_REQUESTS = 50
CONNECTION_POOL_SIZE = 100

# Detection evasion
JITTER_PERCENT = 0.15  # 15% random jitter
MIN_DELAY_MS = 50
MAX_DELAY_MS = 200

# Feature flags
ENABLE_SOUND_NOTIFICATIONS = True
ENABLE_RICH_LOGGING = True
ENABLE_PERFORMANCE_METRICS = True
