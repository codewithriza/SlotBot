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
import time
import random
import string
from typing import Optional
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

# ─── Configuration ───────────────────────────────────────────────────────────
CONFIG_PATH = "config.json"
DATA_PATH = "data.json"
PINGCOUNT_PATH = "pingcount.json"
BLACKLIST_PATH = "blacklist.json"
HISTORY_PATH = "history.json"
TICKETS_PATH = "tickets.json"
REDEEMS_PATH = "redeems.json"


def load_json(path, default=None):
    if default is None:
        default = []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


config = load_json(CONFIG_PATH, default={})
REQUIRED_KEYS = ["token", "prefix", "staffrole", "premiumeroleid", "guildid", "categoryid_1", "categoryid_2", "slot_role_id"]
missing = [k for k in REQUIRED_KEYS if k not in config or config[k] in (None, "", 0, 123)]
if missing:
    logger.warning(f"config.json missing values for: {', '.join(missing)}")

TOKEN = os.environ.get("SLOTBOT_TOKEN", config.get("token", ""))
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
TICKET_CATEGORY_ID = int(config.get("ticket_category_id", 0))

# ─── Bot Setup ───────────────────────────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, status=discord.Status.dnd,
                   activity=discord.Activity(type=discord.ActivityType.watching, name="Slot Management"))
bot.remove_command("help")
bot_start_time = time.time()

BANNER = f"""{Fore.CYAN}
    ███████╗██╗      ██████╗ ████████╗██████╗  ██████╗ ████████╗
    ██╔════╝██║     ██╔═══██╗╚══██╔══╝██╔══██╗██╔═══██╗╚══██╔══╝
    ███████╗██║     ██║   ██║   ██║   ██████╔╝██║   ██║   ██║
    ╚════██║██║     ██║   ██║   ██║   ██╔══██╗██║   ██║   ██║
    ███████║███████╗╚██████╔╝   ██║   ██████╔╝╚██████╔╝   ██║
    ╚══════╝╚══════╝ ╚═════╝    ╚═╝   ╚═════╝  ╚═════╝    ╚═╝
{Style.RESET_ALL}    Made By @codewithriza  •  github.com/codewithriza/SlotBot
"""


# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_slot_owner(channel_id):
    for e in load_json(PINGCOUNT_PATH):
        if e.get("channelid") == channel_id:
            return e.get("userid")
    return None

def get_slot_data(channel_id):
    for e in load_json(PINGCOUNT_PATH):
        if e.get("channelid") == channel_id:
            return e
    return None

def get_user_slot(user_id):
    for e in load_json(PINGCOUNT_PATH):
        if e.get("userid") == user_id:
            return e
    return None

def remove_slot_data(channel_id, path=PINGCOUNT_PATH):
    data = [e for e in load_json(path) if e.get("channelid") != channel_id]
    save_json(path, data)

def is_blacklisted(user_id):
    return any(e.get("userid") == user_id for e in load_json(BLACKLIST_PATH))

def add_to_history(action, **kwargs):
    history = load_json(HISTORY_PATH)
    history.append({"action": action, "timestamp": int(datetime.datetime.now().timestamp()), **kwargs})
    if len(history) > 500:
        history = history[-500:]
    save_json(HISTORY_PATH, history)

