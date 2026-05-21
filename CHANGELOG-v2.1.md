# NitroSniper Configuration Updates

## New Features Added (v2.1.0)

### 🔐 Token Management from Files

#### Option 1: Environment Variables (.env)
```bash
DISCORD_TOKEN_MAIN=your_main_token_here
DISCORD_TOKENS_ALTS=alt_token_1 alt_token_2 alt_token_3
```

#### Option 2: Alt Tokens File (alts.txt)
Create `alts.txt` with one token per line:
```
alt_token_1_here
alt_token_2_here
alt_token_3_here
```

#### Option 3: settings.json (Original)
```json
{
  "tokens": {
    "main": "your_main_token",
    "alts": ["alt_token_1", "alt_token_2"]
  }
}
```

### 🚀 Improved Invite Sniping

- **Automatic Sniping**: Invite links are sniped immediately when detected
- **Multi-Alt Support**: Each alt account snipes in parallel for max coverage
- **Smart Logging**: See which alt account successfully joined servers
- **Better Success Rate**: Multiple attempts from different accounts increase chances

### 📋 Loading Priority

Tokens are loaded in this order (first match wins):
1. Environment variables (`DISCORD_TOKEN_MAIN`, `DISCORD_TOKENS_ALTS`)
2. `alts.txt` file (one token per line)
3. `settings.json` configuration

### ✨ Changes Made

- Updated `config.py` with `.env` support using `python-dotenv`
- Enhanced `invite.py` with parallel sniping via alt accounts
- Created `alts.txt` template for easy alt management
- Updated `.env.example` with new variables
- Improved logging to show alt account operations
- Added per-alt logging in invite sniping

### 🔧 Quick Start

```bash
# Option 1: Use .env file (recommended for secrets)
echo "DISCORD_TOKEN_MAIN=your_token" > .env
echo "DISCORD_TOKENS_ALTS=alt1 alt2 alt3" >> .env

# Option 2: Use alts.txt file
echo "alt_token_1" > alts.txt
echo "alt_token_2" >> alts.txt

# Run the bot
python main.py
```

### 🎯 Benefits

- **More Servers**: Multiple alts = more parallel joins
- **Better Success Rate**: Redundancy in sniping
- **Secure**: Tokens can be stored in `.env` (not committed to git)
- **Flexible**: Use files or env vars or settings.json
- **Professional**: Enterprise-grade token management

### ⚠️ Security Tips

1. Add `.env` to `.gitignore` (already done)
2. Never commit tokens to version control
3. Rotate tokens regularly
4. Use separate Discord accounts for alts
5. Monitor alt account activity
