import discord

client = discord.Client()

fopen = open('BAXrouletteApp.txt', 'r')
scr = open('BAXrouletteScores.txt', 'r')
lines = scr.readlines()
scores = {}

# Populates already existing scores from servers
try:
	server = lines[0].strip()
	print("Loaded new server: "+server)
	scores[server] = {}
	for line in lines[1:len(lines)]:
		try:
			scru = line.strip().split(" ")
			scores[server][scru[0]] = int(scru[1])
			print("Loaded score from server: "+server+", UID: "+scru[0]+" "+scru[1])
		except IndexError:
			# New server
			server = line.strip()
			scores[server] = {}
			print("Loaded new server: "+server)
	
except IndexError:
	pass

scr.close()
lines = fopen.readlines()
fopen.close()

# Populates options from file
labels = []
options = {}
pfx = {}
readies = {}
active = {}
index = ""
for i in range(len(lines)):
    line = lines[i]
    if line.startswith('---'):
        labels.append(lines[i+1])
        options[lines[i+1]] = []
        index = lines[i+1]
    if line.startswith('*'):
        options[index].append(line[2:len(line)])

status = "Do !ba-help for help!"

cardsDict = {} # For cards for each player (ID)
usedCards = {} # Logs if cards are used or not for each player (ID)
stats = {} # Logs stats for each player

DM_ROLL = True # Should the user be DM'd their rolls?


# HELPER FUNCTIONS
def userReference(message):
    spl = message.content.split("<@")
    print(spl)
    st = 0
    if spl[1][st] == "!":
        st = 1
    mentioned = spl[1][st:spl[1].find(">")]
    print(mentioned)
    if mentioned == message.author.id:
        raise IOError()
    return mentioned
def userReferenceIgnoreSelf(message):
    spl = message.content.split("<@")
    print(spl)
    st = 0
    if spl[1][st] == "!":
        st = 1
    mentioned = spl[1][st:spl[1].find(">")]
    print(mentioned)
    return mentioned
def labelFromTarget(target):
    for item2 in labels:
        if item2.lower().startswith(target.lower()):
            break
    if not item2.lower().startswith(target.lower()):
        raise KeyError()
    return item2
def stratFromLabel(label, strat):
    for item in options[label]:
        if item.lower().startswith(strat.lower()):
            break
    if not item.lower().startswith(strat.lower()):
        raise KeyError()
    return item
def targetFromMessage(message):
    spl = message.content.split(" ")
    idea = spl[1]
    return targetFromInput(message, idea)
def targetFromInput(message, inp):
    for items in stats[message.author.id].keys():
        if items.lower().startswith(inp.lower()):
            break
    if not items.lower().startswith(inp.lower()):
        print(items.lower()+" "+inp.lower())
        raise KeyError()
    return items
def reset(message):
    global usedCards, cardsDict, status, active, stats
    # Resets all dictionaries
    msg = "<@"+message.author.id+">"
    usedCards = {}
    cardsDict = {}
    stats = {}
    readies[message.server.id] = {}
    msg += " reset all rolls! everyone can now roll again"
    status = "!ba-help Do !ba-roll and !ba-go when ready"
    active[message.server.id] = True
    return msg
# SETS UP EVERYTHING ON STARTUP
@client.event
async def on_ready():
    global prefixes, active, stats, status
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    prefixes = open('BAXroulettePrefixes.txt', 'r')
    lz = prefixes.readlines()
    for line in lz:
        [sid, val] = line.strip().split(" ")
        pfx[sid] = val
    prefixes.close()
    prefixes = open("BAXroulettePrefixes.txt", "a")
    for server in client.servers:
        print(server.id+" "+str(server))
        try:
            print("Loaded: "+pfx[server.id])
        except KeyError:
            pfx[server.id] = "!"
            prefixes.write(server.id+" "+pfx[server.id]+"\n")
        try:
            print("Loaded: "+str(scores[server.id]))
        except KeyError:
            scores[server.id] = {}
        readies[server.id] = {}
        active[server.id] = True
    print('------')
    print("READY!")
    prefixes.close()

