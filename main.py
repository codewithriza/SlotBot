# Slot Bot - A Discord bot for managing slots
# Made by Riza (https://github.com/codewithriza/SlotBot)
# Contact for help - https://discord.com/users/887532157747212370
# Create an issue in this repo for support: https://github.com/codewithriza/SlotBot/issues

import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import json
import os
import asyncio
import logging
from colorama import Fore, Style

# ─── Logging Setup ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("slotbot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("SlotBot")

# ─── Configuration Loading ───────────────────────────────────────────────────
CONFIG_PATH = "config.json"
DATA_PATH = "data.json"
PINGCOUNT_PATH = "pingcount.json"


def load_json(path: str, default=None):
    """Safely load a JSON file, returning *default* on failure."""
    if default is None:
        default = []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path: str, data):
    """Atomically write JSON data to a file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


config = load_json(CONFIG_PATH, default={})

# Validate required config keys
REQUIRED_KEYS = [
    "token",
    "prefix",
    "staffrole",
    "premiumeroleid",
    "guildid",
    "categoryid_1",
    "categoryid_2",
    "slot_role_id",
]

missing = [k for k in REQUIRED_KEYS if k not in config or config[k] in (None, "", 0, 123)]
if missing:
    logger.warning(
        f"config.json is missing or has placeholder values for: {', '.join(missing)}. "
        "Please update config.json before running the bot."
    )

# Pull values from config with safe defaults
TOKEN = config.get("token", "")
PREFIX = config.get("prefix", ",")
STAFF_ROLE_ID = int(config.get("staffrole", 0))
PREMIUM_ROLE_ID = int(config.get("premiumeroleid", 0))
GUILD_ID = int(config.get("guildid", 0))
CATEGORY_ID_1 = int(config.get("categoryid_1", 0))
CATEGORY_ID_2 = int(config.get("categoryid_2", 0))
SLOT_ROLE_ID = int(config.get("slot_role_id", 0))
LOG_CHANNEL_ID = int(config.get("log_channel_id", 0))
DEFAULT_PING_COUNT = int(config.get("default_ping_count", 3))
PING_RESET_HOURS = int(config.get("ping_reset_hours", 24))

# Allow token override via environment variable (recommended)
TOKEN = os.environ.get("SLOTBOT_TOKEN", TOKEN)

# ─── Bot Setup ───────────────────────────────────────────────────────────────
intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    status=discord.Status.dnd,
    activity=discord.Activity(
        type=discord.ActivityType.watching, name="Slot Management"
    ),
)
bot.remove_command("help")

BANNER = f"""{Fore.CYAN}
    ███████╗██╗      ██████╗ ████████╗██████╗  ██████╗ ████████╗
    ██╔════╝██║     ██╔═══██╗╚══██╔══╝██╔══██╗██╔═══██╗╚══██╔══╝
    ███████╗██║     ██║   ██║   ██║   ██████╔╝██║   ██║   ██║
    ╚════██║██║     ██║   ██║   ██║   ██╔══██╗██║   ██║   ██║
    ███████║███████╗╚██████╔╝   ██║   ██████╔╝╚██████╔╝   ██║
    ╚══════╝╚══════╝ ╚═════╝    ╚═╝   ╚═════╝  ╚═════╝    ╚═╝
{Style.RESET_ALL}    Made By @codewithriza  •  github.com/codewithriza/SlotBot
"""


# ─── Utility Helpers ─────────────────────────────────────────────────────────
def get_slot_owner(channel_id: int) -> int | None:
    """Return the user ID of the slot owner for a given channel, or None."""
    data = load_json(PINGCOUNT_PATH)
    for entry in data:
        if entry.get("channelid") == channel_id:
            return entry.get("userid")
    return None


def get_slot_data(channel_id: int) -> dict | None:
    """Return the full slot data dict for a channel, or None."""
    data = load_json(PINGCOUNT_PATH)
    for entry in data:
        if entry.get("channelid") == channel_id:
            return entry
    return None


def remove_slot_data(channel_id: int, path: str = PINGCOUNT_PATH):
    """Remove a slot entry from a JSON data file by channel ID."""
    data = load_json(path)
    data = [entry for entry in data if entry.get("channelid") != channel_id]
    save_json(path, data)


async def send_log(guild: discord.Guild, embed: discord.Embed):
    """Send an embed to the configured log channel, if it exists."""
    if LOG_CHANNEL_ID:
        channel = guild.get_channel(LOG_CHANNEL_ID)
        if channel:
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                logger.warning("Cannot send to log channel – missing permissions.")


def build_rules_embed(guild: discord.Guild) -> discord.Embed:
    """Build the standard slot rules embed."""
    embed = discord.Embed(title="📜 Slot Rules", color=0x8A2BE2)
    rules = (
        "1. We don't offer any refunds.\n"
        "2. You can't sell or share your slot.\n"
        "3. If you promote any server your slot will be revoked.\n"
        "4. If you scam, your slot will get revoked and you will get banned.\n"
        "5. We can put your slot on hold at any time.\n"
        "6. Save the transcript of the ticket when you buy – if the server gets termed you won't get your slot back without it.\n"
        "7. We recommend using MM. If the slot user denies MM, we have the right to revoke your slot.\n"
        "8. You are not allowed to advertise your server invite or telegram invite.\n"
        "9. Ping reset: every 24 hours.\n"
        "10. Positions are never fixed.\n"
        "11. Inactive slots may be revoked without a refund.\n"
        "12. We can change the rules whenever we want without further notice.\n"
        "13. Over-pinging will lead to an instant slot revoke without any refund.\n"
        "14. Inactivity for more than 2 days will result in removal of the slot (you will be warned first)."
    )
    embed.add_field(name="Rules", value=rules, inline=False)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    return embed


# ─── Events ──────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
