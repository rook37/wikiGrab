#bot.py
import os
import discord
import setproctitle
from dotenv import load_dotenv
import wikiGrab
import asyncio
from discord.ext import commands

#TO DO:	see if there's a way to make commands case-insensitive.

load_dotenv()
setproctitle.setproctitle('dbot')
TOKEN = os.getenv('DISCORD_TOKEN')
channelID = int(os.getenv('CHANNEL_ID'))
bot = commands.Bot(command_prefix='!')

@bot.command(name='wiki help')
async def wikihelp(ctx):
	await ctx.message.channel.send(('Hi, {}!! \n The !wiki command searches various wikis and pulls the links for you! Currently enabled are Wikipedia, the Minecraft, Halo, and Warframe wikis!\nThe search command takes the form of !wiki WIKI QUERY, with WIKI being wiki/minecraft/halo/warframe and QUERY being your search term').format(ctx.message.author.mention))	
	
@bot.command()
async def exit(ctx):
		await bot.close()
	
@bot.command()
async def wiki(ctx):
		if(ctx.message.content == '!wiki help'): 
			await wikihelp(ctx)
		else:
			ctx.message.content = ctx.message.content.replace(ctx.message.content[:5], '', 1)
			tempM = ctx.message.content.split(" ")
			if (len(tempM)>3):
				tempM[2] = queryHandle(tempM)
				print(tempM)
			if(len(tempM)>2):
				await wikiGrab.recieve(bot,ctx.message.channel,tempM[1],tempM[2])
			else: await ctx.message.channel.send("Please specify a wiki in the form of \`!wiki WIKI QUERY\` - possible wikis are \'wiki\',\'mc\', \'halo\', and \'warframe\'")
	
@bot.command()
async def todo(ctx):
		f = open("todo.txt","a")
		ctx.message.content = ctx.message.content.replace(ctx.message.content[:5], '', 1)
		f.write("\n-"+ctx.message.content)
		f.close()


def is_wiki(m):
	return m.content.startswith('!wiki')

def is_me(m):
	return m.author == bot.user

def queryHandle(list):
	union = list[2]
	for x in list[3:]:
		union = union+' '+x
	return union.replace('"','')

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
	#channel = bot.get_channel(channelID)
	#await CHAN.send('`*hacker voice* i\'m in`')

@bot.event
async def on_reaction_add(reaction,user):
    reactList = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','➕']
    if(str(reaction) in reactList) and not (user == bot.user):
        await wikiGrab.reacted(reaction)

bot.run(TOKEN)