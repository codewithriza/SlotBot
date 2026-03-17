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
    print(BANNER)
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guild(s)")
    logger.info(f"Command prefix: {PREFIX}")

    # Start background tasks
    if not expire_slots.is_running():
        expire_slots.start()
    if not reset_pings.is_running():
        reset_pings.start()

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        logger.error(f"Failed to sync slash commands: {e}")


@bot.event
async def on_command_error(ctx: commands.Context, error):
    """Global error handler for prefix commands."""
    if isinstance(error, commands.MissingRole):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="You do not have the required role to use this command.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"Missing required argument: `{error.param.name}`\nUse `{PREFIX}help` for command usage.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ Invalid Argument",
            description=f"Invalid argument provided.\nUse `{PREFIX}help` for command usage.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, commands.CommandNotFound):
        pass  # Silently ignore unknown commands
    else:
        logger.error(f"Unhandled error in {ctx.command}: {error}", exc_info=error)
        embed = discord.Embed(
            title="⚠️ Error",
            description="An unexpected error occurred. Please try again later.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed, delete_after=10)


# ─── Background Tasks ────────────────────────────────────────────────────────
@tasks.loop(hours=1)
async def expire_slots():
    """Check for expired slots every hour and clean them up."""
    data = load_json(PINGCOUNT_PATH)
    now = datetime.datetime.now().timestamp()
    expired = []
    remaining = []

    for entry in data:
        end_time = entry.get("endtime", 0)
        if now >= float(end_time):
            expired.append(entry)
        else:
            remaining.append(entry)

    if not expired:
        return

    save_json(PINGCOUNT_PATH, remaining)

    # Also clean data.json
    slot_data = load_json(DATA_PATH)
    expired_channel_ids = {e["channelid"] for e in expired}
    slot_data = [s for s in slot_data if s.get("channelid") not in expired_channel_ids]
    save_json(DATA_PATH, slot_data)

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    for entry in expired:
        try:
            channel = guild.get_channel(entry["channelid"])
            member = guild.get_member(entry["userid"])

            if member:
                role = guild.get_role(PREMIUM_ROLE_ID)
                if role and role in member.roles:
                    await member.remove_roles(role)

                slot_role = guild.get_role(SLOT_ROLE_ID)
                if slot_role and slot_role in member.roles:
                    await member.remove_roles(slot_role)

            if channel:
                embed = discord.Embed(
                    title="⏰ Slot Expired",
                    description=f"This slot has expired and has been locked.",
                    color=discord.Color.red(),
                )
                embed.set_footer(text="Contact staff to renew your slot.")
                await channel.send(embed=embed)
                await channel.set_permissions(guild.default_role, send_messages=False)
                if member:
                    await channel.set_permissions(member, send_messages=False)

            # Log the expiry
            log_embed = discord.Embed(
                title="📋 Slot Expired",
                description=f"**User:** <@{entry['userid']}>\n**Channel:** <#{entry['channelid']}>",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now(),
            )
            await send_log(guild, log_embed)
            logger.info(f"Slot expired for user {entry['userid']} in channel {entry['channelid']}")

        except Exception as e:
            logger.error(f"Error expiring slot {entry}: {e}")


@expire_slots.before_loop
async def before_expire():
    await bot.wait_until_ready()


@tasks.loop(hours=24)
async def reset_pings():
    """Reset ping counts for all slots every 24 hours."""
    data = load_json(PINGCOUNT_PATH)
    if not data:
        return

    for entry in data:
        entry["ping_count"] = entry.get("max_pings", DEFAULT_PING_COUNT)

    save_json(PINGCOUNT_PATH, data)
    logger.info("Ping counts reset for all slots.")


@reset_pings.before_loop
async def before_reset_pings():
    await bot.wait_until_ready()


# ─── Help Command ────────────────────────────────────────────────────────────
@bot.command()
async def help(ctx):
    """Display the help menu with all available commands."""
    embed = discord.Embed(
        title="🎰 SlotBot Help Menu",
        description="Here are all the available commands:",
        color=0x8A2BE2,
    )

    # Staff commands
    staff_cmds = (
        f"**`{PREFIX}create @user <duration> <d/m> <pings> <category1/category2> [name]`**\n"
        f"└ Create a new slot for a user\n\n"
        f"**`{PREFIX}renew @user #channel <duration> <d/m>`**\n"
        f"└ Renew an existing slot\n\n"
        f"**`{PREFIX}revoke @user #channel`**\n"
        f"└ Revoke a user's slot\n\n"
        f"**`{PREFIX}hold`**\n"
        f"└ Put the current slot on hold\n\n"
        f"**`{PREFIX}unhold`**\n"
        f"└ Remove hold from the current slot\n\n"
        f"**`{PREFIX}add @user`**\n"
        f"└ Add a user to the slot role\n\n"
        f"**`{PREFIX}remove @user`**\n"
        f"└ Remove a user from the slot role\n\n"
        f"**`{PREFIX}delete`**\n"
        f"└ Delete the current slot channel\n\n"
        f"**`{PREFIX}slotinfo [#channel]`**\n"
        f"└ View information about a slot\n\n"
        f"**`{PREFIX}slots`**\n"
        f"└ List all active slots"
    )
    embed.add_field(name="🛡️ Staff Commands", value=staff_cmds, inline=False)

    # User commands
    user_cmds = (
        f"**`{PREFIX}ping <@everyone/@here>`**\n"
        f"└ Ping in your slot channel\n\n"
        f"**`{PREFIX}nuke`**\n"
        f"└ Clear messages in your slot channel\n\n"
        f"**`{PREFIX}myslot`**\n"
        f"└ View your slot information\n\n"
        f"**`{PREFIX}stats`**\n"
        f"└ View bot statistics"
    )
    embed.add_field(name="👤 User Commands", value=user_cmds, inline=False)

    if ctx.guild and ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    embed.set_footer(text=f"SlotBot • Prefix: {PREFIX} • Made by @codewithriza")

    await ctx.send(embed=embed, delete_after=60)


# ─── Staff Commands ──────────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def create(
    ctx,
    member: discord.Member = None,
    yoyo: int = None,
    cx: str = None,
    ping_count: int = None,
    category: str = "category1",
    *,
    name: str = None,
):
    """Create a new slot for a user."""
    if member is None:
        await ctx.reply("❌ Please mention a user. Usage: `{0}create @user 1 d 3 category1 Slot Name`".format(PREFIX))
        return

    if yoyo is None or cx is None:
        await ctx.reply("❌ Invalid format. Usage: `{0}create @user 1 d 3 category1 Slot Name`".format(PREFIX))
        return

    if cx.lower() not in ("d", "m"):
        await ctx.reply("❌ Duration type must be `d` (days) or `m` (months).")
        return

    if ping_count is None:
        ping_count = DEFAULT_PING_COUNT

    if category.lower() not in ("category1", "category2"):
        await ctx.reply("❌ Invalid category. Choose `category1` or `category2`.")
        return

    category_id = CATEGORY_ID_1 if category.lower() == "category1" else CATEGORY_ID_2

    if name is None:
        name = member.display_name

    # Calculate end time
    if cx.lower() == "d":
        end_timestamp = int((yoyo * 24 * 60 * 60) + datetime.datetime.now().timestamp())
    else:  # months
        end_timestamp = int((yoyo * 30 * 24 * 60 * 60) + datetime.datetime.now().timestamp())

    # Set up channel permissions
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(
            view_channel=True, send_messages=False, mention_everyone=False
        ),
        member: discord.PermissionOverwrite(
            view_channel=True, send_messages=True, mention_everyone=True
        ),
    }

    # Get category
    cat = discord.utils.get(ctx.guild.categories, id=category_id)
    if cat is None:
        await ctx.reply("❌ Category not found. Please check your `config.json` category IDs.")
        return

    # Create the channel
    channel = await ctx.guild.create_text_channel(name, category=cat, overwrites=overwrites)

    # Assign roles
    premium_role = discord.utils.get(ctx.guild.roles, id=PREMIUM_ROLE_ID)
    if premium_role:
        await member.add_roles(premium_role)

    slot_role = discord.utils.get(ctx.guild.roles, id=SLOT_ROLE_ID)
    if slot_role:
        await member.add_roles(slot_role)

    # Send rules embed
    rules_embed = build_rules_embed(ctx.guild)
    await channel.send(embed=rules_embed)

    # Send slot info embed
    duration_str = f"{yoyo} day{'s' if yoyo != 1 else ''}" if cx.lower() == "d" else f"{yoyo} month{'s' if yoyo != 1 else ''}"
    info_embed = discord.Embed(
        title="🎰 Slot Created",
        description=(
            f"**Slot Owner:** {member.mention}\n"
            f"**Duration:** {duration_str}\n"
            f"**Expires:** <t:{end_timestamp}:R> (<t:{end_timestamp}:F>)\n"
            f"**Ping Count:** {ping_count}\n"
            f"**Category:** {category}"
        ),
        color=0x8A2BE2,
    )
    info_embed.set_footer(text=ctx.guild.name)
    if member.avatar:
        info_embed.set_author(name=str(member), icon_url=member.avatar.url)
    else:
        info_embed.set_author(name=str(member))
    await channel.send(embed=info_embed)

    # Save slot data
    slot_entry = {
        "endtime": end_timestamp,
        "userid": member.id,
        "channelid": channel.id,
        "ping_count": ping_count,
        "max_pings": ping_count,
        "created_at": int(datetime.datetime.now().timestamp()),
        "created_by": ctx.author.id,
    }

    # Save to pingcount.json
    ping_data = load_json(PINGCOUNT_PATH)
    ping_data.append(slot_entry)
    save_json(PINGCOUNT_PATH, ping_data)

    # Save to data.json
    data = load_json(DATA_PATH)
    data.append(slot_entry)
    save_json(DATA_PATH, data)

    await ctx.reply(f"✅ Successfully created slot {channel.mention} for {member.mention}")

    # Log
    log_embed = discord.Embed(
        title="📋 Slot Created",
        description=(
            f"**User:** {member.mention}\n"
            f"**Channel:** {channel.mention}\n"
            f"**Duration:** {duration_str}\n"
            f"**Pings:** {ping_count}\n"
            f"**Created by:** {ctx.author.mention}"
        ),
        color=discord.Color.green(),
        timestamp=datetime.datetime.now(),
    )
    await send_log(ctx.guild, log_embed)
    logger.info(f"Slot created for {member} in {channel.name} by {ctx.author}")

