# Slot Bot - A Discord bot for managing slots
# Made by Riza (https://github.com/codewithriza/SlotBot)
# Contact for help - https://discord.com/users/887532157747212370
# Create an issue in this repo for support: https://github.com/codewithriza/SlotBot/issues


import discord
from discord.ext import commands , tasks
import datetime
import json
import os
from colorama import Fore

bot = commands.Bot(
    command_prefix=",",
    intents=discord.Intents.all(),
    status=discord.Status.dnd,
    activity=discord.Activity(
        type=discord.ActivityType.watching, name="Riza"
    ),
    guild = discord.Object(id=1229389945626693714) # Change it with your guild id right click on your server and copy the server id and paste it instead of 1229389945626693714
)
bot.remove_command("help")


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
    await bot.tree.sync()
    bot.add_view(CreateButton())
    bot.add_view(CloseButton())
    bot.add_view(TrashButton())
with open("config.json", "r") as file:
    hmm = json.load(file)

rid = hmm["premiumeroleid"]
cid = hmm["categoryid"]
staff = hmm["staffrole"]
print(rid)
@tasks.loop(hours=1)
async def expire():
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    nowtime = datetime.datetime.now()
    nt = nowtime.strftime("%Y%m%d")
    remove = []

    for xd in data:
        for item in xd:
            slottime = item["endtime"]
            st = datetime.datetime.fromtimestamp(int(slottime))
            print(st.strftime("%Y%m%d"))
            finalse = st.strftime("%Y%m%d")
            print(f"Slot end {finalse}")
            print(f"now time {nt}")
            print(nt >= finalse)

            if nt >= finalse:
                
                with open("data.json", "w") as file:
                    json.dump(data, file, indent=4)
                
                channel = bot.get_channel(item["channelid"])
                guild = bot.get_guild(int(hmm["guildid"]))
                member = guild.get_member(item["userid"])
                await bot.tree.sync()

@bot.command()
async def help(ctx):
    embed = discord.Embed(description="**,create** - Use To Create Slot `,create @user 7 d 2 category1 slotname`\n**,add** - Use To Add User In Slot`,add @usermention`\n**,remove** - Use To Remove User In SLot\n**,renew** - Use To Renew Slot\n**,hold\n**,**unhold**\n**,nuke\n**/ping @everyone/@here",color=0x8A2BE2)
    embed.set_thumbnail(url=ctx.guild.icon)
    embed.set_author(name="Slot Bot Help Menu")
    await ctx.send(embed=embed,delete_after=30)


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


@bot.command()
async def delete(ctx):
    if discord.utils.get(ctx.guild.roles, id=1229402537648455700) in ctx.author.roles:
        try:
            await ctx.channel.delete()
            await ctx.send("Channel deleted successfully.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to delete this channel.")
    else:
        await ctx.send("You do not have the necessary role to use this command.")


@bot.command()
@commands.has_role(int(staff))
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




@bot.command()
@commands.has_role(int(staff))
async def unhold(ctx):
    channel = ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)

    # Create the embed
    embed = discord.Embed(title="UNHELD SLOT",
                          description="Slot has been unheld and the case has been solved.",
                          color=0x8A2BE2)
    embed.set_footer(text=f"Slot unheld by {ctx.author.display_name}")
    embed.set_thumbnail(url="https://wallpapers-clan.com/wp-content/uploads/2022/10/rick-sanchez-pfp-26.jpg")

    # Send the embed
    await channel.send(embed=embed)



@bot.command()
@commands.has_role(int(staff))
async def add(ctx, member: discord.Member):
    role = ctx.guild.get_role(1229474713345069199)
    await member.add_roles(role)
    await ctx.send(f"Added role {role.name} to {member.display_name}")
@bot.command()
@commands.has_role(int(staff))
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

    await channel.set_permissions(member,view_channel=True,send_messages=True,mention_everyone=True)
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
            json.dump(data, file,indent=4)
     
    embed = discord.Embed(description="""We don't offer any refunds.
You can't sell or share your slot.
If you promote any server your slot will be revoked.
If you scam your slot will get Revoked and you will get banned.
We can put your slot on hold at any time.
If you do not save the transcript of the ticket when you bought it if you or our server will get Termed you will not get your slot back.
We recommend to use MM, if the slot user denies MM, we have the right to revoke your slot.
You are not allowed to advertise your server invite or telegram invite.
ping reset | every 24 hours
positions are never fixed
If we see that your slot is inactive and is hardly used, we have the right to revoke your slot without a refund.
we can change the rules whenever we want without further notice
overpinging will lead in an instant slot revoke without any refund
Inactivity For More Than 2 Days Will Result In Removal Of Slot (YOU WILL BE WARNED FIRST)""",color=0x8A2BE2)

    embed.set_author(name="Slot Rules")
    embed.set_thumbnail(url=f"{ctx.guild.icon}")

    await channel.send(embed=embed)
    embed = discord.Embed(description=f'**Slot Owner:** {member.mention}\n**End:** <t:{int(yoyo)}:R>',color=0x8A2BE2)
    embed.set_footer(text=ctx.guild.name)
    embed.set_author(name=member)
    await channel.send(embed=embed)
    await ctx.reply(f"successfully renew Slot {channel.mention}")


