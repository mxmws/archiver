import asyncio
import discord
from discord.ext import commands
from webserver import keep_alive
from replit import db

invite_link = 'https://discord.com/oauth2/authorize?client_id=808370491530149928&permissions=1073793088&scope=bot'
no_archive_emojis = ['🇳', '🇴', '🟦', '🇦', '🇷', '🇨', '🇭', '🇮', '🇻', '🇪']
archive_command = 'archive'
prefix = '%'
bot = commands.Bot(command_prefix=prefix)
client = discord.Client()

# replace the get and set functions if you don't use the repl.it database

def get_archive_channel(guild):
    channel_id = db[guild.id][1]
    return guild.get_channel(channel_id)

def set_archive_channel(guild, channel):
    db[guild.id] = [db[guild.id][0], channel.id]

async def get_archive_emoji(guild):
    emoji_id = db[guild.id][0]
    return await guild.fetch_emoji(emoji_id)

def set_archive_emoji(guild, emoji):
    try:
        db[guild.id] = [emoji.id, db[guild.id][1]]
    except:
        db[guild.id] = [emoji.id, 0]



# adds archive_this.png as emoji to guild
async def add_emoji(guild):
    with open("archive_this.png", "rb") as image:
        f = image.read()
        b = bytearray(f)
        archive_emoji = await guild.create_custom_emoji(name="archive_this", image=b)
        set_archive_emoji(guild, archive_emoji)

@bot.event
async def on_ready():
    print(bot.user.name + " is ready")
    await bot.change_presence(activity = discord.Activity(name=prefix + "help", type=3))

@bot.event
async def on_guild_join(guild):
    await add_emoji(guild) 

@bot.event
async def on_message(message):
    # request to set archive channel
    if message.content == prefix + archive_command:
        # check if user has permissions
        if not message.author.guild_permissions.manage_channels:
            embed = discord.Embed(
            description = "You need permission to manage channels in order to set this channel as the archive channel.",
            color=0x00ddcc
            )
            await message.channel.send(embed=embed)
        # set channel as archive channel
        else:
            set_archive_channel(message.guild, message.channel)
            embed = discord.Embed(
            description = "This channel is now set as the archive.",
            color=0x00ddcc
            )
            await message.channel.send(embed=embed)
    # request for help
    elif message.content == prefix + 'help':
        # get archive emoji
        try:
            archive_emoji = await get_archive_emoji(message.guild)
        # add archive emoji if it didn't exist
        except:
            await add_emoji(message.guild)
            embed = discord.Embed(
            description = "The archive emoji has been deleted. Try this command again. \nIf it still doesn't work kick me and reinvite me with all permissions necessary. [invite](" + invite_link + ")",
            color=0x00ddcc
            )
            await message.channel.send(embed=embed)
        # give helpful information to user
        else:
            embed = discord.Embed(
            description = "**How to use Archiver**",
            color=0x00ddcc
            )
            embed.add_field(name = "1.", value = "Use " + prefix + archive_command + " to set a channel as the archive channel.", inline = True)
            embed.add_field(name = "2.", value = "React with " +  str(archive_emoji) + " to archive a message.", inline = True)
            embed.add_field(name = "3.", value = "If you like Archiver [invite](" + invite_link + ") it to another server.", inline = True)
            await message.channel.send(embed=embed)
    # request for invite link
    elif message.content == prefix + 'invite':
        await add_emoji(message.guild)
        embed = discord.Embed(description = "[invite](" + invite_link + ")", color=0x00ddcc)
        await message.channel.send(embed=embed)

@bot.event
async def on_raw_reaction_add(payload):

    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    archive_emoji = await get_archive_emoji(guild)

    # if user reacted with archive emoji
    if (archive_emoji.id == payload.emoji.id):
        print('archive_emoji')        
        
        # return if message has been archived before
        for reaction in message.reactions:
            if reaction.me and reaction.emoji == archive_emoji:
                return

        archive_channel = get_archive_channel(guild)
        # add reactions and return if archive channel is not set
        if not archive_channel:
            for emoji in no_archive_emojis:
                await message.add_reaction(emoji)
            return
        
        # add reactions to give feedback and to remember this message has been archived
        await message.add_reaction(payload.emoji)        

        embed = discord.Embed(
            description = '[ʲᵘᵐᵖ ᵗᵒ ᵐᵉˢˢᵃᵍᵉ](' + message.jump_url + ')\n' + message.content,
            color=0x00ffee
        )
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        embed.set_footer(text='archived by ' + payload.member.name)


        image_formats = ['.jpg', '.jpeg', '.bmp', '.png']

        # add image if existing
        for at in message.attachments:
            is_image = False
            for format in image_formats:
                if format in at.filename:
                    is_image = True
                    embed.set_image(url=at.url)
            
            if not is_image:
                embed.description = embed.description + '\n*see attachment*'

        await archive_channel.send(embed=embed)

        # add embedds if existing
        for em in message.embeds:
            await archive_channel.send(embed=em)


        # add attachments if it's not an image
        for at in message.attachments:
            is_image = False
            for format in image_formats:
                if format in at.filename:
                    is_image = True
                    continue

            if not is_image:
                file = await at.to_file()
                await archive_channel.send(file=file)



# keep bot alive if you run it on repl.it
keep_alive()
bot.run(TOKEN)
