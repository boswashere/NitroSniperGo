"""
Test suite for NitroSniper
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

# Example tests - will be expanded


@pytest.mark.asyncio
async def test_code_extraction():
    """Test Nitro code extraction"""
    from utils import extract_gift_code
    
    # Valid codes
    assert extract_gift_code("https://discord.com/gifts/abcdefghijklmnop") == "abcdefghijklmnop"
    assert extract_gift_code("discord.gift/abcdefghijklmnop") == "abcdefghijklmnop"
    
    # Invalid codes
    assert extract_gift_code("https://discord.com/gifts/short") is None


@pytest.mark.asyncio
async def test_invite_extraction():
    """Test invite link extraction"""
    from utils import extract_invite_code
    
    # Valid invites
    assert extract_invite_code("https://discord.gg/abcdefg") == "abcdefg"
    
    # Invalid invites
    assert extract_invite_code("not a link") is None


def test_filter_matches():
    """Test filtering logic"""
    from utils import filter_matches
    
    # Whitelist
    assert filter_matches("nitro giveaway", ["nitro"], include=True) is True
    assert filter_matches("xp giveaway", ["nitro"], include=True) is False
    
    # Blacklist
    assert filter_matches("test giveaway", ["test"], include=False) is False
    assert filter_matches("nitro giveaway", ["test"], include=False) is True


def test_cache():
    """Test code cache"""
    from utils import CodeCache
    
    cache = CodeCache(ttl=60)
    
    # Add code
    cache.add("test123")
    assert cache.exists("test123") is True
    
    # Non-existent code
    assert cache.exists("notfound") is False
    
    # Cleanup
    cache.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
