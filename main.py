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