def format_uptime(seconds):
    d, h, m, s = int(seconds // 86400), int((seconds % 86400) // 3600), int((seconds % 3600) // 60), int(seconds % 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)

def make_bar(cur, mx, length=10):
    if mx == 0: return "░" * length
    filled = int((cur / mx) * length)
    return "█" * filled + "░" * (length - filled)

async def send_log(guild, embed):
    if LOG_CHANNEL_ID:
        ch = guild.get_channel(LOG_CHANNEL_ID)
        if ch:
            try: await ch.send(embed=embed)
            except discord.Forbidden: pass

def build_rules_embed(guild):
    embed = discord.Embed(title="📜 Slot Rules", color=0x8A2BE2)
    rules = ("1. No refunds.\n2. Can't sell/share your slot.\n3. Server promotion = revoke.\n"
             "4. Scamming = revoke + ban.\n5. We can hold your slot anytime.\n"
             "6. Save ticket transcripts – no transcript = no recovery.\n"
             "7. Use MM. Denying MM = right to revoke.\n8. No server/telegram invite ads.\n"
             "9. Ping reset: every 24 hours.\n10. Positions are never fixed.\n"
             "11. Inactive slots may be revoked without refund.\n"
             "12. Rules can change without notice.\n13. Over-pinging = instant revoke.\n"
             "14. 2+ days inactive = removal (warned first).")
    embed.add_field(name="Rules", value=rules, inline=False)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    return embed


# ─── Events ──────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(BANNER)
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guild(s) | Prefix: {PREFIX}")
    for p in [DATA_PATH, PINGCOUNT_PATH, BLACKLIST_PATH, HISTORY_PATH, TICKETS_PATH, REDEEMS_PATH]:
        if not os.path.exists(p): save_json(p, [])
    if not expire_slots.is_running(): expire_slots.start()
    if not reset_pings.is_running(): reset_pings.start()
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        logger.error(f"Failed to sync slash commands: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(embed=discord.Embed(title="❌ Permission Denied", description="You lack the required role.", color=discord.Color.red()), delete_after=10)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=discord.Embed(title="❌ Missing Argument", description=f"Missing: `{error.param.name}`. Use `{PREFIX}help`.", color=discord.Color.red()), delete_after=10)
    elif isinstance(error, commands.BadArgument):
        await ctx.send(embed=discord.Embed(title="❌ Invalid Argument", description=f"Bad argument. Use `{PREFIX}help`.", color=discord.Color.red()), delete_after=10)
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=discord.Embed(title="⏳ Cooldown", description=f"Try again in **{error.retry_after:.1f}s**.", color=discord.Color.orange()), delete_after=5)
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        logger.error(f"Error in {ctx.command}: {error}", exc_info=error)
        await ctx.send(embed=discord.Embed(title="⚠️ Error", description="An unexpected error occurred.", color=discord.Color.red()), delete_after=10)


# ─── Background Tasks ────────────────────────────────────────────────────────
@tasks.loop(hours=1)
async def expire_slots():
    data = load_json(PINGCOUNT_PATH)
    now = datetime.datetime.now().timestamp()
    expired, remaining = [], []
    for e in data:
        (expired if now >= float(e.get("endtime", 0)) else remaining).append(e)
    if not expired: return
    save_json(PINGCOUNT_PATH, remaining)
    slot_data = load_json(DATA_PATH)
    exp_ids = {e["channelid"] for e in expired}
    save_json(DATA_PATH, [s for s in slot_data if s.get("channelid") not in exp_ids])
    guild = bot.get_guild(GUILD_ID)
    if not guild: return
    for entry in expired:
        try:
            ch = guild.get_channel(entry["channelid"])
            mem = guild.get_member(entry["userid"])
            if mem:
                for rid in [PREMIUM_ROLE_ID, SLOT_ROLE_ID]:
                    r = guild.get_role(rid)
                    if r and r in mem.roles: await mem.remove_roles(r)
            if ch:
                await ch.send(embed=discord.Embed(title="⏰ Slot Expired", description="This slot has expired and been locked.", color=discord.Color.red()).set_footer(text="Contact staff to renew."))
                await ch.set_permissions(guild.default_role, send_messages=False)
                if mem: await ch.set_permissions(mem, send_messages=False)
            add_to_history("expired", userid=entry["userid"], channelid=entry["channelid"])
            await send_log(guild, discord.Embed(title="📋 Slot Expired", description=f"**User:** <@{entry['userid']}>\n**Channel:** <#{entry['channelid']}>", color=discord.Color.orange(), timestamp=datetime.datetime.now()))
        except Exception as e:
            logger.error(f"Error expiring slot: {e}")

@expire_slots.before_loop
async def before_expire(): await bot.wait_until_ready()

@tasks.loop(hours=24)
async def reset_pings():
    data = load_json(PINGCOUNT_PATH)
    if not data: return
    for e in data: e["ping_count"] = e.get("max_pings", DEFAULT_PING_COUNT)
    save_json(PINGCOUNT_PATH, data)
    logger.info("Ping counts reset for all slots.")

@reset_pings.before_loop
async def before_reset_pings(): await bot.wait_until_ready()


# ─── Help ────────────────────────────────────────────────────────────────────
@bot.command()
async def help(ctx):
    e = discord.Embed(title="🎰 SlotBot Help Menu", description="All available commands:", color=0x8A2BE2)
    staff = (f"**`{PREFIX}create`** – Create a slot\n**`{PREFIX}renew`** – Renew a slot\n"
             f"**`{PREFIX}extend`** – Extend duration\n**`{PREFIX}transfer`** – Transfer ownership\n"
             f"**`{PREFIX}revoke`** – Revoke a slot\n**`{PREFIX}hold`** / **`{PREFIX}unhold`** – Hold/unhold\n"
             f"**`{PREFIX}add`** / **`{PREFIX}remove`** – Add/remove role\n**`{PREFIX}delete`** – Delete channel\n"
             f"**`{PREFIX}warn`** – Warn a user\n**`{PREFIX}blacklist`** / **`{PREFIX}unblacklist`** – Manage blacklist\n"
             f"**`{PREFIX}slotinfo`** / **`{PREFIX}slots`** – View info\n**`{PREFIX}announce`** – Send embed\n"
             f"**`{PREFIX}setup`** – Setup wizard")
    user = (f"**`{PREFIX}ping`** – Ping in slot\n**`{PREFIX}nuke`** – Clear messages\n"
            f"**`{PREFIX}myslot`** – Your slot info\n**`{PREFIX}stats`** – Bot stats\n"
            f"**`{PREFIX}uptime`** – Bot uptime\n**`{PREFIX}serverinfo`** – Server info\n"
            f"**`{PREFIX}leaderboard`** – Slot leaderboard\n**`{PREFIX}history`** – Recent activity")
    e.add_field(name="🛡️ Staff Commands", value=staff, inline=False)
    e.add_field(name="👤 User Commands", value=user, inline=False)
    e.add_field(name="⚡ Slash Commands", value="`/ping` `/slotinfo` `/stats` `/myslot` `/serverinfo` `/leaderboard`", inline=False)
    if ctx.guild and ctx.guild.icon: e.set_thumbnail(url=ctx.guild.icon.url)
    e.set_footer(text=f"SlotBot v3.0 • Prefix: {PREFIX} • @codewithriza")
    await ctx.send(embed=e, delete_after=120)


# ─── Staff: Create ───────────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def create(ctx, member: discord.Member = None, yoyo: int = None, cx: str = None,
                 ping_count: int = None, category: str = "category1", *, name: str = None):
    if not member: return await ctx.reply(f"❌ Usage: `{PREFIX}create @user 1 d 3 category1 Name`")
    if is_blacklisted(member.id): return await ctx.reply(f"❌ {member.mention} is **blacklisted**.")
    if not yoyo or not cx: return await ctx.reply(f"❌ Usage: `{PREFIX}create @user 1 d 3 category1 Name`")
    if cx.lower() not in ("d", "m"): return await ctx.reply("❌ Use `d` (days) or `m` (months).")
    if ping_count is None: ping_count = DEFAULT_PING_COUNT
    if category.lower() not in ("category1", "category2"): return await ctx.reply("❌ Use `category1` or `category2`.")
    existing = get_user_slot(member.id)
    if existing: return await ctx.reply(f"⚠️ {member.mention} already has a slot in <#{existing['channelid']}>.")
    cat_id = CATEGORY_ID_1 if category.lower() == "category1" else CATEGORY_ID_2
    if not name: name = member.display_name
    end_ts = int((yoyo * 86400 if cx.lower() == "d" else yoyo * 30 * 86400) + datetime.datetime.now().timestamp())
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, mention_everyone=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, mention_everyone=True),
    }
    cat = discord.utils.get(ctx.guild.categories, id=cat_id)
    if not cat: return await ctx.reply("❌ Category not found. Check config.json.")
    ch = await ctx.guild.create_text_channel(name, category=cat, overwrites=overwrites)
    for rid in [PREMIUM_ROLE_ID, SLOT_ROLE_ID]:
        r = discord.utils.get(ctx.guild.roles, id=rid)
        if r: await member.add_roles(r)
    await ch.send(embed=build_rules_embed(ctx.guild))
    dur = f"{yoyo} day{'s' if yoyo != 1 else ''}" if cx.lower() == "d" else f"{yoyo} month{'s' if yoyo != 1 else ''}"
    ie = discord.Embed(title="🎰 Slot Created", description=f"**Owner:** {member.mention}\n**Duration:** {dur}\n**Expires:** <t:{end_ts}:R> (<t:{end_ts}:F>)\n**Pings:** {ping_count}\n**Category:** {category}", color=0x8A2BE2)
    ie.set_footer(text=ctx.guild.name)
    if member.avatar: ie.set_author(name=str(member), icon_url=member.avatar.url)
    else: ie.set_author(name=str(member))
    await ch.send(embed=ie)
    entry = {"endtime": end_ts, "userid": member.id, "channelid": ch.id, "ping_count": ping_count, "max_pings": ping_count, "created_at": int(datetime.datetime.now().timestamp()), "created_by": ctx.author.id, "warnings": 0}
    for p in [PINGCOUNT_PATH, DATA_PATH]:
        d = load_json(p); d.append(entry); save_json(p, d)
    await ctx.reply(f"✅ Created slot {ch.mention} for {member.mention}")
    add_to_history("created", userid=member.id, channelid=ch.id, staff=ctx.author.id, duration=dur)
    await send_log(ctx.guild, discord.Embed(title="📋 Slot Created", description=f"**User:** {member.mention}\n**Channel:** {ch.mention}\n**Duration:** {dur}\n**By:** {ctx.author.mention}", color=discord.Color.green(), timestamp=datetime.datetime.now()))


# ─── Staff: Renew ────────────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def renew(ctx, member: discord.Member = None, channel: discord.TextChannel = None, yoyo: int = None, cx: str = None):
    if not member: return await ctx.reply(f"❌ Usage: `{PREFIX}renew @user #channel 1 d`")
    if not channel: return await ctx.reply(f"❌ Usage: `{PREFIX}renew @user #channel 1 d`")
    if not yoyo or not cx: return await ctx.reply(f"❌ Usage: `{PREFIX}renew @user #channel 1 d`")
    if cx.lower() not in ("d", "m"): return await ctx.reply("❌ Use `d` or `m`.")
    end_ts = int((yoyo * 86400 if cx.lower() == "d" else yoyo * 30 * 86400) + datetime.datetime.now().timestamp())
    await channel.set_permissions(member, view_channel=True, send_messages=True, mention_everyone=True)
    for rid in [PREMIUM_ROLE_ID, SLOT_ROLE_ID]:
        r = discord.utils.get(ctx.guild.roles, id=rid)
        if r: await member.add_roles(r)
    await channel.purge(limit=1000)
    await channel.send(embed=build_rules_embed(ctx.guild))
    dur = f"{yoyo} day{'s' if yoyo != 1 else ''}" if cx.lower() == "d" else f"{yoyo} month{'s' if yoyo != 1 else ''}"
    ie = discord.Embed(title="🔄 Slot Renewed", description=f"**Owner:** {member.mention}\n**Duration:** {dur}\n**Expires:** <t:{end_ts}:R>", color=0x8A2BE2)
    ie.set_footer(text=ctx.guild.name)
    if member.avatar: ie.set_author(name=str(member), icon_url=member.avatar.url)
    else: ie.set_author(name=str(member))
    await channel.send(embed=ie)
    for p in [PINGCOUNT_PATH, DATA_PATH]:
        d = load_json(p); updated = False
        for e in d:
            if e.get("channelid") == channel.id:
                e["endtime"] = end_ts; e["userid"] = member.id; e["ping_count"] = e.get("max_pings", DEFAULT_PING_COUNT); e["warnings"] = 0; updated = True; break
        if not updated: d.append({"endtime": end_ts, "userid": member.id, "channelid": channel.id, "ping_count": DEFAULT_PING_COUNT, "max_pings": DEFAULT_PING_COUNT, "created_at": int(datetime.datetime.now().timestamp()), "created_by": ctx.author.id, "warnings": 0})
        save_json(p, d)
    await ctx.reply(f"✅ Renewed {channel.mention} for {member.mention}")
    add_to_history("renewed", userid=member.id, channelid=channel.id, staff=ctx.author.id, duration=dur)
    await send_log(ctx.guild, discord.Embed(title="📋 Slot Renewed", description=f"**User:** {member.mention}\n**Channel:** {channel.mention}\n**Duration:** {dur}\n**By:** {ctx.author.mention}", color=discord.Color.blue(), timestamp=datetime.datetime.now()))


