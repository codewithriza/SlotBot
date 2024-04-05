# Slot Bot - A Discord bot for managing slots
# Made by Riza (https://github.com/codewithriza/SlotBot)
# Contact for help - https://discord.com/users/887532157747212370
# Create an issue in this repo for support: https://github.com/codewithriza/SlotBot/issues

import discord
from discord.ext import commands, tasks
import config
import datetime
import json
import os
from colorama import Fore
import asyncio
import time
import os


# Bot configuration
bot = commands.Bot(
    command_prefix=",",
    intents=discord.Intents.all(),
    status=discord.Status.dnd,
    activity=discord.Activity(
        type=discord.ActivityType.watching, name="Riza" #change activity here
    ), 
    guild=discord.Object(id=1218925217129435186)  # Paste your guild id
)
bot.remove_command("help")

# Load configuration data from config.json
with open("config.json", "r") as file:
    config_data = json.load(file)
    staff_role = config_data["staffrole"]
    premium_role_id = config_data["premiumeroleid"]
    guild_id = config_data["guildid"]
    category_id = config_data["categoryid"]


# Bot event - called when the bot is ready
@bot.event
async def on_ready():
    print("\033[94m" + """
    
    ███████╗██╗███████╗░█████╗░
    ██╔══██╗██║╚════██║██╔══██╗
    ██████╔╝██║░░███╔═╝███████║
    ██╔══██╗██║██╔══╝░░██╔══██║
    ██║░░██║██║███████╗██║░░██║
    ╚═╝░░╚═╝╚═╝╚══════╝╚═╝░░╚═╝
    
    """ + "\033[0m" + "Made By @codewithriza")
    print("Bot is ready!")

    # Sync guild information
    await bot.tree.sync()

# Bot command - provides help information
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        description="**,create** - Use To Create Slot `,create @usermention 1 m slotname`\n**,add** - Use To Add User In Slot`,add @usermention`\n**,remove** - Use To Remove User In SLot\n**,renew** - Use To Renew Slot\n**,hold\n**,**unhold**",
        color=0x8A2BE2
    )
    embed.set_thumbnail(url=ctx.guild.icon)
    embed.set_author(name="Slot Bot Help Menu")
    await ctx.send(embed=embed, delete_after=30)


# Function to get slot owner based on channel ID
def get_slot_owner(channel_id):
    try:
        with open("pingcount.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    for entry in data:
        if entry.get('channelid') == channel_id:
            return entry.get('userid')

    return None

# Command to hold a slot
@bot.command()
@commands.has_role(int(staff_role))
async def hold(ctx):
    channel = ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)

    # Find the slot owner
    user_id = get_slot_owner(channel.id)

    if user_id is None:
        await ctx.reply("Could not find slot owner")
        return

    # Create the embed
    embed = discord.Embed(title="SLOT ON HOLD",
                          description=f"A report is open against <@{user_id}>\nDo not start a deal with them until the slot is open",
                          color=0x8A2BE2)
    embed.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/warning-xxl.png")
    embed.set_footer(text=f"{ctx.author.display_name} has held the slot")

    # Send the embed
    await channel.send(embed=embed)

# Command to unhold a slot
@bot.command()
@commands.has_role(int(staff_role))
async def unhold(ctx):
    channel = ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)

    # Create the embed
    embed = discord.Embed(title="UNHELD SLOT",
                          description="Slot has been unheld and the case has been solved.",
                          color=0x8A2BE2)
    embed.set_footer(text=f"Slot unheld by {ctx.author.display_name}")
    embed.set_thumbnail(url="")  # paste your guild logo

    # Send the embed
    await channel.send(embed=embed)

# Command to add a role to a user
@bot.command()
@commands.has_role(int(staff_role))
async def add(ctx, member: discord.Member):
    role = ctx.guild.get_role(123456789)  # Paste the buyer role id
    await member.add_roles(role)
    await ctx.send(f"Added role {role.name} to {member.display_name}")

