<div align="center">

# 🎰 SlotBot

### A powerful Discord bot for seamless slot management

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
[Installation](#-installation) •
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
| ⏸️ **Hold / Unhold** | Temporarily freeze slots during investigations |
| 🚫 **Slot Revocation** | Revoke slots with automatic role & permission cleanup |
| 📢 **Ping Management** | Configurable ping counts with automatic 24-hour resets |
| ⏰ **Auto-Expiry** | Background task automatically expires and locks slots |
| 📊 **Statistics** | View bot stats, active slots, and server metrics |
| 📋 **Audit Logging** | All actions logged to a dedicated channel and log file |
| 🔧 **Slash Commands** | Modern Discord slash commands alongside prefix commands |
| 🛡️ **Role-Based Access** | Staff-only commands with proper permission checks |
| ⚠️ **Error Handling** | Graceful error handling with user-friendly messages |
| 💣 **Nuke Command** | Clear slot channels while preserving bot embeds |
| 🔍 **Slot Info** | View detailed information about any slot |
| 📜 **Auto Rules** | Automatically posts slot rules on creation/renewal |

---

## 📦 Installation

### Prerequisites

- **Python 3.10** or higher
- A **Discord Bot** token ([create one here](https://discord.com/developers/applications))
- **Git** installed on your system

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/codewithriza/SlotBot.git
cd SlotBot

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the bot (see Configuration section below)
nano config.json

# 5. Run the bot
python3 main.py
```

---

## ⚙️ Configuration

Edit `config.json` with your server's values:

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

| Key | Description |
|-----|-------------|
| `token` | Your Discord bot token (or use `SLOTBOT_TOKEN` env variable) |
| `prefix` | Command prefix (default: `,`) |
| `staffrole` | Role ID for staff members who can manage slots |
| `premiumeroleid` | Role ID assigned to users with active slots |
| `guildid` | Your Discord server (guild) ID |
| `categoryid_1` | Category ID for slot category 1 |
| `categoryid_2` | Category ID for slot category 2 |
| `slot_role_id` | Additional role ID for slot holders |
| `log_channel_id` | Channel ID for audit log messages |
| `default_ping_count` | Default number of pings per slot (default: `3`) |
| `ping_reset_hours` | Hours between ping count resets (default: `24`) |

### 🔐 Token Security

You can set your bot token in two ways:

1. **config.json** – Set the `"token"` field (keep the file private!)
2. **Environment variable** – Set `SLOTBOT_TOKEN` (recommended for production)

```bash
export SLOTBOT_TOKEN="your_bot_token_here"
python3 main.py
```

> [!IMPORTANT]
> **Never commit your bot token to Git!** The `.gitignore` is configured to protect sensitive files, but always double-check before pushing.

### How to Get IDs

1. Enable **Developer Mode** in Discord: `Settings → Advanced → Developer Mode`
2. **Right-click** on any server, channel, role, or user
3. Click **"Copy ID"**

---

## 🎮 Commands

### 🛡️ Staff Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `,create` | Create a new slot | `,create @user 7 d 3 category1 Slot Name` |
| `,renew` | Renew an existing slot | `,renew @user #channel 30 d` |
| `,revoke` | Revoke a user's slot | `,revoke @user #channel` |
| `,hold` | Put a slot on hold | `,hold` (in slot channel) |
| `,unhold` | Remove hold from a slot | `,unhold` (in slot channel) |
| `,add` | Add slot role to a user | `,add @user` |
| `,remove` | Remove slot role from a user | `,remove @user` |
| `,delete` | Delete a slot channel | `,delete` (in slot channel) |
| `,slotinfo` | View slot details | `,slotinfo #channel` |
| `,slots` | List all active slots | `,slots` |

### 👤 User Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `,ping` | Ping @everyone/@here in your slot | `,ping everyone` or `,ping here` |
| `,nuke` | Clear messages in your slot | `,nuke` (in your slot channel) |
| `,myslot` | View your slot information | `,myslot` |
| `,stats` | View bot statistics | `,stats` |
| `,help` | Show the help menu | `,help` |

### ⚡ Slash Commands

| Command | Description |
|---------|-------------|
| `/ping` | Check bot latency |
| `/slotinfo` | View slot information |
| `/stats` | View bot statistics |

---

## 🏗️ Project Structure

```
SlotBot/
├── main.py              # Main bot file with all commands and logic
├── config.json          # Bot configuration (IDs, token, settings)
├── data.json            # Slot expiry data storage
├── pingcount.json       # Ping count tracking per slot
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
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Staff runs  │────▶│  Bot creates │────▶│  Channel created │
│  ,create     │     │  slot entry  │     │  with permissions │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Roles added │
                    │  Rules posted│
                    │  Info embed  │
                    └──────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Background Tasks Run  │
              │  • Expire check (1hr)  │
              │  • Ping reset (24hr)   │
              └────────────────────────┘
```

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on:

- Reporting bugs
- Suggesting features
- Submitting pull requests
- Code style guidelines

[![Discord](https://img.shields.io/badge/Join_our_Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/JdyvFVgsTN)

---

## 💡 Tips

> [!NOTE]
> The bot needs **Administrator** permissions and should be positioned **above** the slot roles in the role hierarchy.

> [!TIP]
> Set up a dedicated **log channel** and add its ID to `config.json` as `log_channel_id` to track all slot actions.

> [!WARNING]
> Make sure to create **two separate categories** in your Discord server for `categoryid_1` and `categoryid_2` before running the bot.

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
