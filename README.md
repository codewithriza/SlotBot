<div align="center">

# 🎰 SlotBot

### The ultimate Discord bot for seamless slot management

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![discord.py](https://img.shields.io/badge/discord.py-2.3+-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/codewithriza/SlotBot?style=for-the-badge&color=yellow)](https://github.com/codewithriza/SlotBot/stargazers)
[![Issues](https://img.shields.io/github/issues/codewithriza/SlotBot?style=for-the-badge)](https://github.com/codewithriza/SlotBot/issues)

<br/>

<a href="https://drive.google.com/file/d/1ESOROJ6V65hZ3IOk70nerMaDbOmP12UQ/view">
  <img src="https://github.com/codewithriza/SlotBot/blob/main/image/banner.png" alt="SlotBot Banner" width="700">
</a>

<br/>

*Click the banner above to watch the setup tutorial!*

<br/>

[Features](#-features) •
[Quick Start](#-quick-start) •
[Configuration](#-configuration) •
[Commands](#-commands) •
[Contributing](#-contributing) •
[Support](#-support)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎰 **Slot Creation** | Create slots with custom durations (days/months), categories, and ping limits |
| 🔄 **Slot Renewal** | Renew existing slots with new durations seamlessly |
| ⏳ **Slot Extension** | Extend slot duration without resetting the channel |
| 🔀 **Slot Transfer** | Transfer slot ownership between users |
| ⏸️ **Hold / Unhold** | Temporarily freeze slots during investigations |
| 🚫 **Slot Revocation** | Revoke slots with automatic role & permission cleanup |
| 📢 **Ping Management** | Configurable ping counts with automatic 24-hour resets + cooldowns |
| ⏰ **Auto-Expiry** | Background task automatically expires and locks slots hourly |
| ⚠️ **Warning System** | Warn slot owners with DM notifications and tracking |
| 🚫 **Blacklist System** | Blacklist users from receiving slots with auto-revocation |
| 📊 **Advanced Statistics** | Detailed stats with progress bars, 24h activity, warnings, and more |
| 🏆 **Leaderboard** | Rank slots by remaining time with medal display |
| 📜 **Activity History** | Track all slot actions with timestamps |
| 📋 **Audit Logging** | All actions logged to a dedicated channel and log file |
| 🔧 **Setup Wizard** | Interactive first-time configuration command |
| ⚡ **Slash Commands** | Modern Discord slash commands alongside prefix commands |
| 🛡️ **Role-Based Access** | Staff-only commands with proper permission checks |
| ⚠️ **Error Handling** | Graceful error handling with cooldown support |
| 💣 **Nuke Command** | Clear slot channels while preserving bot embeds |
| 📢 **Announcements** | Staff can send formatted announcement embeds |
| 🏠 **Server Info** | Detailed server information display |
| ⏱️ **Uptime Tracking** | Real-time bot uptime monitoring |
| 🎫 **Ticket System** | Create support tickets with buttons, auto-transcripts on close, DM delivery |
| 🎟️ **Redeem Codes** | Generate redeemable codes that auto-create slots with set duration/pings |

---

## 🚀 Quick Start

### Step 1: Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** → give it a name → click **"Create"**
3. Go to the **"Bot"** tab → click **"Add Bot"**
4. Under **"Privileged Gateway Intents"**, enable:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Click **"Reset Token"** → copy the token (you'll need it later)

### Step 2: Invite the Bot

1. Go to **"OAuth2"** → **"URL Generator"**
2. Select scopes: `bot`, `applications.commands`
3. Select permissions: `Administrator`
4. Copy the generated URL and open it in your browser
5. Select your server and authorize

### Step 3: Set Up Your Server

Create these in your Discord server:
- **2 Categories** for slot channels (e.g., "Slots Category 1" and "Slots Category 2")
- **1 Staff Role** for bot managers
- **1 Premium/Buyer Role** for slot holders
- **1 Slot Role** (additional role for slot holders)
- **1 Log Channel** for audit logs (optional but recommended)

> 💡 **Tip:** Enable Developer Mode in Discord (`Settings → Advanced → Developer Mode`) to copy IDs by right-clicking.

### Step 4: Install & Run

```bash
# Clone the repository
git clone https://github.com/codewithriza/SlotBot.git
cd SlotBot

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure the bot (see next section)
# Then run:
python3 main.py
```

### Step 5: Use the Setup Wizard

Once the bot is running with just the token set, use the **setup wizard** in Discord:
```
,setup
```
This will interactively ask you for all the IDs and save them to `config.json`!

---

## ⚙️ Configuration

Edit `config.json` with your values:

```json
{
    "token": "YOUR_BOT_TOKEN_HERE",
    "prefix": ",",
    "staffrole": 123456789,
    "premiumeroleid": 123456789,
    "guildid": 123456789,
    "categoryid_1": 123456789,
    "categoryid_2": 123456789,
    "slot_role_id": 123456789,
    "log_channel_id": 123456789,
    "default_ping_count": 3,
    "ping_reset_hours": 24
}
```

| Key | Description | Required |
|-----|-------------|----------|
| `token` | Your Discord bot token | ✅ |
| `prefix` | Command prefix (default: `,`) | ✅ |
| `staffrole` | Staff role ID | ✅ |
| `premiumeroleid` | Premium/buyer role ID | ✅ |
| `guildid` | Your server ID | ✅ |
| `categoryid_1` | First slot category ID | ✅ |
| `categoryid_2` | Second slot category ID | ✅ |
| `slot_role_id` | Slot holder role ID | ✅ |
| `log_channel_id` | Audit log channel ID | Optional |
| `default_ping_count` | Default pings per slot | Optional |
| `ping_reset_hours` | Hours between ping resets | Optional |
| `ticket_category_id` | Category ID for ticket channels | Optional |

### 🔐 Token Security

**Option 1:** Set in `config.json` (keep the file private!)
```json
{ "token": "your_token_here" }
```

**Option 2:** Environment variable (recommended for production)
```bash
export SLOTBOT_TOKEN="your_token_here"
python3 main.py
```

> [!IMPORTANT]
> **Never commit your bot token to Git!** The `.gitignore` is configured to protect sensitive files.

---

## 🎮 Commands

### 🛡️ Staff Commands

| Command | Description | Example |
|---------|-------------|---------|
| `,create` | Create a new slot | `,create @user 7 d 3 category1 Shop` |
| `,renew` | Renew an existing slot | `,renew @user #channel 30 d` |
| `,extend` | Extend slot duration | `,extend @user 7 d` |
| `,transfer` | Transfer slot ownership | `,transfer @from @to` |
| `,revoke` | Revoke a user's slot | `,revoke @user #channel` |
| `,hold` | Put slot on hold | `,hold` |
| `,unhold` | Remove hold | `,unhold` |
| `,add` | Add slot role | `,add @user` |
| `,remove` | Remove slot role | `,remove @user` |
| `,delete` | Delete slot channel | `,delete` |
| `,warn` | Warn a slot owner | `,warn @user Inactive` |
| `,blacklist` | Blacklist a user | `,blacklist @user Scammer` |
| `,unblacklist` | Remove from blacklist | `,unblacklist @user` |
| `,slotinfo` | View slot details | `,slotinfo #channel` |
| `,slots` | List all slots | `,slots` |
| `,announce` | Send announcement | `,announce Sale today!` |
| `,setup` | Setup wizard | `,setup` |
| `,ticket` | Send ticket panel with button | `,ticket` |
| `,closeticket` | Close current ticket | `,closeticket` |
| `,createredeem` | Create a redeem code | `,createredeem 7 d 3 category1 1` |
| `,redeems` | List all redeem codes | `,redeems` |
| `,deleteredeem` | Delete a redeem code | `,deleteredeem CODE` |

### 👤 User Commands

| Command | Description | Example |
|---------|-------------|---------|
| `,ping` | Ping in your slot | `,ping everyone` |
| `,nuke` | Clear slot messages | `,nuke` |
| `,myslot` | View your slot | `,myslot` |
| `,stats` | Bot statistics | `,stats` |
| `,uptime` | Bot uptime | `,uptime` |
| `,serverinfo` | Server information | `,serverinfo` |
| `,leaderboard` | Slot leaderboard | `,leaderboard` |
| `,history` | Recent activity | `,history` |
| `,redeem` | Redeem a code for a slot | `,redeem XXXX-XXXX-XXXX` |

### ⚡ Slash Commands

| Command | Description |
|---------|-------------|
| `/ping` | Check bot latency |
| `/slotinfo` | View slot information |
| `/stats` | View bot statistics |
| `/myslot` | View your slot |
| `/serverinfo` | Server information |
| `/leaderboard` | Slot leaderboard |

---

## 🏗️ Project Structure

```
SlotBot/
├── main.py              # Main bot file with all commands
├── config.json          # Bot configuration
├── data.json            # Slot expiry data
├── pingcount.json       # Ping count tracking
├── blacklist.json       # Blacklisted users
├── history.json         # Action history log
├── tickets.json         # Open ticket tracking
├── redeems.json         # Redeem codes storage
├── slotbot.log          # Runtime log file
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
├── .env.example         # Environment variable template
├── CONTRIBUTING.md      # Contribution guidelines
├── LICENSE              # MIT License
├── README.md            # This file
└── image/
    ├── banner.png       # Project banner
    └── slotbotthumbnail.png
```

---

## 🔧 How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  Staff runs      │────▶│  Bot validates   │────▶│  Channel created  │
│  ,create         │     │  & checks blacklist│   │  with permissions │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Roles assigned  │
                    │  Rules posted    │
                    │  Info embed sent │
                    │  History logged  │
                    └──────────────────┘
                               │
                               ▼
              ┌────────────────────────────┐
              │   Background Tasks Run     │
              │   • Expire check (1hr)     │
              │   • Ping reset (24hr)      │
              │   • Auto role cleanup      │
              │   • Audit log updates      │
              └────────────────────────────┘
```

---

## 💡 Tips & Notes

> [!NOTE]
> The bot needs **Administrator** permissions and should be positioned **above** the slot roles in the role hierarchy.

> [!TIP]
> Use the `,setup` command for easy first-time configuration instead of manually editing `config.json`.

> [!TIP]
> Set up a dedicated **log channel** to track all slot actions with timestamps.

> [!WARNING]
> Create **two separate categories** in your Discord server before running the bot.

> [!CAUTION]
> Users with **3+ warnings** should be reviewed for potential slot revocation.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

[![Discord](https://img.shields.io/badge/Join_our_Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/JdyvFVgsTN)

---

## ⭐ Support

If you find this project useful, please consider giving it a **star** on GitHub! 🌟

<div align="center">

[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/users/887532157747212370)
[![X](https://img.shields.io/badge/X-%23000000.svg?style=for-the-badge&logo=X&logoColor=white)](https://twitter.com/rizawastaken)
[![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=youtube&logoColor=white)](https://drive.google.com/file/d/1ESOROJ6V65hZ3IOk70nerMaDbOmP12UQ/view)
[![GitHub](https://img.shields.io/badge/GitHub-%23181717.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/codewithriza/SlotBot)

<br/>

**Made with ❤️ by [@codewithriza](https://github.com/codewithriza)**

</div>
