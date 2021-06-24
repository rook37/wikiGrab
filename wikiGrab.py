#!/usr/bin/python3

"""
    opensearch.py
    MediaWiki API Demos
    Demo of `Opensearch` module: Search the wiki and obtain
	results in an OpenSearch (http://www.opensearch.org) format
    MIT License


    TODO-
    add - emoji before the 1 for 'page back' if possible
    add '+ to keep searching to the message' when results are >5
    
"""

import requests
import discord
#from itertools import islice

S = requests.Session()  

wikiPosts = []
wikiPostIds = []
bot = discord.Client()
emojiNo = {'1️⃣':1,'2️⃣':2,'3️⃣':3,'4️⃣':4,'5️⃣':5,'➕':6}
noEmoji = {0:'1️⃣',1:'2️⃣',2:'3️⃣',3:'4️⃣',4:'5️⃣',5:'➕'}

class sResult:
    def __init__(self,client,chan,data,msg,wf):
        # comes out in form: 'term',[page names],[page URLs]

        self.wf = wf
        self.names = data[1]
        self.compareList = self.names.copy()
        self.urls = data[3]    
        self.msg = msg
        self.pNo = 0
        self.message = None
        self.chan = chan
        self.type = 0
        self.currDict = {1:0,2:2,3:3,4:4,5:5}
        self.valid = 0
        self.keepSearching = 0
        for n in range(len(self.names)): 
            #currently, this creates a comparable list of lowercase titles while maintaining original capitalization for presentation
            #it also checks for valid titles (i.e. not subtitles) by checking how many do not have the / sign. 
            #when refactoring, it would make sense to use this to create a list of valid indices in order to avoid running the whole list at every print
            self.compareList[n] = self.names[n].lower()
            if self.wf==1 or "/" not in self.names[n]: 
                self.valid+=1
                print(self.names[n])       
        
    async def react(self, message):
        for x in range(0,min(self.valid,6)):
            await message.add_reaction(noEmoji[x])

    async def print(self):
        if len(self.names) == 0:
            await self.chan.send("Sorry, no results!")
        elif (self.msg.lower() in self.compareList) and (self.keepSearching == 0): #If we hit a direct query, print the answer!
            self.keepSearching = 1
            if(len(self.names)>1): #if that direct query has other potential results, they're made available with this check
                self.message = await self.chan.send("Hit the + emoji to continue searching with this query: "+self.msg+'\n'+self.urls[self.compareList.index(self.msg.lower())])
                await self.message.add_reaction(noEmoji[5])
            else:
                self.message = await self.chan.send(self.urls[self.compareList.index(self.msg.lower())])
        elif self.valid<=5: #If the list has multiple results but less than 5, print that selection
                c = 1
                string = "Please react with the # corresponding to the desired page:\n"
                for allItems in self.names:
                    if "/" in allItems and self.wf == 0:
                        continue
                    string = (string+str(c)+": "+allItems+'\n')
                    self.currDict[c] = self.urls[self.names.index(allItems)]
                    c += 1                    
                await self.sendIt(string)
        else: #If the list has >5 results, print the first 5 and track where we're at
            self.type = 1
            await self.longPrint(self.pNo)
             
    async def longPrint(self,c):
        self.valid=1
        string = "Please react with the # corresponding to the desired page"  # or select the + to keep searching:\n"
        #for allItems in islice(self.names, c, min(len(self.names),c+5)):
        for item in range(c,len(self.names)):            
            if "/" in self.names[item] and self.wf == 0:
                continue
            string = (string+str(self.valid)+": "+self.names[item]+'\n') 
            self.currDict[self.valid] = self.urls[item] 
            if(self.valid == 5): 
                self.valid = 6
                break
            if(item==len(self.names)-1): break #greeeeeeasy, need to think of a cleaner approach
            self.valid+=1           
        self.pNo = c+5
        await self.sendIt(string)

    async def sendIt(self,string): #takes built string and sends/edits message
        if(self.message is not None):
                await self.message.edit(content = string)           
        else:
            self.message = await self.chan.send(string)
            self.mID = self.message.id
            wikiPostIds.append(self.mID)
        await self.react(self.message)

    def cont(self):
        if(self.type==1):
            self.longPrint(self.pNo)
    
def cont(reaction, message):
    # if reaction is 1-5 print it
    for posts in wikiPosts:
        if posts.mID == message.id and posts.type == 1:
            posts.longprint(posts.pNo) 
            
async def recieve(client, channel, targ, msg):
    global bot
    bot = client
    targ = targ.lower()
    wf = 0
    #note:  turn if tree into dict at some point. maybe set default !wiki QUERY command to forward straight to wikipedia?
    wiki = 'init'
    if(targ == 'wiki'):
        wiki = 'en.wikipedia.org/w/'
    elif(targ == 'mc') or targ == 'minecraft':
        wiki = 'minecraft.gamepedia.com/'
    elif(targ == 'halo'):
        wiki = 'www.halopedia.org/'
    elif(targ == 'wf') or targ == 'warframe':
        wiki = 'warframe.fandom.com/'
        wf = 1
    if(wiki == 'init'):
        await channel.send("No such wiki!")
    else:
        url = "https://"+wiki+"api.php"
        data = grab(url, msg,wf)    
        res = sResult(client, channel, data, msg,wf)
        wikiPosts.append(res)
        await res.print()

def grab(URL, msg,wf):
    PARAMS = {
        "action": "opensearch",
        "namespace": "0",
        "search": msg,
        "limit": "100",
        "format": "json"
        }
    R = S.get(url=URL, params=PARAMS)
    data = R.json()
    if wf == 1:
        emptyL = []
        for items in data[1]:
            temp = items.split(" ")
            string = "https://warframe.fandom.com/wiki/"+temp[0]
            c=1
            while(c<len(temp)):
                string=string+"_"+temp[c]
                c+=1
            emptyL.append(string)
        data.append([])
        data.append(emptyL)
        #build a data[3] that is https://warframe.fandom.com/Thing_thing. Split on space and build?
   
    return data

@bot.event
async def reacted(reaction):
    found = None
    for posts in wikiPosts:
        if(reaction.message.content == posts.message.content):
            found = posts
    num = emojiNo[str(reaction)]
    if(found is not None):
        await reaction.message.clear_reactions()
        if(num<=5):
            await reaction.message.edit(content=found.currDict[num])
        else: 
            await found.print()

# async def on_reaction_add(reaction,user):
#     if reaction.message in wikiPosts.msg:
#         c = 0
#         while(c<len(wikiPosts)):
#             if reaction.message is not wikiPosts[c].msg:
#                 c+=1
#             else:
#                 break
#         print(c)