@bot.command()
@commands.has_role(int(staff))
async def remove(ctx, member: discord.Member):
    role = ctx.guild.get_role(1229474713345069199)
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"Removed role {role.name} from {member.display_name}")
    else:
        await ctx.send(f"{member.display_name} doesn't have the role {role.name}")


@bot.command()
@commands.has_role(int(staff))
async def revoke(ctx,member: discord.Member=None, channel: discord.TextChannel = None):

    rr = []

    with open("./data.json","r") as rr:
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

    await channel.set_permissions(member, send_messages=True,mention_everyone=False)
    await ctx.reply("successfully removed")
@bot.command()
@commands.has_role(int(staff))
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
        category_id = 1229474371588849745  # Category 1 ID
    else:
        category_id = 1229474415734034472  # Category 2 ID

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
    embed = discord.Embed(title=" SLOT RULES", color=0x8A2BE2)
    rules = """
1. We don't offer any refunds.
2. You can't sell or share your slot.
3. If you promote any server your slot will be revoked.
4. If you scam your slot will get revoked and you will get banned.
5. We can put your slot on hold at any time.
6. If you do not save the transcript of the ticket when you bought it if you or our server will get termed you will not get your slot back.
7. We recommend using MM, if the slot user denies MM, we have the right to revoke your slot.
8. You are not allowed to advertise your server invite or telegram invite.
9. Ping reset: every 24 hours.
10. Positions are never fixed.
11. If we see that your slot is inactive and is hardly used, we have the right to revoke your slot without a refund.
12. We can change the rules whenever we want without further notice.
13. Overpinging will lead to an instant slot revoke without any refund.
14. Inactivity for more than 2 days will result in the removal of the slot (you will be warned first).
"""
    embed.add_field(name="Rules", value=rules, inline=False)
    embed.set_image(url="https://media.discordapp.net/attachments/1229389946226475122/1229475051817140379/Rick-and-Morty-sunglasses.jpg?ex=662fd0de&is=661d5bde&hm=3f5f6515b54ba7d626e2a1eccfb7a89a2a7061fd6b96d203e6143c0a500138ab&=&format=webp&width=932&height=700")
    await a.send(embed=embed)

    if cx.lower() == "d":
        yoyo = (yoyo * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    elif cx.lower() == "m":
        yoyo = (yoyo * 30 * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    else:
        await ctx.reply("Use valid Format: ,create @user 1 m 4")

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


@bot.command()
async def ping(ctx, mention: str = None):
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

                    # Determine the mention based on user input
                    mention_str = ""
                    if mention == "@here":
                        mention_str = "@here"
                    elif mention == "@everyone":
                        mention_str = "@everyone"

                    # Send the appropriate mention
                    here_message = await ctx.send(mention_str)

                    # Send a message in an embed format
                    embed = discord.Embed(
                        title="Ping Detected",
                        description=f"{ctx.author.mention} pinged {mention_str} in their slot! You have {data[i]['ping_count']} ping{'s' if data[i]['ping_count'] != 1 else ''} left.\n\n**Use <#1220914365193257010>**",
                        color=0xFFFF00
                    )
                    await ctx.send(embed=embed)

                    # Wait for 5 seconds
                    await asyncio.sleep(5)

                    # Delete the mention message
                    await here_message.delete()
                    return

                else:
                    await ctx.send("You have used all your pings.")
                    return
            else:
                await ctx.send("You can only use the ping command in your slot channel.")
                return
    await ctx.send("You don't have any slots. Create a slot to get pings.")

@bot.command()
async def nuke(ctx):
    # Check if the user has the specified role
    role = ctx.guild.get_role(1229474713345069199)
    if role and role in ctx.author.roles:
        # Define a predicate to filter messages
        def is_not_bot_embed_message(message):
            return message.author != bot.user or not message.embeds

        # Delete all messages except bot embed messages
        await ctx.channel.purge(limit=None, check=is_not_bot_embed_message)

        # Build the embed
        embed = discord.Embed(
            title="Nuke",
            description=f"Successfully nuked {ctx.channel.mention}",
            color=discord.Color.red()
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1229481737348976740/1229496580319739924/latest.png?ex=662fe4eb&is=661d6feb&hm=01571fce0db9e7b8a0b6c9f8146197c8fed98aaa99991bf51da563f3cd16e31c&=&format=webp&quality=lossless&width=846&height=874")

        # Send the embed
        await ctx.send(embed=embed)
    else:
        await ctx.send("You do not have permission to use this command.")
bot.run("paste your bot token")