# ─── Staff: Extend ───────────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def extend(ctx, member: discord.Member = None, yoyo: int = None, cx: str = None):
    """Extend a slot's duration without resetting the channel."""
    if not member: return await ctx.reply(f"❌ Usage: `{PREFIX}extend @user 7 d`")
    if not yoyo or not cx: return await ctx.reply(f"❌ Usage: `{PREFIX}extend @user 7 d`")
    if cx.lower() not in ("d", "m"): return await ctx.reply("❌ Use `d` or `m`.")
    slot = get_user_slot(member.id)
    if not slot: return await ctx.reply(f"❌ {member.mention} doesn't have a slot.")
    extra = yoyo * 86400 if cx.lower() == "d" else yoyo * 30 * 86400
    new_end = int(float(slot["endtime"]) + extra)
    dur = f"{yoyo} day{'s' if yoyo != 1 else ''}" if cx.lower() == "d" else f"{yoyo} month{'s' if yoyo != 1 else ''}"
    for p in [PINGCOUNT_PATH, DATA_PATH]:
        d = load_json(p)
        for e in d:
            if e.get("channelid") == slot["channelid"]: e["endtime"] = new_end; break
        save_json(p, d)
    ch = ctx.guild.get_channel(slot["channelid"])
    if ch:
        await ch.send(embed=discord.Embed(title="⏳ Slot Extended", description=f"Slot extended by **{dur}**.\n**New Expiry:** <t:{new_end}:R> (<t:{new_end}:F>)", color=discord.Color.green()))
    await ctx.reply(f"✅ Extended {member.mention}'s slot by **{dur}**. New expiry: <t:{new_end}:R>")
    add_to_history("extended", userid=member.id, channelid=slot["channelid"], staff=ctx.author.id, duration=dur)
    await send_log(ctx.guild, discord.Embed(title="📋 Slot Extended", description=f"**User:** {member.mention}\n**Extended by:** {dur}\n**By:** {ctx.author.mention}", color=discord.Color.green(), timestamp=datetime.datetime.now()))


# ─── Staff: Transfer ─────────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def transfer(ctx, from_member: discord.Member = None, to_member: discord.Member = None):
    """Transfer slot ownership from one user to another."""
    if not from_member or not to_member: return await ctx.reply(f"❌ Usage: `{PREFIX}transfer @from @to`")
    if is_blacklisted(to_member.id): return await ctx.reply(f"❌ {to_member.mention} is blacklisted.")
    if get_user_slot(to_member.id): return await ctx.reply(f"❌ {to_member.mention} already has a slot.")
    slot = get_user_slot(from_member.id)
    if not slot: return await ctx.reply(f"❌ {from_member.mention} doesn't have a slot.")
    ch = ctx.guild.get_channel(slot["channelid"])
    if not ch: return await ctx.reply("❌ Slot channel not found.")
    # Update permissions
    await ch.set_permissions(from_member, overwrite=None)
    await ch.set_permissions(to_member, view_channel=True, send_messages=True, mention_everyone=True)
    # Transfer roles
    for rid in [PREMIUM_ROLE_ID, SLOT_ROLE_ID]:
        r = ctx.guild.get_role(rid)
        if r:
            if r in from_member.roles: await from_member.remove_roles(r)
            await to_member.add_roles(r)
    # Update data
    for p in [PINGCOUNT_PATH, DATA_PATH]:
        d = load_json(p)
        for e in d:
            if e.get("channelid") == slot["channelid"]: e["userid"] = to_member.id; break
        save_json(p, d)
    await ch.send(embed=discord.Embed(title="🔀 Slot Transferred", description=f"Ownership transferred from {from_member.mention} to {to_member.mention}.", color=0x8A2BE2))
    await ctx.reply(f"✅ Transferred slot from {from_member.mention} to {to_member.mention}")
    add_to_history("transferred", from_user=from_member.id, to_user=to_member.id, channelid=slot["channelid"], staff=ctx.author.id)
    await send_log(ctx.guild, discord.Embed(title="📋 Slot Transferred", description=f"**From:** {from_member.mention}\n**To:** {to_member.mention}\n**By:** {ctx.author.mention}", color=discord.Color.purple(), timestamp=datetime.datetime.now()))


# ─── Staff: Revoke ───────────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def revoke(ctx, member: discord.Member = None, channel: discord.TextChannel = None):
    if not member: return await ctx.reply(f"❌ Usage: `{PREFIX}revoke @user #channel`")
    if not channel: return await ctx.reply(f"❌ Usage: `{PREFIX}revoke @user #channel`")
    if not any(e.get("channelid") == channel.id for e in load_json(PINGCOUNT_PATH)):
        return await ctx.reply("❌ Slot not found in database.")
    await channel.set_permissions(member, send_messages=False, mention_everyone=False)
    for rid in [PREMIUM_ROLE_ID, SLOT_ROLE_ID]:
        r = ctx.guild.get_role(rid)
        if r and r in member.roles: await member.remove_roles(r)
    remove_slot_data(channel.id, PINGCOUNT_PATH); remove_slot_data(channel.id, DATA_PATH)
    await channel.send(embed=discord.Embed(title="🚫 Slot Revoked", description=f"Revoked from {member.mention}.", color=discord.Color.red()).set_footer(text=f"By {ctx.author.display_name}"))
    await ctx.reply(f"✅ Revoked {channel.mention} from {member.mention}")
    add_to_history("revoked", userid=member.id, channelid=channel.id, staff=ctx.author.id)
    await send_log(ctx.guild, discord.Embed(title="📋 Slot Revoked", description=f"**User:** {member.mention}\n**Channel:** {channel.mention}\n**By:** {ctx.author.mention}", color=discord.Color.red(), timestamp=datetime.datetime.now()))