# Command to renew a slot
@bot.command()
@commands.has_role(int(staff_role))
async def renew(ctx, member: discord.Member = None, channel: discord.TextChannel = None, yoyo: str = None, cx: str = None):
    if member is None:
        await ctx.reply("Member Not Found")
        return

    if channel is None:
        await ctx.reply("Channel Not Found")
        return

    if yoyo is None or cx is None:
        await ctx.reply("Use valid Format: ,renew @user #channel 1 m/d his Slot")
        return

    yoyo_value = None
    try:
        yoyo_value = int(yoyo[:-1]) if yoyo.endswith(('m', 'd')) else None
    except ValueError:
        pass

    if yoyo_value is None:
        await ctx.reply("Use valid Format: ,renew @user #channel 1 m/d his Slot")
        return

    if cx.lower() == "d":
        yoyo_value = (yoyo_value * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    elif cx.lower() == "m":
        yoyo_value = (yoyo_value * 30 * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    else:
        await ctx.reply("Use valid Format: ,renew @user #channel 1 m/d his Slot")
        return

    await channel.set_permissions(member, view_channel=True, send_messages=True, mention_everyone=True)
    role = discord.utils.get(ctx.guild.roles, id=int(rid))
    await member.add_roles(role)
    print("ruw")
    async for message in channel.history(limit=1000):
        await message.delete()
    dataz = {
        "endtime": yoyo,
        "userid": member.id,
        "channelid": channel.id
    },
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    data.append(dataz)
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

    embed = discord.Embed(description="""Paste your slot rules here""", color=0x8A2BE2)

    embed.set_author(name="Slot Rules")
    embed.set_thumbnail(url=f"{ctx.guild.icon}")

    await channel.send(embed=embed)
    embed = discord.Embed(description=f'**Slot Owner:** {member.mention}\n**End:** <t:{int(yoyo)}:R>', color=0x8A2BE2)
    embed.set_footer(text=ctx.guild.name)
    embed.set_author(name=member)
    await channel.send(embed=embed)
    await ctx.reply(f"successfully renew Slot {channel.mention}")

# Command to remove a role from a user
@bot.command()
@commands.has_role(int(staff_role))
async def remove(ctx, member: discord.Member):
    role = ctx.guild.get_role(123456789)  # replace with the buyer role id
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"Removed role {role.name} from {member.display_name}")
    else:
        await ctx.send(f"{member.display_name} doesn't have the role {role.name}")

# Command to revoke slot permissions
@bot.command()
@commands.has_role(int(staff_role))
async def revoke(ctx, member: discord.Member = None, channel: discord.TextChannel = None):

    rr = []

    with open("./data.json", "r") as rr:
        rr = json.load(rr)

    ftf = False

    for x in rr:
        for xx in x:
            if (xx["channelid"] == channel.id):
                ftf = True

    if (ftf == False):
        await ctx.send("Slot Not In DataBase")
        return

    if (member == False):
        await ctx.reply("Member Not Found")

    if (channel == False):
        await ctx.reply("Channel Not Found")

    await channel.set_permissions(member, send_messages=True, mention_everyone=False)
    await ctx.reply("successfully removed")

# Command to create a new slot
@bot.command()
@commands.has_role(int(staff_role))
async def create(ctx, member: discord.Member = None, yoyo: int = None, cx=None, ping_count: int = 0, category: str = "category1", *, x=None):
    if member is None:
        await ctx.reply("User Not Found")
        return

    if yoyo is None:
        await ctx.reply("Use valid Format: ,create @user 1 d his Slot")
        return

    if cx is None:
        await ctx.reply("Use valid Format: ,create @user 1 d his Slot")
        return

    if category.lower() not in ['category1', 'category2']:
        await ctx.reply("Invalid category. Please choose either 'category1' or 'category2'.")
        return

    # Determine the category ID based on the user's choice
    if category.lower() == 'category1':
        category_id = 123456789  # Category 1 ID
    else:
        category_id = 123456789  # Category 2 ID

    if x is None:
        x = member.display_name

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, mention_everyone=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, mention_everyone=True)
    }

    category = discord.utils.get(ctx.guild.categories, id=category_id)

    a = await ctx.guild.create_text_channel(x, category=category, overwrites=overwrites)

    await a.set_permissions(ctx.guild.default_role, send_messages=False)
    role = discord.utils.get(ctx.author.guild.roles, id=int(rid))
    await member.add_roles(role)
    embed = discord.Embed(title="SLOT RULES", color=0x8A2BE2)
    rules = """Paste your slot rules here"""
    embed.add_field(name="Rules", value=rules, inline=False)
    embed.set_image(url="add url to your logo")
    await a.send(embed=embed)

    if cx.lower() == "d":
        yoyo = (yoyo * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    elif cx.lower() == "m":
        yoyo = (yoyo * 30 * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    else:
        await ctx.reply("Use valid Format: ,create @user 1 m 4 slotname")

    embed = discord.Embed(description=f'**Slot Owner:** {member.mention}\n**End:** <t:{int(yoyo)}:R>\n**Ping Count:** {ping_count}', color=0x8A2BE2)
    embed.set_footer(text=ctx.guild.name)
    embed.set_author(name=member)
    await a.send(embed=embed)
    await ctx.reply(f"successfully Create Slot {a.mention}")

    dataz = {
        "endtime": yoyo,
        "userid": member.id,
        "channelid": a.id,
        "ping_count": ping_count  # Store the initial ping count
    }

    try:
        with open("pingcount.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.append(dataz)

    with open("pingcount.json", "w") as file:
        json.dump(data, file, indent=4)

# Command to ping users in a slot
@bot.command()
async def ping(ctx):
    try:
        with open("pingcount.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    for i, user_data in enumerate(data):
        if user_data["userid"] == ctx.author.id:
            # Check if the user is the owner of the channel
            if ctx.channel.id == user_data["channelid"]:
                # Check if the user has any ping counts left
                if user_data["ping_count"] > 0:
                    # Decrement the ping count
                    data[i]["ping_count"] -= 1
                    with open("pingcount.json", "w") as file:
                        json.dump(data, file, indent=4)

                    # Send @here
                    here_message = await ctx.send("@here")

                    # Send a message in an embed format
                    embed = discord.Embed(
                        title="Ping Detected",
                        description=f"{ctx.author.mention} pinged @here in their slot! You have {data[i]['ping_count']} ping{'s' if data[i]['ping_count'] != 1 else ''} left.\n\n**Use <#123456789>**",  # replace #123456789 with your own channel id
                        color=0xFFFF00
                    )
                    await ctx.send(embed=embed)

                    # Wait for 5 seconds
                    await asyncio.sleep(5)

                    # Delete the @here message
                    await here_message.delete()
                    return

                else:
                    await ctx.send("You have used all your pings.")
                    return
            else:
                await ctx.send("You can only use the ping command in your slot channel.")
                return
    await ctx.send("You don't have any slots. Create a slot to get pings.")

bot.run("token")