@client.event
async def on_message(message):
    global stats
    if message.content.startswith(pfx[message.server.id]+'reset'):
        msg = reset(message)
        msgs = []
        for x in client.messages:
            msgs.append(x)
            # print(x.author.id)
            # print(x.content+"\n")
        for i in msgs:
        	# THE AUTHOR ID HERE REPRESENTS THE BOT'S ID!!! CHANGE THIS
            if "<@" in i.content and i.author.id == "333843575123083266" and not "players are ready" in i.content:
                await client.delete_message(i)
        await client.send_message(message.channel, msg)
    elif message.content.startswith(pfx[message.server.id]+'roll'):
        auth = "<@"+message.author.id+">"
        msg = "<@"+message.author.id+">"
        allowed = True
        if active[message.server.id]:
            try:
                if usedCards[message.author.id] != None:
                    allowed = False
            except KeyError:
                # User hasn't rolled yet!
                readies[message.server.id][message.author] = False
            if allowed:
                stats[message.author.id] = {}
                msg += " you rolled:\n"
                for i in labels:
                    choice = options[i][random.randint(0,len(options[i])-1)]
                    msg += i
                    msg += "- "+choice
                    if i.startswith("Start"):
                        stats[message.author.id]["Start"] = choice
                    if i.startswith("Objectives"):
                        stats[message.author.id]["Objective"] = choice
                    if i.startswith("Obstacles"):
                        stats[message.author.id]["Obstacle"] = choice
                    if i.startswith("Cards"):
                        print(message.author.id)
                        print(choice)
                        cardsDict[message.author.id] = choice
                        usedCards[message.author.id] = False
                print(stats[message.author.id])
            else:
                msg += " you have already rolled! wait for !ba-reset when the game is over!"
                msg += "\nYour Stats are:\n"
                for key,val in stats[message.author.id].items():
                    msg += ""+key
                    msg += "\n- "+val
        else:
            msg += " please wait until the current game is over!"
        if DM_ROLL:
            await client.send_message(message.channel, auth+" has rolled!")
            await client.send_message(message.author, msg)
        else:
            await client.send_message(message.channel, msg)
    elif message.content.startswith(pfx[message.server.id]+"stats"):
        msg = "<@"+message.author.id+">"
        msg += "\nYour Stats are:\n"
        for key,val in stats[message.author.id].items():
            msg += ""+key
            msg += "\n- "+val
        if DM_ROLL:
            await client.send_message(message.author, msg)
        else:
            await client.send_message(message.channel, msg)
    elif message.content.startswith(pfx[message.server.id]+"cards"):
        msg = "<@"+message.author.id+">"
        msg += "\nAll the cards are:\n"
        lbl = labelFromTarget("Card")
        for item in options[lbl]:
            msg += "- "+item
        await client.send_message(message.channel, msg)
    elif message.content.startswith(pfx[message.server.id]+'card'):
        msg = "<@"+message.author.id+">"
        try:
            card = cardsDict[message.author.id]
            msg += " your card is: "+cardsDict[message.author.id]
            msg += "\n"
            # Find a way to incoporate the use functionality here
            if card.startswith("Curse"):
                msg += "Forces another player to reroll the listed stat\n"
                msg += "Mention another user after using "+pfx[message.server.id]+"use when using this card\n"
                msg += "Example (Curse Objective): "+pfx[message.server.id]+"use @Sc2ad will force @Sc2ad's objective stat to be rerolled"
            elif card.startswith("Trade"):
                msg += "Forces another player to trade the listed stat\n"
                msg += "Mention another user after using "+pfx[message.server.id]+"use when using this card\n"
                msg += "Example (Trade Start): "+pfx[message.server.id]+"use @Sc2ad will trade @Sc2ad's start stat with your own"
            elif card.startswith("Swap"):
                msg += "Swaps another player's card\n"
                msg += "Mention another user after using "+pfx[message.server.id]+"use when using this card\n"
                msg += "Example: "+pfx[message.server.id]+"use @Sc2ad will swap your card for @Sc2ad's card, allowing you to use their card, but they cannot swap"
            elif card.startswith("Cherrypick"):
                msg += "Choose your listed stat\n"
                msg += "Mention a stat type after "+pfx[message.server.id]+"use when using this card\n"
                msg += "For a full list of stat types, do "+pfx[message.server.id]+"use\n"
                msg += "Example (Cherrypick Obstacle): "+pfx[message.server.id]+"use no t2 air will set your own obstacle to 'No T2 Air fabs'"
            elif card.startswith("Reroll"):
                msg += "Reroll your choice of a stat\n"
                msg += "Mention a stat to reroll after using "+pfx[message.server.id]+"use when using this card\n"
                msg += "For a full list of stats, do "+pfx[message.server.id]+"use\n"
                msg += "Example: "+pfx[message.server.id]+"use obj will reroll your own objective stat"
            elif card.startswith("Copy"):
                msg += "Copy your choice of a stat from a player\n"
                msg += "Mention a user AND your choice of a stat after using "+pfx[message.server.id]+"use when using this card\n"
                msg += "For a full list of stats, do "+pfx[message.server.id]+"use with a valid user mentioned directly after\n"
                msg += "Example: "+pfx[message.server.id]+"use @Sc2ad obj will copy @Sc2ad's objective stat"
            elif card.startswith("Block"):
                msg += "Blocks all other cards (only defends yourself)\n"
                msg += pfx[message.server.id]+"use does nothing"
        except KeyError:
            print("KEYERROR! "+message.author.id)
            msg += " you don't have any cards!"
        if DM_ROLL:
            await client.send_message(message.author, msg)
            await client.send_message(message.channel, "<@"+message.author.id+"> got information on their card")
        else:
            await client.send_message(message.channel, msg)
    elif message.content.startswith(pfx[message.server.id]+'use'):
        # MAYBE MAKE CARD USE HIDDEN AS WELL?
        msg = "<@"+message.author.id+">"
        allowed = True
        try:
            allowed = not usedCards[message.author.id]
            if not allowed:
                msg += " already used their card!"
            allowed2 = not readies[message.server.id][message.author]
            if not allowed2 and allowed:
                msg += " You are already ready!"
            allowed = allowed and allowed2
        except KeyError:
            print("KEYERROR! (TRIED TO USE CARD)"+message.author.id)
            allowed = False
            msg += " doesn't yet have a card!"
        if allowed:
            card = cardsDict[message.author.id]
            msg += " used their card: "+card
            print(msg)
            if "Start" in card:
                # Target start!
                target = "Start"
            if "Objective" in card:
                # Target objective!
                target = "Objective"
            if "Obstacle" in card:
                # Target obstacle!
                target = "Obstacle"
            # CURSE CARD
            if card.startswith("Curse"):
                # Curse cards!
                # Need to make sure the user references someone, who also has a start/objective/obstacle
                try:
                    mentioned = userReference(message)
                    msg += "\nYou cursed <@"+mentioned+">'s "+target+"!"
                    if not cardsDict[mentioned].startswith("Block"):
                        for item in labels:
                            if item.startswith(target):
                                break
                        choice = options[item][random.randint(0,len(options[item])-1)]
                        while choice == stats[mentioned][target]:
                            choice = options[item][random.randint(0,len(options[item])-1)]
                        stats[mentioned][target] = choice
                        msg += "\n<@"+mentioned+">'s new "+target+" is:"
                        msg += "\n- "+choice
                        usedCards[message.author.id] = True
                    else:
                        msg += "\nBut it was blocked!"
                except IndexError:
                    print("Error! specifcation, most likely")
                    msg += "\nYou must specify a user with this card!"
                except KeyError:
                    print("Error! KEYERROR: "+mentioned)
                    msg += "\nThat user has no card!"
                except IOError:
                    print("Error! Targetted self!")
                    msg += "\nYou cannot target yourself!"
            # TRADE CARD
            elif card.startswith("Trade"):
                try:
                    mentioned = userReference(message)
                    msg += "\nYou traded <@"+mentioned+">'s "+target+" with your "+target+"!"
                    if not cardsDict[mentioned].startswith("Block"):
                        for item in labels:
                            if item.startswith(target):
                                break
                        temp = stats[message.author.id][target]
                        stats[message.author.id][target] = stats[mentioned][target]
                        stats[mentioned][target] = temp
                        msg += "\n<@"+mentioned+">'s new "+target+" is:"
                        msg += "\n- "+temp
                        msg += "\nAnd your new "+target+" is:"
                        msg += "\n- "+stats[message.author.id][target]
                        usedCards[message.author.id] = True
                    else:
                        msg += "\nBut it was blocked!"
                except IndexError:
                    print("Error! specifcation, most likely")
                    msg += "\nYou must specify a user with this card!"
                except KeyError:
                    print("Error! KEYERROR: "+mentioned)
                    msg += "\nThat user has no card!"
                except IOError:
                    print("Error! Targetted self!")
                    msg += "\nYou cannot target yourself!"
            elif card.startswith("Swap"):
                try:
                    mentioned = userReference(message)
                    msg += "\nYou swapped <@"+mentioned+">'s "+cardsDict[mentioned]+" with your "+cardsDict[message.author.id]+"!"
                    if not cardsDict[mentioned].startswith("Block"):
                        temp = cardsDict[message.author.id]
                        cardsDict[message.author.id] = cardsDict[mentioned]
                        cardsDict[mentioned] = temp
                        msg += "\n<@"+mentioned+">'s new Card is:"
                        msg += "\n- "+temp
                        msg += "\nAnd your new Card is:"
                        msg += "\n- "+str(usedCards[message.author.id])
                        usedCards[message.author.id] = False
                        usedCards[mentioned] = True
                        # possible issue if they use a card, then it is stolen... is it still usable? doable?
                    else:
                        msg += "\nBut it was blocked!"
                except IndexError:
                    print("Error! specifcation, most likely")
                    msg += "\nYou must specify a user with this card!"
                except KeyError:
                    print("Error! KEYERROR: "+mentioned)
                    msg += "\nThat user has no card!"
                except IOError:
                    print("Error! Targetted self!")
                    msg += "\nYou cannot target yourself!"
            elif card.startswith("Cherrypick"):
                spl = message.content.split(" ")
                try:
                    idea = spl[1]
                    for q in range(2,len(spl)):
                        idea += " "+spl[q]
                    item2 = labelFromTarget(target)
                    item = stratFromLabel(item2, idea)
                    msg += "\nYou set your "+target+" to "+item
                    stats[message.author.id][target] = item
                    usedCards[message.author.id] = True
                except IndexError:
                    print("Error! Target not spaced appropriately!")
                    msg += "\nThis card requires a type after it!"
                    msg += "\nValid types are limited to:\n"
                    for item in labels:
                        if item.startswith(target):
                            break
                    for val in options[item]:
                        msg += "- "+val
                except KeyError:
                    print("Error! KEYERROR! User inputted: "+idea)
                    msg += "\nYou entered: '"+idea+"'"
                    msg += "\nPlease enter a valid type"
                    msg += "\nValid types are limited to:\n"
                    for item in labels:
                        if item.startswith(target):
                            break
                    for val in options[item]:
                        msg += "- "+val
            elif card.startswith("Reroll"):
                try:
                    items = targetFromMessage(message)
                    item = labelFromTarget(items)
                    choice = options[item][random.randint(0,len(options[item])-1)]
                    while choice == stats[message.author.id][items]:
                        choice = options[item][random.randint(0,len(options[item])-1)]
                    msg += "\nYou rerolled your "+items+" from "+stats[message.author.id][items].strip()+" to "+choice
                    stats[message.author.id][items] = choice
                    usedCards[message.author.id] = True
                except IndexError:
                    print("Error! Target not spaced appropriately!")
                    msg += "\nThis card requires a type after it!"
                    msg += "\nValid types are limited to:\n"
                    for item in labels:
                        if not "Card" in item:
                            msg += "- "+item
                except KeyError:
                    print("Error! KEYERROR! User inputted: "+idea)
                    msg += "\nYou entered: '"+idea+"'"
                    msg += "\nPlease enter a valid type"
                    msg += "\nValid types are limited to:\n"
                    for item in labels:
                        if not "Card" in item:
                            msg += "- "+item
            elif card.startswith("Copy"):
                # HOLY OP
                try:
                    mentioned = userReference(message)
                    spl = message.content.split(" ")
                    inp = spl[2]
                    target = targetFromInput(message, inp)
                    msg += "\nYou copied <@"+mentioned+">'s "+target+", replacing your "+target+" from "+stats[message.author.id][target]+" to "+stats[mentioned][target]
                    if not cardsDict[mentioned].startswith("Block"):
                        stats[message.author.id][target] = stats[mentioned][target]
                        usedCards[message.author.id] = True
                    else:
                        msg += "\nBut it was blocked!"
                except IndexError:
                    print("Error! Target not spaced appropriately! (USER + TRGT)")
                    msg += "\nThis card requires a user and a type after it!"
                    msg += "\nValid types are limited to:\n"
                    for item in labels:
                        if not "Card" in item:
                            msg += "- "+item
                except KeyError:
                    print("Error! KEYERROR! User inputted: "+inp+"\tOr user mentioned a user without a card")
                    msg += "\nYou entered: '"+inp+"'"
                    msg += "\nPlease enter a valid type and user (who has already rolled)"
                    msg += "\nValid types are limited to:\n"
                    for item in labels:
                        if not "Card" in item:
                            msg += "- "+item
                except IOError:
                    print("Error! Targetted self!")
                    msg += "\nYou cannot target yourself!"
            elif card.startswith("Block"):
                msg += "\nYou are immune to everything (this applies always while you have this card, no "+pfx[message.server.id]+"use required)"
            # Add implementation for each type of card!
        if DM_ROLL:
            await client.send_message(message.author, msg)
            await client.send_message(message.channel, "<@"+message.author.id+"> attempted to use their card")
        else:
            await client.send_message(message.channel, msg)
    elif message.content.startswith(pfx[message.server.id]+"ready"):
        try:
            print(readies[message.server.id][message.author])
        except KeyError:
            # No stats yet
            msg = "<@"+message.author.id+"> has not rolled yet!"
            await client.send_message(message.channel, msg)
            return
        msg = "<@"+message.author.id+"> is now ready!"
        msg += "\nWhen all players who have rolled are ready, the game will begin!"
        readies[message.server.id][message.author] = True
        for k in readies[message.server.id].keys():
            msg += "\n"
            if readies[message.server.id][k]:
                msg += ":white_check_mark: "
            else:
                msg += "  "
            msg += "<@"+k.id+">"
            
        if False in readies[message.server.id].values():
            await client.send_message(message.channel, msg)
            return
        await client.send_message(message.channel, msg)
        msg = "All players are ready! Beginning game!"
        msg += "\nPlayers:"
        for uid in stats.keys():
            usedCards[uid] = True
            msg += "\n<@"+uid+">"
        await client.send_message(message.channel, msg)
        status = "Currently playing a game..."
        active[message.server.id] = False
    elif message.content.startswith(pfx[message.server.id]+"win"):
        try:
            mentioned = userReferenceIgnoreSelf(message)
            msg = "<@"+mentioned+"> got their objective! They got one point!"
            msg += "\nTop 3 scores:"
            try:
                if scores[message.server.id][mentioned] == None:
                    scores[message.server.id][mentioned] = 0
            except KeyError:
                print("Created new score for: "+mentioned)
                scores[message.server.id][mentioned] = 0
            scores[message.server.id][mentioned] = scores[message.server.id][mentioned] + 1
            d = Counter(scores[message.server.id])
            for k,v in d.most_common(3):
                msg += "\n<@"+k+">: "+str(v)
        except IndexError:
            msg = "You must specify a user who won!"
        await client.send_message(message.channel, msg)
        scr = open("BAXrouletteScores.txt", "w")
        for k in scores.keys():
            scr.write(k+"\n")
            for k2 in scores[k].keys():
                scr.write(k2+" "+str(scores[k][k2])+"\n")
        scr.close()
    elif message.content.startswith(pfx[message.server.id]+"scores"):
        msg = "Top 5 scores:"
        d = Counter(scores[message.server.id])
        for k,v in d.most_common(5):
            msg += "\n<@"+k+">: "+str(v)
        await client.send_message(message.channel, msg)
    elif message.content.startswith(pfx[message.server.id]+"help"):
        # TO BE ADDED
        msg = "<@"+message.author.id+">"
        msg += "\nCommands:"
        msg += "\n"+pfx[message.server.id]+"roll: Randomly rolls your stats. If you have already rolled, it displays your stats"
        msg += "\n"+pfx[message.server.id]+"reset: Resets all stats and cards for everyone. Should be used after a game ends"
        msg += "\n"+pfx[message.server.id]+"card: Shows your card, along with help for your card"
        msg += "\n"+pfx[message.server.id]+"use: Uses your card. Try "+pfx[message.server.id]+"use for more details. If targetting another user, that user must have a card"
        msg += "\n"+pfx[message.server.id]+"stats: Shows your particular stats"
        msg += "\n"+pfx[message.server.id]+"ready: Indicates that you are ready to begin. You may no longer use your card after ready-ing. Once all players who have rolled are ready, the game begins"
        msg += "\n"+pfx[message.server.id]+"scores: Shows top scores"
        msg += "\n"+pfx[message.server.id]+"win: Gives a user a score point (usually after they complete their objective in game)"
        # msg += "\n"+pfx[message.server.id]+"go: Starts the game, summarizes all the stats, finalizes stats (no more cards can be used)"
        msg += "\n"+pfx[message.server.id]+"chelp: Shows a comprehensive help and use guide (See this if you have questions)"
        await client.send_message(message.channel, msg)
    await client.change_presence(game=discord.Game(name=status))
f = open("discord.key","r")
key = f.readline()
client.run(key)
f.close()