# ─── Staff: Hold / Unhold ────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def hold(ctx):
    uid = get_slot_owner(ctx.channel.id)
    if not uid: return await ctx.reply("❌ No slot owner found for this channel.")
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    mem = ctx.guild.get_member(uid)
    if mem: await ctx.channel.set_permissions(mem, send_messages=False)
    await ctx.channel.send(embed=discord.Embed(title="⚠️ Slot On Hold", description=f"Report opened against <@{uid}>.\n**Do not deal with them until reopened.**", color=discord.Color.yellow()).set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/warning-xxl.png").set_footer(text=f"Held by {ctx.author.display_name}"))
    add_to_history("held", userid=uid, channelid=ctx.channel.id, staff=ctx.author.id)
    await send_log(ctx.guild, discord.Embed(title="📋 Slot Held", description=f"**Channel:** {ctx.channel.mention}\n**User:** <@{uid}>\n**By:** {ctx.author.mention}", color=discord.Color.yellow(), timestamp=datetime.datetime.now()))

@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def unhold(ctx):
    uid = get_slot_owner(ctx.channel.id)
    if not uid: return await ctx.reply("❌ No slot owner found for this channel.")
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    mem = ctx.guild.get_member(uid)
    if mem: await ctx.channel.set_permissions(mem, send_messages=True, mention_everyone=True)
    await ctx.channel.send(embed=discord.Embed(title="✅ Slot Unheld", description="Case resolved. Slot is now open.", color=discord.Color.green()).set_footer(text=f"Unheld by {ctx.author.display_name}"))
    add_to_history("unheld", userid=uid, channelid=ctx.channel.id, staff=ctx.author.id)
    await send_log(ctx.guild, discord.Embed(title="📋 Slot Unheld", description=f"**Channel:** {ctx.channel.mention}\n**By:** {ctx.author.mention}", color=discord.Color.green(), timestamp=datetime.datetime.now()))


# ─── Staff: Add / Remove Role ────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def add(ctx, member: discord.Member = None):
    if not member: return await ctx.reply(f"❌ Usage: `{PREFIX}add @user`")
    role = ctx.guild.get_role(SLOT_ROLE_ID)
    if not role: return await ctx.reply("❌ Slot role not found.")
    if role in member.roles: return await ctx.reply(f"ℹ️ {member.mention} already has **{role.name}**.")
    await member.add_roles(role)
    await ctx.send(embed=discord.Embed(title="✅ Role Added", description=f"Added **{role.name}** to {member.mention}", color=discord.Color.green()))

@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def remove(ctx, member: discord.Member = None):
    if not member: return await ctx.reply(f"❌ Usage: `{PREFIX}remove @user`")
    role = ctx.guild.get_role(SLOT_ROLE_ID)
    if not role: return await ctx.reply("❌ Slot role not found.")
    if role not in member.roles: return await ctx.reply(f"ℹ️ {member.mention} doesn't have **{role.name}**.")
    await member.remove_roles(role)
    await ctx.send(embed=discord.Embed(title="✅ Role Removed", description=f"Removed **{role.name}** from {member.mention}", color=discord.Color.green()))


# ─── Staff: Delete ───────────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def delete(ctx):
    slot = get_slot_data(ctx.channel.id)
    remove_slot_data(ctx.channel.id, PINGCOUNT_PATH); remove_slot_data(ctx.channel.id, DATA_PATH)
    if slot:
        mem = ctx.guild.get_member(slot["userid"])
        if mem:
            for rid in [PREMIUM_ROLE_ID, SLOT_ROLE_ID]:
                r = ctx.guild.get_role(rid)
                if r and r in mem.roles: await mem.remove_roles(r)
    add_to_history("deleted", channelid=ctx.channel.id, staff=ctx.author.id)
    await send_log(ctx.guild, discord.Embed(title="📋 Slot Deleted", description=f"**Channel:** #{ctx.channel.name}\n**By:** {ctx.author.mention}", color=discord.Color.dark_red(), timestamp=datetime.datetime.now()))
    try: await ctx.channel.delete(reason=f"Deleted by {ctx.author}")
    except discord.Forbidden: await ctx.send("❌ Missing permissions to delete.")


# ─── Staff: Warn ─────────────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def warn(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member: return await ctx.reply(f"❌ Usage: `{PREFIX}warn @user [reason]`")
    slot = get_user_slot(member.id)
    warn_count = 0
    if slot:
        d = load_json(PINGCOUNT_PATH)
        for e in d:
            if e.get("userid") == member.id:
                e["warnings"] = e.get("warnings", 0) + 1
                warn_count = e["warnings"]
                break
        save_json(PINGCOUNT_PATH, d)
    else:
        warn_count = 1
    e = discord.Embed(title="⚠️ Warning Issued", description=f"**User:** {member.mention}\n**Reason:** {reason}\n**Total Warnings:** {warn_count}", color=discord.Color.orange())
    e.set_footer(text=f"Warned by {ctx.author.display_name}")
    await ctx.send(embed=e)
    # DM the user
    try:
        dm_embed = discord.Embed(title="⚠️ You've Been Warned", description=f"**Server:** {ctx.guild.name}\n**Reason:** {reason}\n**Total Warnings:** {warn_count}\n\n*3 warnings may result in slot revocation.*", color=discord.Color.orange())
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        pass
    add_to_history("warned", userid=member.id, staff=ctx.author.id, reason=reason, count=warn_count)
    await send_log(ctx.guild, discord.Embed(title="📋 Warning Issued", description=f"**User:** {member.mention}\n**Reason:** {reason}\n**Count:** {warn_count}\n**By:** {ctx.author.mention}", color=discord.Color.orange(), timestamp=datetime.datetime.now()))


# ─── Staff: Blacklist / Unblacklist ──────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def blacklist(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    if not member: return await ctx.reply(f"❌ Usage: `{PREFIX}blacklist @user [reason]`")
    if is_blacklisted(member.id): return await ctx.reply(f"ℹ️ {member.mention} is already blacklisted.")
    bl = load_json(BLACKLIST_PATH)
    bl.append({"userid": member.id, "reason": reason, "by": ctx.author.id, "timestamp": int(datetime.datetime.now().timestamp())})
    save_json(BLACKLIST_PATH, bl)
    # Revoke their slot if they have one
    slot = get_user_slot(member.id)
    if slot:
        ch = ctx.guild.get_channel(slot["channelid"])
        if ch: await ch.set_permissions(member, send_messages=False, mention_everyone=False)
        for rid in [PREMIUM_ROLE_ID, SLOT_ROLE_ID]:
            r = ctx.guild.get_role(rid)
            if r and r in member.roles: await member.remove_roles(r)
        remove_slot_data(slot["channelid"], PINGCOUNT_PATH); remove_slot_data(slot["channelid"], DATA_PATH)
    await ctx.send(embed=discord.Embed(title="🚫 User Blacklisted", description=f"{member.mention} has been blacklisted.\n**Reason:** {reason}", color=discord.Color.dark_red()))
    add_to_history("blacklisted", userid=member.id, staff=ctx.author.id, reason=reason)
    await send_log(ctx.guild, discord.Embed(title="📋 User Blacklisted", description=f"**User:** {member.mention}\n**Reason:** {reason}\n**By:** {ctx.author.mention}", color=discord.Color.dark_red(), timestamp=datetime.datetime.now()))

@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def unblacklist(ctx, member: discord.Member = None):
    if not member: return await ctx.reply(f"❌ Usage: `{PREFIX}unblacklist @user`")
    if not is_blacklisted(member.id): return await ctx.reply(f"ℹ️ {member.mention} is not blacklisted.")
    bl = [e for e in load_json(BLACKLIST_PATH) if e.get("userid") != member.id]
    save_json(BLACKLIST_PATH, bl)
    await ctx.send(embed=discord.Embed(title="✅ User Unblacklisted", description=f"{member.mention} has been removed from the blacklist.", color=discord.Color.green()))
    add_to_history("unblacklisted", userid=member.id, staff=ctx.author.id)


# ─── Staff: Slotinfo / Slots ─────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def slotinfo(ctx, channel: discord.TextChannel = None):
    if not channel: channel = ctx.channel
    slot = get_slot_data(channel.id)
    if not slot: return await ctx.reply("❌ No slot data found.")
    mem = ctx.guild.get_member(slot["userid"])
    mem_str = mem.mention if mem else f"<@{slot['userid']}> (left)"
    end_ts = int(slot.get("endtime", 0))
    created_ts = int(slot.get("created_at", 0))
    pings = slot.get("ping_count", 0)
    mx = slot.get("max_pings", DEFAULT_PING_COUNT)
    warns = slot.get("warnings", 0)
    now = datetime.datetime.now().timestamp()
    total_dur = end_ts - created_ts if created_ts else 1
    elapsed = now - created_ts if created_ts else 0
    progress = min(elapsed / total_dur, 1.0) if total_dur > 0 else 0
    e = discord.Embed(title=f"📊 Slot Info – #{channel.name}", color=0x8A2BE2)
    e.add_field(name="👤 Owner", value=mem_str, inline=True)
    e.add_field(name="📢 Pings", value=f"{pings}/{mx} {make_bar(pings, mx)}", inline=True)
    e.add_field(name="⚠️ Warnings", value=str(warns), inline=True)
    e.add_field(name="⏰ Expires", value=f"<t:{end_ts}:R>" if end_ts else "Unknown", inline=True)
    if created_ts: e.add_field(name="📅 Created", value=f"<t:{created_ts}:F>", inline=True)
    e.add_field(name="⏳ Progress", value=f"{make_bar(int(progress*100), 100, 15)} {int(progress*100)}%", inline=False)
    e.set_footer(text=ctx.guild.name)
    await ctx.send(embed=e)

@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def slots(ctx):
    data = load_json(PINGCOUNT_PATH)
    if not data: return await ctx.reply("ℹ️ No active slots.")
    now = datetime.datetime.now().timestamp()
    lines = []
    for i, e in enumerate(data, 1):
        mem = ctx.guild.get_member(e["userid"])
        ms = mem.mention if mem else f"<@{e['userid']}>"
        ch = ctx.guild.get_channel(e["channelid"])
        cs = ch.mention if ch else f"#{e['channelid']}"
        et = int(e.get("endtime", 0))
        st = "🟢" if now < et else "🔴"
        lines.append(f"`{i}.` {st} {cs} → {ms} | <t:{et}:R>")
    embed = discord.Embed(title=f"🎰 All Slots ({len(data)})", description="\n".join(lines), color=0x8A2BE2)
    embed.set_footer(text=ctx.guild.name)
    await ctx.send(embed=embed)


# ─── Staff: Announce ─────────────────────────────────────────────────────────
@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def announce(ctx, *, message: str = None):
    if not message: return await ctx.reply(f"❌ Usage: `{PREFIX}announce Your message here`")
    e = discord.Embed(title="📢 Announcement", description=message, color=0x8A2BE2, timestamp=datetime.datetime.now())
    if ctx.guild.icon: e.set_thumbnail(url=ctx.guild.icon.url)
    e.set_footer(text=f"Announced by {ctx.author.display_name}")
    await ctx.message.delete()
    await ctx.send(embed=e)


# ─── Staff: Setup Wizard ─────────────────────────────────────────────────────
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Interactive setup wizard for first-time configuration."""
    e = discord.Embed(title="🔧 SlotBot Setup Wizard", description="I'll help you configure SlotBot! Answer the following questions.\n\n**Type `cancel` at any time to abort.**", color=0x8A2BE2)
    await ctx.send(embed=e)
    
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    
    questions = [
        ("What is the **Staff Role ID**? (Right-click the role → Copy ID)", "staffrole"),
        ("What is the **Premium/Buyer Role ID**?", "premiumeroleid"),
        ("What is the **Slot Role ID**? (Role given to slot holders)", "slot_role_id"),
        ("What is the **Category 1 ID**? (For slot channels)", "categoryid_1"),
        ("What is the **Category 2 ID**? (Second category for slots)", "categoryid_2"),
        ("What is the **Log Channel ID**? (For audit logs, 0 to skip)", "log_channel_id"),
        ("How many **default pings** per slot? (e.g., 3)", "default_ping_count"),
    ]
    
    new_config = load_json(CONFIG_PATH, default={})
    new_config["guildid"] = ctx.guild.id
    
    for question, key in questions:
        await ctx.send(embed=discord.Embed(description=question, color=0x8A2BE2))
        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            if msg.content.lower() == "cancel":
                return await ctx.send("❌ Setup cancelled.")
            new_config[key] = int(msg.content)
        except asyncio.TimeoutError:
            return await ctx.send("❌ Setup timed out.")
        except ValueError:
            return await ctx.send("❌ Invalid number. Setup cancelled.")
    
    save_json(CONFIG_PATH, new_config)
    e = discord.Embed(title="✅ Setup Complete!", description="Configuration saved to `config.json`.\n\n**⚠️ Restart the bot** for changes to take effect.\n\nMake sure to also set your bot token in `config.json` or via the `SLOTBOT_TOKEN` environment variable.", color=discord.Color.green())
    await ctx.send(embed=e)
    logger.info(f"Setup wizard completed by {ctx.author}")


# ─── User: Ping ──────────────────────────────────────────────────────────────
@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def ping(ctx, mention: str = None):
    data = load_json(PINGCOUNT_PATH)
    for i, ud in enumerate(data):
        if ud["userid"] == ctx.author.id:
            if ctx.channel.id != ud["channelid"]:
                return await ctx.send("❌ Use this in your slot channel.")
            if ud["ping_count"] <= 0:
                return await ctx.send(embed=discord.Embed(title="❌ No Pings Left", description="Pings reset every 24 hours.", color=discord.Color.red()), delete_after=10)
            data[i]["ping_count"] -= 1
            save_json(PINGCOUNT_PATH, data)
            ms = "@here" if not mention or mention.lower() in ("@here", "here") else "@everyone" if mention.lower() in ("@everyone", "everyone") else "@here"
            pm = await ctx.send(ms)
            left = data[i]["ping_count"]
            mx = ud.get("max_pings", DEFAULT_PING_COUNT)
            await ctx.send(embed=discord.Embed(title="📢 Ping Sent", description=f"{ctx.author.mention} pinged {ms}!\n**Remaining:** {left}/{mx} {make_bar(left, mx)}", color=0xFFFF00))
            await asyncio.sleep(5)
            try: await pm.delete()
            except: pass
            return
    await ctx.send("❌ You don't have a slot.")


# ─── User: Nuke ──────────────────────────────────────────────────────────────
@bot.command()
async def nuke(ctx):
    slot = get_slot_data(ctx.channel.id)
    if not slot: return await ctx.send("❌ Not a slot channel.")
    is_owner = slot["userid"] == ctx.author.id
    staff_role = ctx.guild.get_role(STAFF_ROLE_ID)
    is_staff = staff_role and staff_role in ctx.author.roles
    if not is_owner and not is_staff: return await ctx.send("❌ No permission.")
    deleted = await ctx.channel.purge(limit=None, check=lambda m: m.author != bot.user or not m.embeds)
    await ctx.send(embed=discord.Embed(title="💣 Nuked", description=f"Cleared **{len(deleted)}** messages.", color=discord.Color.red()).set_footer(text=f"By {ctx.author.display_name}"), delete_after=10)


# ─── User: My Slot ───────────────────────────────────────────────────────────
@bot.command()
async def myslot(ctx):
    data = load_json(PINGCOUNT_PATH)
    for entry in data:
        if entry["userid"] == ctx.author.id:
            ch = ctx.guild.get_channel(entry["channelid"])
            end_ts = int(entry.get("endtime", 0))
            created_ts = int(entry.get("created_at", 0))
            pings = entry.get("ping_count", 0)
            mx = entry.get("max_pings", DEFAULT_PING_COUNT)
            warns = entry.get("warnings", 0)
            now = datetime.datetime.now().timestamp()
            total = end_ts - created_ts if created_ts else 1
            elapsed = now - created_ts if created_ts else 0
            progress = min(elapsed / total, 1.0) if total > 0 else 0
            e = discord.Embed(title="🎰 Your Slot", color=0x8A2BE2)
            e.add_field(name="Channel", value=ch.mention if ch else "Unknown", inline=True)
            e.add_field(name="Pings", value=f"{pings}/{mx} {make_bar(pings, mx)}", inline=True)
            e.add_field(name="Warnings", value=f"{'⚠️ ' * warns if warns else '✅ None'}", inline=True)
            e.add_field(name="Expires", value=f"<t:{end_ts}:R>" if end_ts else "Unknown", inline=True)
            if created_ts: e.add_field(name="Created", value=f"<t:{created_ts}:F>", inline=True)
            e.add_field(name="Progress", value=f"{make_bar(int(progress*100), 100, 15)} {int(progress*100)}%", inline=False)
            if ctx.author.avatar: e.set_thumbnail(url=ctx.author.avatar.url)
            e.set_footer(text=ctx.guild.name)
            return await ctx.send(embed=e)
    await ctx.send("❌ You don't have any active slots.")


# ─── User: Stats ─────────────────────────────────────────────────────────────
@bot.command()
async def stats(ctx):
    data = load_json(PINGCOUNT_PATH)
    history = load_json(HISTORY_PATH)
    bl = load_json(BLACKLIST_PATH)
    now = datetime.datetime.now().timestamp()
    total = len(data)
    active = sum(1 for e in data if now < float(e.get("endtime", 0)))
    expired = total - active
    total_warns = sum(e.get("warnings", 0) for e in data)
    uptime_secs = time.time() - bot_start_time
    # Count actions in last 24h
    day_ago = now - 86400
    recent = [h for h in history if h.get("timestamp", 0) > day_ago]
    created_24h = sum(1 for h in recent if h["action"] == "created")
    e = discord.Embed(title="📊 SlotBot Statistics", color=0x8A2BE2)
    e.add_field(name="🎰 Total Slots", value=f"**{total}**", inline=True)
    e.add_field(name="🟢 Active", value=f"**{active}** {make_bar(active, max(total,1))}", inline=True)
    e.add_field(name="🔴 Expired", value=f"**{expired}**", inline=True)
    e.add_field(name="👥 Members", value=f"**{ctx.guild.member_count}**", inline=True)
    e.add_field(name="🏓 Latency", value=f"**{round(bot.latency * 1000)}ms**", inline=True)
    e.add_field(name="⏱️ Uptime", value=f"**{format_uptime(uptime_secs)}**", inline=True)
    e.add_field(name="⚠️ Total Warnings", value=f"**{total_warns}**", inline=True)
    e.add_field(name="🚫 Blacklisted", value=f"**{len(bl)}**", inline=True)
    e.add_field(name="📈 Created (24h)", value=f"**{created_24h}**", inline=True)
    e.add_field(name="📜 History Entries", value=f"**{len(history)}**", inline=True)
    if ctx.guild.icon: e.set_thumbnail(url=ctx.guild.icon.url)
    e.set_footer(text="SlotBot v3.0 • @codewithriza")
    await ctx.send(embed=e)


# ─── User: Uptime ────────────────────────────────────────────────────────────
@bot.command()
async def uptime(ctx):
    secs = time.time() - bot_start_time
    e = discord.Embed(title="⏱️ Bot Uptime", description=f"**{format_uptime(secs)}**\n\nStarted <t:{int(bot_start_time)}:R>", color=0x8A2BE2)
    e.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    await ctx.send(embed=e)


# ─── User: Server Info ───────────────────────────────────────────────────────
@bot.command()
async def serverinfo(ctx):
    g = ctx.guild
    e = discord.Embed(title=f"🏠 {g.name}", color=0x8A2BE2)
    if g.icon: e.set_thumbnail(url=g.icon.url)
    e.add_field(name="👑 Owner", value=g.owner.mention if g.owner else "Unknown", inline=True)
    e.add_field(name="👥 Members", value=f"**{g.member_count}**", inline=True)
    e.add_field(name="💬 Channels", value=f"**{len(g.text_channels)}** text / **{len(g.voice_channels)}** voice", inline=True)
    e.add_field(name="🎭 Roles", value=f"**{len(g.roles)}**", inline=True)
    e.add_field(name="😀 Emojis", value=f"**{len(g.emojis)}**", inline=True)
    e.add_field(name="🔒 Verification", value=str(g.verification_level).title(), inline=True)
    e.add_field(name="📅 Created", value=f"<t:{int(g.created_at.timestamp())}:F>", inline=True)
    e.add_field(name="🆔 Server ID", value=f"`{g.id}`", inline=True)
    slots_data = load_json(PINGCOUNT_PATH)
    e.add_field(name="🎰 Active Slots", value=f"**{len(slots_data)}**", inline=True)
    if g.banner: e.set_image(url=g.banner.url)
    e.set_footer(text=f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=e)


# ─── User: Leaderboard ───────────────────────────────────────────────────────
@bot.command()
async def leaderboard(ctx):
    data = load_json(PINGCOUNT_PATH)
    if not data: return await ctx.send("ℹ️ No slots to show.")
    now = datetime.datetime.now().timestamp()
    # Sort by remaining time (most time left = top)
    active = [e for e in data if now < float(e.get("endtime", 0))]
    active.sort(key=lambda x: float(x.get("endtime", 0)), reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, e in enumerate(active[:10]):
        mem = ctx.guild.get_member(e["userid"])
        ms = mem.mention if mem else f"<@{e['userid']}>"
        et = int(e.get("endtime", 0))
        remaining = et - now
        days_left = int(remaining / 86400)
        medal = medals[i] if i < 3 else f"`{i+1}.`"
        lines.append(f"{medal} {ms} — **{days_left}** days left (<t:{et}:R>)")
    embed = discord.Embed(title="🏆 Slot Leaderboard", description="\n".join(lines) if lines else "No active slots.", color=0xFFD700)
    embed.set_footer(text=f"Top {len(lines)} slots by remaining time")
    await ctx.send(embed=embed)


# ─── User: History ────────────────────────────────────────────────────────────
@bot.command()
async def history(ctx):
    hist = load_json(HISTORY_PATH)
    if not hist: return await ctx.send("ℹ️ No history yet.")
    recent = hist[-15:][::-1]  # Last 15, newest first
    action_icons = {"created": "🎰", "renewed": "🔄", "revoked": "🚫", "expired": "⏰", "transferred": "🔀", "extended": "⏳", "held": "⚠️", "unheld": "✅", "warned": "⚠️", "blacklisted": "🚫", "unblacklisted": "✅", "deleted": "🗑️"}
    lines = []
    for h in recent:
        icon = action_icons.get(h["action"], "📋")
        ts = h.get("timestamp", 0)
        uid = h.get("userid", h.get("from_user", 0))
        lines.append(f"{icon} **{h['action'].title()}** — <@{uid}> <t:{ts}:R>")
    embed = discord.Embed(title="📜 Recent Activity", description="\n".join(lines), color=0x8A2BE2)
    embed.set_footer(text=f"Showing last {len(recent)} actions")
    await ctx.send(embed=embed)


# ─── Slash Commands ──────────────────────────────────────────────────────────
@bot.tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(title="🏓 Pong!", description=f"Latency: **{round(bot.
latency * 1000)}ms**", color=0x8A2BE2), ephemeral=True)

@bot.tree.command(name="slotinfo", description="View slot information")
@app_commands.describe(channel="The slot channel to check")
async def slash_slotinfo(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not channel: channel = interaction.channel
    slot = get_slot_data(channel.id)
    if not slot: return await interaction.response.send_message("No slot data found.", ephemeral=True)
    mem = interaction.guild.get_member(slot["userid"])
    ms = mem.mention if mem else f"<@{slot[chr(39)+'userid'+chr(39)]}> (left)"
    et = int(slot.get("endtime", 0))
    pings = slot.get("ping_count", 0)
    mx = slot.get("max_pings", 3)
    e = discord.Embed(title=f"Slot Info", color=0x8A2BE2)
    e.add_field(name="Owner", value=ms, inline=True)
    e.add_field(name="Pings", value=f"{pings}/{mx}", inline=True)
    e.add_field(name="Expires", value=f"<t:{et}:R>" if et else "Unknown", inline=True)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="stats", description="View bot statistics")
async def slash_stats(interaction: discord.Interaction):
    data = load_json(PINGCOUNT_PATH)
    now = datetime.datetime.now().timestamp()
    total = len(data)
    active = sum(1 for e in data if now < float(e.get("endtime", 0)))
    e = discord.Embed(title="Bot Statistics", color=0x8A2BE2)
    e.add_field(name="Total Slots", value=str(total), inline=True)
    e.add_field(name="Active", value=str(active), inline=True)
    e.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    e.add_field(name="Members", value=str(interaction.guild.member_count), inline=True)
    e.add_field(name="Uptime", value=format_uptime(time.time() - bot_start_time), inline=True)
    if interaction.guild.icon: e.set_thumbnail(url=interaction.guild.icon.url)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="myslot", description="View your slot information")
async def slash_myslot(interaction: discord.Interaction):
    slot = get_user_slot(interaction.user.id)
    if not slot: return await interaction.response.send_message("You don't have a slot.", ephemeral=True)
    ch = interaction.guild.get_channel(slot["channelid"])
    et = int(slot.get("endtime", 0))
    pings = slot.get("ping_count", 0)
    mx = slot.get("max_pings", 3)
    e = discord.Embed(title="Your Slot", color=0x8A2BE2)
    e.add_field(name="Channel", value=ch.mention if ch else "Unknown", inline=True)
    e.add_field(name="Pings", value=f"{pings}/{mx}", inline=True)
    e.add_field(name="Expires", value=f"<t:{et}:R>" if et else "Unknown", inline=True)
    await interaction.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name="serverinfo", description="View server information")
async def slash_serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    e = discord.Embed(title=g.name, color=0x8A2BE2)
    if g.icon: e.set_thumbnail(url=g.icon.url)
    e.add_field(name="Members", value=str(g.member_count), inline=True)
    e.add_field(name="Channels", value=f"{len(g.text_channels)}T / {len(g.voice_channels)}V", inline=True)
    e.add_field(name="Roles", value=str(len(g.roles)), inline=True)
    e.add_field(name="Created", value=f"<t:{int(g.created_at.timestamp())}:F>", inline=True)
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="leaderboard", description="View slot leaderboard")
async def slash_leaderboard(interaction: discord.Interaction):
    data = load_json(PINGCOUNT_PATH)
    now = datetime.datetime.now().timestamp()
    active = sorted([e for e in data if now < float(e.get("endtime", 0))], key=lambda x: float(x.get("endtime", 0)), reverse=True)
    medals = ["1.", "2.", "3."]
    lines = []
    for i, e in enumerate(active[:10]):
        mem = interaction.guild.get_member(e["userid"])
        ms = mem.mention if mem else f"<@{e[chr(39)+'userid'+chr(39)]}> "
        et = int(e.get("endtime", 0))
        days = int((et - now) / 86400)
        m = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{m} {ms} - {days} days left")
    embed = discord.Embed(title="Slot Leaderboard", description=chr(10).join(lines) if lines else "No active slots.", color=0xFFD700)
    await interaction.response.send_message(embed=embed)


# ─── Ticket System ───────────────────────────────────────────────────────────
class TicketCloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        is_staff = staff_role and staff_role in interaction.user.roles
        tickets = load_json(TICKETS_PATH)
        ticket = next((t for t in tickets if t.get("channelid") == interaction.channel.id), None)
        is_owner = ticket and ticket.get("userid") == interaction.user.id
        if not is_staff and not is_owner:
            return await interaction.response.send_message("❌ Only staff or the ticket creator can close this.", ephemeral=True)
        await interaction.response.send_message(embed=discord.Embed(title="🔒 Closing Ticket", description="Saving transcript and closing in 5 seconds...", color=discord.Color.orange()))
        # Generate transcript
        messages = []
        async for msg in interaction.channel.history(limit=200, oldest_first=True):
            ts = msg.created_at.strftime("%Y-%m-%d %H:%M")
            messages.append(f"[{ts}] {msg.author.display_name}: {msg.content}")
        transcript = "\n".join(messages)
        # Try to DM transcript to ticket creator
        if ticket:
            creator = interaction.guild.get_member(ticket["userid"])
            if creator:
                try:
                    dm_embed = discord.Embed(title=f"📋 Ticket Transcript – #{interaction.channel.name}", description=f"Your ticket in **{interaction.guild.name}** has been closed.", color=0x8A2BE2)
                    await creator.send(embed=dm_embed)
                    if len(transcript) <= 1990:
                        await creator.send(f"```\n{transcript}\n```")
                    else:
                        await creator.send(f"```\n{transcript[:1990]}\n```\n*(truncated)*")
                except discord.Forbidden:
                    pass
            # Remove from tickets data
            tickets = [t for t in tickets if t.get("channelid") != interaction.channel.id]
            save_json(TICKETS_PATH, tickets)
        # Log
        await send_log(interaction.guild, discord.Embed(title="📋 Ticket Closed", description=f"**Channel:** #{interaction.channel.name}\n**Closed by:** {interaction.user.mention}", color=discord.Color.orange(), timestamp=datetime.datetime.now()))
        add_to_history("ticket_closed", userid=interaction.user.id, channelid=interaction.channel.id)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")
        except discord.Forbidden:
            await interaction.channel.send("❌ Cannot delete channel – missing permissions.")


class TicketCreateButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, emoji="🎫", custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user already has an open ticket
        tickets = load_json(TICKETS_PATH)
        existing = next((t for t in tickets if t.get("userid") == interaction.user.id), None)
        if existing:
            ch = interaction.guild.get_channel(existing["channelid"])
            if ch:
                return await interaction.response.send_message(f"❌ You already have an open ticket: {ch.mention}", ephemeral=True)
            else:
                tickets = [t for t in tickets if t.get("userid") != interaction.user.id]
                save_json(TICKETS_PATH, tickets)
        # Create ticket channel
        cat = discord.utils.get(interaction.guild.categories, id=TICKET_CATEGORY_ID) if TICKET_CATEGORY_ID else None
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=cat, overwrites=overwrites)
        # Save ticket
        tickets.append({"userid": interaction.user.id, "channelid": ch.id, "created_at": int(datetime.datetime.now().timestamp())})
        save_json(TICKETS_PATH, tickets)
        # Send welcome embed
        e = discord.Embed(title="🎫 Ticket Opened", description=f"Welcome {interaction.user.mention}!\n\nPlease describe your issue or request.\nA staff member will assist you shortly.\n\n**Click the button below to close this ticket.**", color=0x8A2BE2)
        e.set_footer(text=f"Ticket created by {interaction.user.display_name}")
        await ch.send(embed=e, view=TicketCloseButton())
        await ch.send(f"{interaction.user.mention} {'| ' + staff_role.mention if staff_role else ''}")
        await interaction.response.send_message(f"✅ Ticket created: {ch.mention}", ephemeral=True)
        add_to_history("ticket_created", userid=interaction.user.id, channelid=ch.id)
        await send_log(interaction.guild, discord.Embed(title="📋 Ticket Created", description=f"**User:** {interaction.user.mention}\n**Channel:** {ch.mention}", color=discord.Color.green(), timestamp=datetime.datetime.now()))


@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def ticket(ctx):
    """Send a ticket panel with a create button."""
    e = discord.Embed(title="🎫 Support Tickets", description="Need help? Want to buy a slot? Have an issue?\n\n**Click the button below to create a ticket!**\n\nA private channel will be created for you.", color=0x8A2BE2)
    if ctx.guild.icon:
        e.set_thumbnail(url=ctx.guild.icon.url)
    e.set_footer(text=f"{ctx.guild.name} • Ticket System")
    await ctx.message.delete()
    await ctx.send(embed=e, view=TicketCreateButton())
    logger.info(f"Ticket panel sent by {ctx.author}")


@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def closeticket(ctx):
    """Close the current ticket channel."""
    tickets = load_json(TICKETS_PATH)
    ticket = next((t for t in tickets if t.get("channelid") == ctx.channel.id), None)
    if not ticket:
        return await ctx.reply("❌ This is not a ticket channel.")
    # Generate transcript
    messages = []
    async for msg in ctx.channel.history(limit=200, oldest_first=True):
        ts = msg.created_at.strftime("%Y-%m-%d %H:%M")
        messages.append(f"[{ts}] {msg.author.display_name}: {msg.content}")
    transcript = "\n".join(messages)
    creator = ctx.guild.get_member(ticket["userid"])
    if creator:
        try:
            dm_embed = discord.Embed(title=f"📋 Ticket Transcript – #{ctx.channel.name}", description=f"Your ticket in **{ctx.guild.name}** has been closed by staff.", color=0x8A2BE2)
            await creator.send(embed=dm_embed)
            if len(transcript) <= 1990:
                await creator.send(f"```\n{transcript}\n```")
            else:
                await creator.send(f"```\n{transcript[:1990]}\n```\n*(truncated)*")
        except discord.Forbidden:
            pass
    tickets = [t for t in tickets if t.get("channelid") != ctx.channel.id]
    save_json(TICKETS_PATH, tickets)
    add_to_history("ticket_closed", userid=ctx.author.id, channelid=ctx.channel.id)
    await send_log(ctx.guild, discord.Embed(title="📋 Ticket Closed", description=f"**Channel:** #{ctx.channel.name}\n**Closed by:** {ctx.author.mention}", color=discord.Color.orange(), timestamp=datetime.datetime.now()))
    await ctx.send(embed=discord.Embed(title="🔒 Closing Ticket", description="Closing in 5 seconds...", color=discord.Color.orange()))
    await asyncio.sleep(5)
    try:
        await ctx.channel.delete(reason=f"Ticket closed by {ctx.author}")
    except discord.Forbidden:
        await ctx.send("❌ Cannot delete – missing permissions.")


# ─── Redeem System ───────────────────────────────────────────────────────────
def generate_redeem_code(length=12):
    """Generate a random redeem code."""
    chars = string.ascii_uppercase + string.digits
    code = "-".join("".join(random.choices(chars, k=4)) for _ in range(length // 4))
    return code


@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def createredeem(ctx, duration: int = None, unit: str = None, pings: int = None, category: str = "category1", uses: int = 1):
    """Create a redeem code for a slot. Usage: ,createredeem 7 d 3 category1 1"""
    if not duration or not unit:
        return await ctx.reply(f"❌ Usage: `{PREFIX}createredeem 7 d 3 category1 1`\n`duration unit pings category uses`")
    if unit.lower() not in ("d", "m"):
        return await ctx.reply("❌ Unit must be `d` (days) or `m` (months).")
    if pings is None:
        pings = DEFAULT_PING_COUNT
    if category.lower() not in ("category1", "category2"):
        return await ctx.reply("❌ Category must be `category1` or `category2`.")
    code = generate_redeem_code()
    redeems = load_json(REDEEMS_PATH)
    redeems.append({
        "code": code,
        "duration": duration,
        "unit": unit.lower(),
        "pings": pings,
        "category": category.lower(),
        "max_uses": uses,
        "uses": 0,
        "created_by": ctx.author.id,
        "created_at": int(datetime.datetime.now().timestamp()),
        "redeemed_by": [],
    })
    save_json(REDEEMS_PATH, redeems)
    dur_str = f"{duration} day{'s' if duration != 1 else ''}" if unit.lower() == "d" else f"{duration} month{'s' if duration != 1 else ''}"
    e = discord.Embed(title="🎟️ Redeem Code Created", color=discord.Color.green())
    e.add_field(name="Code", value=f"```{code}```", inline=False)
    e.add_field(name="Duration", value=dur_str, inline=True)
    e.add_field(name="Pings", value=str(pings), inline=True)
    e.add_field(name="Category", value=category, inline=True)
    e.add_field(name="Max Uses", value=str(uses), inline=True)
    e.set_footer(text=f"Created by {ctx.author.display_name}")
    await ctx.reply(embed=e)
    add_to_history("redeem_created", staff=ctx.author.id, code=code, duration=dur_str)
    await send_log(ctx.guild, discord.Embed(title="📋 Redeem Code Created", description=f"**Code:** `{code}`\n**Duration:** {dur_str}\n**Uses:** {uses}\n**By:** {ctx.author.mention}", color=discord.Color.green(), timestamp=datetime.datetime.now()))
    logger.info(f"Redeem code {code} created by {ctx.author}")


@bot.command()
async def redeem(ctx, code: str = None):
    """Redeem a code to get a slot. Usage: ,redeem CODE"""
    if not code:
        return await ctx.reply(f"❌ Usage: `{PREFIX}redeem YOUR-CODE-HERE`")
    if is_blacklisted(ctx.author.id):
        return await ctx.reply("❌ You are **blacklisted** and cannot redeem codes.")
    existing = get_user_slot(ctx.author.id)
    if existing:
        return await ctx.reply(f"⚠️ You already have a slot in <#{existing['channelid']}>.")
    redeems = load_json(REDEEMS_PATH)
    redeem_entry = None
    for r in redeems:
        if r["code"].upper() == code.upper():
            redeem_entry = r
            break
    if not redeem_entry:
        return await ctx.reply("❌ Invalid redeem code.")
    if redeem_entry["uses"] >= redeem_entry["max_uses"]:
        return await ctx.reply("❌ This code has already been fully redeemed.")
    if ctx.author.id in redeem_entry.get("redeemed_by", []):
        return await ctx.reply("❌ You have already used this code.")
    # Create the slot
    member = ctx.author
    duration = redeem_entry["duration"]
    unit = redeem_entry["unit"]
    pings = redeem_entry["pings"]
    category = redeem_entry["category"]
    cat_id = CATEGORY_ID_1 if category == "category1" else CATEGORY_ID_2
    end_ts = int((duration * 86400 if unit == "d" else duration * 30 * 86400) + datetime.datetime.now().timestamp())
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, mention_everyone=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, mention_everyone=True),
    }
    cat = discord.utils.get(ctx.guild.categories, id=cat_id)
    if not cat:
        return await ctx.reply("❌ Slot category not found. Contact staff.")
    ch = await ctx.guild.create_text_channel(member.display_name, category=cat, overwrites=overwrites)
    for rid in [PREMIUM_ROLE_ID, SLOT_ROLE_ID]:
        r = discord.utils.get(ctx.guild.roles, id=rid)
        if r: await member.add_roles(r)
    await ch.send(embed=build_rules_embed(ctx.guild))
    dur_str = f"{duration} day{'s' if duration != 1 else ''}" if unit == "d" else f"{duration} month{'s' if duration != 1 else ''}"
    ie = discord.Embed(title="🎟️ Slot Redeemed!", description=f"**Owner:** {member.mention}\n**Duration:** {dur_str}\n**Expires:** <t:{end_ts}:R> (<t:{end_ts}:F>)\n**Pings:** {pings}", color=discord.Color.gold())
    ie.set_footer(text=ctx.guild.name)
    if member.avatar: ie.set_author(name=str(member), icon_url=member.avatar.url)
    else: ie.set_author(name=str(member))
    await ch.send(embed=ie)
    entry = {"endtime": end_ts, "userid": member.id, "channelid": ch.id, "ping_count": pings, "max_pings": pings, "created_at": int(datetime.datetime.now().timestamp()), "created_by": member.id, "warnings": 0}
    for p in [PINGCOUNT_PATH, DATA_PATH]:
        d = load_json(p); d.append(entry); save_json(p, d)
    # Update redeem usage
    redeem_entry["uses"] += 1
    redeem_entry["redeemed_by"].append(ctx.author.id)
    save_json(REDEEMS_PATH, redeems)
    await ctx.reply(f"✅ Code redeemed! Your slot: {ch.mention}")
    add_to_history("redeemed", userid=member.id, channelid=ch.id, code=code.upper(), duration=dur_str)
    await send_log(ctx.guild, discord.Embed(title="📋 Code Redeemed", description=f"**User:** {member.mention}\n**Code:** `{code.upper()}`\n**Channel:** {ch.mention}\n**Duration:** {dur_str}", color=discord.Color.gold(), timestamp=datetime.datetime.now()))
    logger.info(f"Code {code.upper()} redeemed by {member}")


@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def redeems(ctx):
    """List all redeem codes."""
    data = load_json(REDEEMS_PATH)
    if not data:
        return await ctx.reply("ℹ️ No redeem codes exist.")
    lines = []
    for i, r in enumerate(data, 1):
        status = "✅" if r["uses"] < r["max_uses"] else "❌"
        dur = f"{r['duration']}{'d' if r['unit'] == 'd' else 'm'}"
        lines.append(f"`{i}.` {status} `{r['code']}` — {dur} | {r['uses']}/{r['max_uses']} uses | {r['pings']} pings")
    e = discord.Embed(title=f"🎟️ Redeem Codes ({len(data)})", description="\n".join(lines), color=0x8A2BE2)
    e.set_footer(text="✅ = Available | ❌ = Fully used")
    await ctx.send(embed=e)


@bot.command()
@commands.has_role(STAFF_ROLE_ID)
async def deleteredeem(ctx, code: str = None):
    """Delete a redeem code."""
    if not code:
        return await ctx.reply(f"❌ Usage: `{PREFIX}deleteredeem CODE`")
    data = load_json(REDEEMS_PATH)
    new_data = [r for r in data if r["code"].upper() != code.upper()]
    if len(new_data) == len(data):
        return await ctx.reply("❌ Code not found.")
    save_json(REDEEMS_PATH, new_data)
    await ctx.reply(f"✅ Redeem code `{code.upper()}` deleted.")
    logger.info(f"Redeem code {code.upper()} deleted by {ctx.author}")


# Register persistent views on startup
@bot.event
async def on_connect():
    bot.add_view(TicketCreateButton())
    bot.add_view(TicketCloseButton())


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        logger.error("No bot token! Set in config.json or SLOTBOT_TOKEN env var.")
        exit(1)
    logger.info("Starting SlotBot v3.0...")
    bot.run(TOKEN, log_handler=None)
