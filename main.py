import discord 
from discord.ext import commands , tasks
import datetime
import json
import os
from colorama import Fore
intents = discord.Intents().all()
bot = commands.Bot(command_prefix=',', intents = intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    print("\033[94m" + """

██████╗░██╗███████╗░█████╗░
██╔══██╗██║╚════██║██╔══██╗
██████╔╝██║░░███╔═╝███████║
██╔══██╗██║██╔══╝░░██╔══██║
██║░░██║██║███████╗██║░░██║
╚═╝░░╚═╝╚═╝╚══════╝╚═╝░░╚═╝
""" + "\033[0m" + "Made By @codewithriza")
    print(f"{bot.user.name} is Ready")
    await expire()
                            
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

                

                if member and channel:
                    print(member.id)
                    await channel.send(f"Slot expired")
                    role = discord.utils.get(guild.roles, id=rid)
                    print(role)
                    await member.remove_roles(role)
                    await channel.set_permissions(member, send_messages=False)
                    print(xd)
                    data.remove(xd)
                    with open("./data.json","w") as nice:
                        json.dump(data, nice,indent=4)



@bot.event
async def on_message(message):
    await bot.process_commands(message)
    category = discord.utils.get(message.guild.categories, id=int(cid))
    if category:
        if "@here" in message.content:
            try:
                with open("pingcount.json", "r") as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = []

            print(message.channel.id)
            print(data)     
            nice = False      
            if not data:
                dataz = {
                    "channelid": message.channel.id,
                    "time": datetime.datetime.now().timestamp(),
                    "count": 2
                }
                data.append(dataz)
                with open("pingcount.json", "w") as file:
                    json.dump(data, file, indent=4)
                    await message.channel.send("1/2")
                    return
            for c in data:
                print(c)
                if message.channel.id == c["channelid"]:
                    nice = True
                    print(c["time"])
                    print(datetime.datetime.now().timestamp())
                    nowt = datetime.datetime.now().timestamp()
                    slotdata = int(c["time"])
                    print(slotdata)
                    sl = datetime.datetime.fromtimestamp(slotdata)
                    slot = sl.strftime("%Y%m%d")
                    cx = datetime.datetime.now()
                    print(cx.timestamp())
                    nowtime = cx.strftime("%Y%m%d")
                    

                    if slot == nowtime:
                        xxx = c["count"]
                        if c["count"] >= 3:
                            channel = bot.get_channel(c["channelid"])
                            await channel.set_permissions(message.author, send_messages=False)
                            await message.channel.send("3/2 Slot Revoked <@&your staff role id>\n**Reason:** 3 here ping")
                            return
                        c["count"] = c["count"] + 1
                        await message.channel.send(f"{xxx}/{xxx}")
                        with open("pingcount.json", "w") as file:
                            json.dump(data, file, indent=4)
                        return
                    else:
                        c["time"] = datetime.datetime.now().timestamp()
                        c["count"] = 2
                        with open("pingcount.json", "w") as file:
                            json.dump(data, file, indent=4)
                        await message.channel.send("1/2")
            if not nice:
                datazx = {
                    "channelid": message.channel.id,
                    "time": datetime.datetime.now().timestamp(),
                    "count": 2
                }
                data.append(datazx)
                with open("pingcount.json", "w") as file:
                    json.dump(data, file, indent=4)
                    await message.channel.send("1/2")

            



   
@bot.command()
async def help(ctx):
    embed = discord.Embed(description="**,create** - Use To Create Slot\n**,add** - Use To Add User In Slot\n**,remove** - Use To Remove User In SLot\n**,renew** - Use To Renew Slot",color=0xFFFF00)
    embed.set_thumbnail(url=ctx.guild.icon)
    embed.set_author(name="Slot Bot Help Menu")
    await ctx.send(embed=embed,delete_after=30)
 
@bot.command()
@commands.has_role(int(staff))
async def add(ctx,member: discord.Member=None, channel: discord.TextChannel = None):

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

    await channel.set_permissions(member,view_channel=True, send_messages=True,mention_everyone=True)
    await ctx.reply("successfully Added")

@bot.command()
@commands.has_role(int(staff))
async def renew(ctx,member: discord.Member = None,channel: discord.TextChannel=None,yoyo: int = None,cx=None):
     

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
                
    print("ru")
    if (member == None):
        await ctx.reply("Member Not Found")
        return

    if (channel == None):
        await ctx.reply("Channel Not Found")
        return

    if (cx.lower() == "d"):
         yoyo = (yoyo * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    elif (cx.lower() == "m"):
         yoyo = (yoyo * 30 * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    else:
         await ctx.reply("Use valid Formate: ,add @user 1 m his Slot")

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
     
    embed = discord.Embed(description="""Your Slot Rules""",color=0xFFFF00)

    embed.set_author(name="Slot Rules")
    embed.set_thumbnail(url=f"{ctx.guild.icon}")

    await channel.send(embed=embed)
    embed = discord.Embed(description=f'**Slot Owner:** {member.mention}\n**End:** <t:{int(yoyo)}:R>',color=0xFFFF00)
    embed.set_footer(text=ctx.guild.name)
    embed.set_author(name=member)
    await channel.send(embed=embed)
    await ctx.reply(f"successfully renew Slot {channel.mention}")


@bot.command()
@commands.has_role(int(staff))
async def remove(ctx,member: discord.Member=None, channel: discord.TextChannel = None):

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
async def create(ctx,member: discord.Member=None,yoyo: int = None,cx=None,*,x=None):

    if member == None:
        await ctx.reply("User Not Found")
        return

    if yoyo == None:
        await ctx.reply("Use valid Formate: ,add @user 1 m his Slot")
        return
    
    if cx == None:
        await ctx.reply("Use valid Formate: ,add @user 1 m his Slot")
        return

    
    if (x == None):
        x = member.display_name

    overwrites = {
    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True,send_messages=False),
    member: discord.PermissionOverwrite(view_channel=True,send_messages=True,mention_everyone=True)
}
    
    

    category = discord.utils.get(ctx.guild.categories, id=int(cid))

    a = await ctx.guild.create_text_channel(x,category=category,overwrites=overwrites)

    await a.set_permissions(ctx.guild.default_role, send_messages=False)
    role = discord.utils.get(ctx.author.guild.roles, id=int(rid))
    await member.add_roles(role)

    embed = discord.Embed(description="""Your Slot Rules *""",color=0xFFFF00)

    embed.set_author(name="Slot Rules")
    embed.set_thumbnail(url=ctx.guild.icon)

    await a.send(embed=embed)

    if (cx.lower() == "d"):
        yoyo = (yoyo * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    elif (cx.lower() == "m"):
        yoyo = (yoyo * 30 * 24 * 60 * 60) + datetime.datetime.now().timestamp()
    else:
        await ctx.reply("Use valid Formate: ,add @user 1 m his Slot")
        
    embed = discord.Embed(description=f'**Slot Owner:** {member.mention}\n**End:** <t:{int(yoyo)}:R>',color=0xFFFF00)
    embed.set_footer(text=ctx.guild.name)
    embed.set_author(name=member)
    await a.send(embed=embed)
    await ctx.reply(f"successfully Create Slot {a.mention}")
    dataz = {
        "endtime": yoyo,
        "userid": member.id,
        "channelid": a.id
    },
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    data.append(dataz)
   
    with open("data.json", "w") as file:
        json.dump(data, file,indent=4)
  
bot.run("Your bot Token")
