# Installation & Setup Guide

## Quick Start (2 minutes)

### 1. Prerequisites
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/)
- **Discord Account** - Obviously!

### 2. Clone Repository
```bash
git clone https://github.com/yourusername/NitroSniperGo.git
cd NitroSniperGo
```

### 3. Setup
```bash
# On Linux/Mac
./start.sh

# On Windows
python setup.py
```

### 4. Configure
Edit `settings.json` with your Discord tokens.

### 5. Run
```bash
python main.py
```

---

## Detailed Installation

### Step 1: Get Your Discord Token

1. Open Discord in your browser (discord.com)
2. Open DevTools (Ctrl+Shift+I on Windows/Linux, Cmd+Option+I on Mac)
3. Go to **Application** tab
4. Click **Local Storage** on the left
5. Select `https://discord.com`
6. Search for a value that starts with `Nz...` or `Mz...`
7. That's your token!

⚠️ **NEVER SHARE YOUR TOKEN!** Anyone with it can access your account.

### Step 2: Virtual Environment (Recommended)

#### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Windows (CMD):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure settings.json

Open `settings.json` and fill in:

```json
{
  "tokens": {
    "main": "YOUR_MAIN_TOKEN",
    "alts": ["ALT_TOKEN_1", "ALT_TOKEN_2"]
  }
}
```

### Step 5: Run the Bot
```bash
python main.py
```

You should see:
```
[2024-01-01 12:00:00] [INFO] Settings loaded successfully
[2024-01-01 12:00:01] [INFO] Connecting to Discord...
[2024-01-01 12:00:05] [+] Bot logged in as YourUsername#1234
```

---

## Docker Installation

### Quick Docker Setup
```bash
docker-compose up -d
```

### Manual Docker Build
```bash
# Build image
docker build -t nitrosniper .

# Run container
docker run -d \
  --name nitrosniper \
  -v $(pwd)/settings.json:/app/settings.json:ro \
  --restart unless-stopped \
  nitrosniper
```

---

## Troubleshooting

### "Python 3.10+ required"
- Install Python 3.10 or higher
- Check version: `python --version`

### "Invalid token"
- Token might be expired. Get a new one.
- Make sure you copied the entire token

### "ModuleNotFoundError: discord"
```bash
pip install -r requirements.txt
```

### "Connection refused"
- Check your internet connection
- Discord API might be down
- Check firewall settings

### Bot won't start
1. Check `settings.json` is valid JSON (use [jsonlint.com](https://jsonlint.com))
2. Verify token format
3. Check logs for errors

---

## Configuration Reference

### tokens
- `main` - Your main Discord account token
- `alts` - Array of alternative account tokens

### status
- `main` - Status for main account (online, idle, dnd, invisible)
- `alts` - Status for alt accounts

### nitro
- `max` - Max Nitro to redeem before cooldown (default: 2)
- `cooldown` - Cooldown hours after reaching max (default: 24)
- `main_sniper` - Enable sniping on main account (recommended: true)
- `delay` - Show redeem delay in logs (default: true)

### giveaway
- `enable` - Enable giveaway module (default: true)
- `delay` - Delay before reacting (seconds, default: 5)
- `dm` - Message to send to host when won (leave empty to disable)
- `dm_delay` - Delay before sending DM (seconds, default: 10)
- `blacklist_words` - Words that disable auto-join
- `whitelist_words` - Only join if contain these words (empty = all)
- `blacklist_servers` - Server IDs to ignore

### invite
- `enable` - Enable invite sniping (default: true)
- `delay.min` - Minimum join delay (minutes)
- `delay.max` - Maximum join delay (minutes)
- `max` - Max servers to join before cooldown
- `cooldown` - Cooldown hours

### webhook
- `url` - Discord webhook URL for notifications
- `good_only` - Only notify on successful actions

---

## Performance Tips

1. **Run on a VPS** - Lower latency = faster sniping
2. **Use Alt Accounts** - Better for Nitro redemption
3. **Optimize Delays** - Lower delays = faster response
4. **Monitor Cooldowns** - Respect rate limits
5. **Webhook Logging** - Track what's happening

---

## Security Tips

⚠️ **Important!**

1. **Never share your token** - It's like your password
2. **Use alt accounts** - Don't use your main for sniping
3. **Keep settings.json private** - Don't commit to Git
4. **Use Discord Bot Token** - If possible, use a bot account instead
5. **Rotate tokens** - Change tokens every few months

---

## Uninstall

### Remove Everything
```bash
# Deactivate virtual environment
deactivate

# Delete folder
rm -rf NitroSniperGo  # Linux/Mac
rmdir /s NitroSniperGo  # Windows
```

---

## Support

Having issues? 

1. Check troubleshooting section above
2. Check logs for error messages
3. Search existing issues on GitHub
4. Create new issue with detailed error info

---

Happy sniping! 🚀
