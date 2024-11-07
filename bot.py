import discord
from discord.ext import commands
import time
from secrets_parser import parse
from flask import Flask, request
import threading
from database import get, set, delete
import asyncio

app=Flask(__name__)

bot_Token = parse("variables.txt")["discord"]
GUILD_ID = parse("variables.txt")["guild_id"]


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print("Bot Started")

async def create_channels(level):
    guild = bot.get_guild(int(GUILD_ID))
    levels_category = None
    hints_category = None
    for x in guild.categories:
        if x.name == "levels":
            levels_category = x
        if x.name == "hints":
            hints_category = x
    level_channel=None
    channel0_name=f"leads-{level}"
    hint_channel=None
    channel1_name=f"hints-{level}"

    for x in levels_category.text_channels:
        if x.name==channel0_name:
            level_channel=x
    if level_channel==None:
        level_channel=await guild.create_text_channel(f"leads-{level}", category=levels_category)
    
    for x in levels_category.text_channels:
        if x.name==channel1_name:
            hint_channel=x
    if hint_channel==None:
        hint_channel=await guild.create_text_channel(f"hints-{level}", category=hints_category)
    set("level_channels", level, {"level":level_channel.id, "hint":hint_channel.id})

@app.get("/create_level")
async def create_channel():
    asyncio.run_coroutine_threadsafe(create_channels(request.args["level"]), bot.loop)
    return {"succes":"created channels"}

async def send_message(level, name, email, content):
    content=content.replace("`", "")
    channel=bot.get_channel(get("level_channels", level)["Value"]["level"])
    message=await channel.send(f"`{name} {email} : {content}`\n")
    set("discord_messages", str(message.id), {"email":email})

@app.get("/send_message")
async def send_message_api():
    asyncio.run_coroutine_threadsafe(send_message(request.args["level"], request.args["name"], request.args["email"], request.args["content"]), bot.loop)
    return {"success":"true"}

@bot.event
async def on_message(message:discord.Message):
    if message.author==bot:
        return
    await bot.process_commands(message)
    if message.channel.name=="announcements":
        set("announcements", str(message.id), {"content":message.content, "time":time.time()})
        return
    if message.channel.category.name=="hints":
        level=message.channel.name.split("-", 1)[1]
        type="cryptic"
        if "ctf" in message.channel.name:
            type="ctf"
        set("hints/"+level, str(message.id), {"time":time.time(), "content":message.content, "id":message.id, "author":"Exun Clan", "type":type})
        return
    if message.reference!=None:
        id=message.reference.message_id
        database_message=get("discord_messages", str(id))
        if database_message["Ok"]:
            type="cryptic"
            if "ctf" in message.channel.name:
                type="ctf"
            set("messages/"+database_message["Value"]["email"], str(message.id), {"author":"Exun Clan", "content":message.content, "time":time.time(), "id":str(message.id), "type":type})

@bot.event
async def on_message_delete(message:discord.Message):
    if message.channel.name=="announcements":
        delete("announcements", str(message.id))
        return
    if message.channel.category.name=="hints":
        level=message.channel.name.split("-", 1)[1]
        delete("hints/"+level, str(message.id))
    if message.reference!=None:
        id=message.reference.message_id
        database_message=get("discord_messages", str(id))
        if database_message["Ok"]:
            delete("messages/"+database_message["Value"]["email"], str(message.id))

@bot.command()
async def info(ctx):
    await ctx.send("""
Commands:
```
/info : help page
/backlink : to set a backlink which redirects to a url, example: /backlink abcd https://sudocrypt.com/assets/sudo.png
/logs : to get the logs of a player, example: /logs exun@dpsrkp.net
/ctf_leads : to toggle ctf leads
/cryptic_leads : to toggle cryptic
/disqualify : to toggle disqualification of a player, example: /disqualify {email}
```
""")

@bot.command()
async def backlink(ctx, backlink, url):
    set("backlinks", backlink, url)
    await ctx.send("backlink /"+backlink+" set to `"+url+"`")

@bot.command()
async def logs(ctx, email):
    log=get("logs", email)["Value"]
    if len(log)>1800:
        log=log[len(log)-1800:]
    await ctx.send("```"+log+"```")

@bot.command()
async def cryptic_leads(ctx):
    current_Leads=get("status", "leads-cryptic")["Value"]
    set("status", "leads-cryptic", not current_Leads)
    message=""
    if current_Leads:
        message="off"
    else:
        message="on"
    await ctx.send("Cryptic Leads have been turned "+message)

@bot.command()
async def ctf_leads(ctx):
    current_Leads=get("status", "leads-ctf")["Value"]
    set("status", "leads-ctf", not current_Leads)
    message=""
    if current_Leads:
        message="off"
    else:
        message="on"
    await ctx.send("CTF Leads have been turned "+message)

@bot.command()
async def disqualify(ctx, email):
    disqualified=get("disqualified", email)["Value"]
    set("disqualified", email, not disqualified)
    message=""
    if disqualified:
        message="allowed to play"
    else:
        message="disqualified"
    await ctx.send(email+" has been "+message)

@bot.event
async def on_message_edit(before, after):
    if before.channel.name=="announcements":
        announcement=get("announcements", str(before.id))
        if announcement["Ok"]:
            announcement["Value"]["content"]=after.content
            set("announcements", str(before.id), announcement["Value"])
        return
    if before.channel.category.name=="hints":
        level=before.channel.name.split("-", 1)[1]
        hint=get("hints/"+level, str(before.id))["Value"]
        set("hints/"+level, str(before.id), hint | {"content":after.content})
    if before.reference!=None:
        id=before.reference.message_id
        database_message=get("discord_messages", str(id))
        if database_message["Ok"]:
            message=get("messages/"+database_message["Value"]["email"], str(before.id))["Value"]
            set("messages/"+database_message["Value"]["email"], str(before.id), message | {"content":after.content})

threading.Thread(target=bot.run, args=(bot_Token, ), daemon=True).start()
app.run(host="0.0.0.0", port=8008)