import discord
from discord.ext import commands
import re

client = discord.Client()
installlink = "https://discordapp.com/api/oauth2/authorize?client_id=572138008971706400&permissions=289856&scope=bot"
TOKEN = "This is not the Token you are looking for..."


def run():
    client.run(TOKEN)

def isLink(link):
    link_regex = re.compile(
        r'^https?://(?:(ptb|canary)\.)?discordapp\.com/channels/'
        r'(?:([0-9]{15,21})|(@me))'
        r'/(?P<channel_id>[0-9]{15,21})/(?P<message_id>[0-9]{15,21})$'
        )
    pattern = r"https://discordapp\.com/channels/[0-9]+/[0-9]+/[0-9]+"
    if re.match(pattern, link):
        return True
    else:
        return False

def getcmds(content):
    cmds= []
    i = 0
    j = -1
    k = -1
    while i<len(content):
        if content[i] == "<":
            j = i
        elif content[i] == ">" and j != -1 and k == -1:
            k = i
            cmds.append(content[j+1:k])
            k = -1
        i += 1
    return cmds

def getOtC(message):
    for channel in message.guild.channels:
        if channel.name == "off-topic" or channel.name == "off topic":
            return channel
    for channel in message.guild.channels:
        if channel.name == "oof-topic" or channel.name == "oof topic":
            return channel
    return None

#async def getMessage(link):
#    link = link.split("/")
#    g = link[4]
#    c = link[5]
#    m = link[6]
#    print(link)
#    print(g)
#    print(c)
#    print(m)
#    guild = client.get_guild(g)
#    if not guild == None:
#        channel = guild.get_channel(c)
#        if not channel == None:
#            message = await channel.fetch_message(m)
#            if not message == None:
#                return message
#            else:
#                return "m"
#        else:
#            return "c"
#    else:
#        return "g"

##async def getMessage(link):
##    link = link.split("/")
##    s = link[4]
##    c = link[5]
##    m = link[6]
##    for server in client.guilds:
##        if server.id == s:
##            for channel in server.channels:
##                if channel.id == c:
##                    async for message in client.logs_from(channel,10000000000000000000000):
##                        if message.id == m:
##                            return message
##    return None

class FakeCtx:
    pass

async def getMessage(message, link):
    ctx = FakeCtx()
    ctx.channel = message.channel
    ctx.bot = client
    msg = await discord.ext.commands.MessageConverter().convert(ctx,link)
    return msg
##    link = link.split("/")
##    c = link[5]
##    m = link[6]
##    channel = client.get_channel(c)
##    if not(channel == None):
##        return await channel.fetch_message(m)
##    return None

async def cmd_help(message):
    perms = message.author.guild_permissions
    embed = discord.Embed(color = discord.Color.gold())
    if perms.manage_messages:
        embed.add_field(name="<pin> optional link", value = "Pins the message. or the message, the link is ponting at.", inline = False)
        embed.add_field(name="<unpin> link", value = "Unpinns the message with the given link")
    if perms.add_reactions:
        embed.add_field(name="<vote>", value = "Adds the thumbs up and the thumbsdown emoji for voting", inline = False)
    embed.add_field(name="<role name>", value = "Taggs the role (message will be deleted)", inline = False)
    embed.add_field(name="<member name>", value = "Taggs the person (message will be deleted)", inline = False)
    embed.add_field(name="<get> link", value = "Gets the message from the link (also works with embeds!!)", inline = False)
    #embed.add_field()
    await message.author.send(embed = embed)


async def cmd_pin(message):
    if not message.channel.permissions_for(message.author).manage_messages:
        return
    try:
        link = message.content.split(" ")[message.content.find("<pin>") + 1]
    except:
        link = "Not a link"
    print(link, isLink(link))
    if not isLink(link):
        await message.pin()
    else:
        msg = await getMessage(link)
        if msg == None:
            await message.channel.send("Unable to find the message.")
        else:
            await msg.pin()

async def cmd_unpin(message):
    link = message.content.split(" ")[message.content.find("<unpin>") + 1]
    if not isLink(link):
        await message.channel.send("Invalid link: The link is either no link or not a link to a message.")
        return
    try:
        msg = await getMessage(link)
    except:
        await message.channel.send("Unable to find message.")
    
    await msg.unpin()

async def cmd_vote(message):
    await message.add_reaction("\U0001f44d")
    await message.add_reaction("\U0001f44e")

async def cmd_get(message):
    link = message.content.split(" ")[message.content.find("<get>") + 1]
    if not isLink(link):
        await message.channel.send("Invalid link: The link is either no link or not a link to a message.")
        return

    try:
        msg = await getMessage(message, link)
    except Exception as error:
        print(error)
        await message.channel.send("Unable to find the message")
        return
    if msg == None:
        await message.channel.send("Unable to find the channel")
        return
    else:
        embed = discord.Embed(title = msg.content, color = discord.Color.green())
        embed.set_footer(text = message.author.name, icon_url = message.author.avatar_url)
        embed.set_author(name = msg.author.name, icon_url = msg.author.avatar_url)
        await message.channel.send(embed = embed)
        for emb in msg.embeds:
            await message.channel.send(embed = emb)

async def cmd_installLink(message):
    await message.channel.send("Here is a link which u can use to install me: {}".format(installlink))

async def go_to_off_topic(message):
    otc = getOtC(message)
    if otc == None:
        return
    msg = await message.channel.send("The content is off-topic. Please write this type of things in {}".format(otc.mention))
    await msg.add_reaction("\U0001F4A5")
    reaction, user = await client.wait_for("reaction_add", check = lambda reaction, user: reaction.emoji == "\U0001F4A5" and not user.bot)
    await msg.delete()

commands = {
    "help":cmd_help,
    "pin":cmd_pin,
    "unpin":cmd_unpin,
    "vote":cmd_vote,
    "get":cmd_get,
    "link":cmd_installLink, "install":cmd_installLink, "installlink":cmd_installLink,

}

@client.event
async def on_ready():
    print("Currently running on servers:")
    for g in client.guilds:
        print("name: {} - id: {}".format(g.name, g.id))
    await client.change_presence(activity = discord.Game("<help> for fuctions"))
    print("The Utilitybot is now ready!")


@client.event
async def on_message(message):
    await main(message)

@client.event
async def on_message_edit(oldmsg, newmsg):
    oldcmds = getcmds(oldmsg.content)
    newcmds = getcmds(newmsg.content)
    cmds = [cmd for cmd in newcmds if cmd not in oldcmds]
    for cmd in cmds:
        try:
            await commands[cmd](newmsg)
        except Exception as error:
            print(error)

async def main(message):
    content = message.content
    cmds = getcmds(content)
    for cmd in cmds:
        try:
            await commands[cmd](message)

        except Exception as error:
            print(error)
        
        for mem in message.channel.members:
            if mem.name.lower().startswith(cmd):
                print("yes")
                msg = await message.channel.send(mem.mention)
                await msg.delete()
                break

            try:

                if mem.nick.lower().startswith(cmd):
                    msg = await message.channel.send(mem.mention)
                    await msg.delete()
                    break
            except:
                pass

            
        for role in message.guild.roles:
            if role.name.lower() == cmd:
                msg = await message.channel.send(role.mention)
                await msg.delete()
                break

        
    if content.lower().__contains__("go to off-topic") or content.lower().__contains__("go to off topic"):
        await go_to_off_topic(message)



if __name__ == "__main__":
    run()
