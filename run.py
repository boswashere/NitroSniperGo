#!/usr/bin/env python3
"""
NitroSniper Bot - Modern Python 2026 Edition
High-performance Discord Nitro sniper and giveaway automation
"""

import sys

# Check Python version
if sys.version_info < (3, 10):
    print("❌ Python 3.10 or higher is required!")
    print(f"   Your version: {sys.version}")
    sys.exit(1)

# Start the bot
if __name__ == "__main__":
    import asyncio
    from main import main
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
