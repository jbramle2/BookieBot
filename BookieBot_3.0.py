# BookieBot.py
import os
import json
import random
import discord
import asyncio
import sys
from discord.ext import commands
from itertools import islice
from dotenv import load_dotenv

load_dotenv()

with open('token.txt', 'r') as t:
    TOKEN = t.read()

client = discord.Client(intents=discord.Intents.default())
# = discord.Client()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

global betting
global betteam
global betamount
global userliandri
global author
global user
global numredbets
global numbluebets
global redbettotal
global bluebettotal
global multiplier
global payout
global lessteam

betting = 0
betteam = 'not specified'
betamount = 0
userliandri = 0
numredbets = 0
numbluebets = 0
betwins = 0
betloses = 0
multiplier = 6
payout = 0
lessteam = None

with open('bank2.txt') as f:
    bank = json.load(f)

with open('bank.txt') as fd:
    legacybank = json.load(fd)

# bank = {'user': []}

winners = []
losers = []
currentbets = []


# returns a users current liandri
def findmoney(json_object, name):
    for entry in json_object['user']:
        if name == entry['name']:
            return entry['Liandri']

def findtotalwins(json_object, name):
    for entry in json_object['user']:
        if name == entry['name']:
            return entry['Total Wins']

def findtotallosses(json_object, name):
    for entry in json_object['user']:
        if name == entry['name']:
            return entry['Total Losses']

def findwinnings(json_object, name):
    for entry in json_object['user']:
        if name == entry['name']:
            return entry['Winnings']

def findlosses(json_object, name):
    for entry in json_object['user']:
        if name == entry['name']:
            return entry['Losses']

def findbankruptcies(json_object, name):
    for entry in json_object['user']:
        if name == entry['name']:
            return entry['Bankruptcies']

def findgiven(json_object, name):
    for entry in json_object['user']:
        if name == entry['name']:
            return entry['Liandri Given']

def findreceived(json_object, name):
    for entry in json_object['user']:
        if name == entry['name']:
            return entry['Liandri Received']


def findtargetmoney(json_object, name):
    for entry in json_object['user']:
        if name == entry['username']:
            return entry['Liandri']

        if name == entry['mentionname']:
            return entry['Liandri']

        namenoex = name.replace('!', '')

        if namenoex == entry['mentionname']:
            return entry['Liandri']

def findtargetname(json_object, name):
    for entry in json_object['user']:
        if name == entry['username']:
            return entry['username']

        if name == entry['mentionname']:
            return entry['username']

        namenoex = name.replace('!', '')

        if namenoex == entry['mentionname']:
            return entry['username']


def findcurrentbet(json_object, name):
    for entry in json_object['user']:
        if name == entry['name']:
            return entry['Current Bet']

def findsumredbets():
    currentredbets = []

    for x in bank['user']:
        if x['Current Bet'] > 0 and x['Current team'] == 'red':
            currentredbets.append(x['Current Bet'])
    print(currentredbets)
    if currentredbets:
        return sum(currentredbets)
    else:
        return 0

def findnumredbets():
    currentredbets = []

    for x in bank['user']:
        if x['Current Bet'] > 0 and x['Current team'] == 'red':
            currentredbets.append(x['Current Bet'])
    print(currentredbets)
    return len(currentredbets)

def findsumbluebets():
    currentbluebets = []

    for x in bank['user']:
        if x['Current Bet'] > 0 and x['Current team'] == 'blue':
            currentbluebets.append(x['Current Bet'])
    print(currentbluebets)
    if currentbluebets:
        return sum(currentbluebets)
    else:
        return 0

def findnumbluebets():
    currentbluebets = []

    for x in bank['user']:
        if x['Current Bet'] > 0 and x['Current team'] == 'blue':
            currentbluebets.append(x['Current Bet'])
    print(currentbluebets)
    return len(currentbluebets)

def findcurrentpayout():
    red_sum = findsumredbets()
    blue_sum = findsumbluebets()
    totalbets = red_sum + blue_sum

    if red_sum > blue_sum:
        if blue_sum > 0:
            current_payout = round(1 / (blue_sum / totalbets), 1)
            if current_payout > 1000000:
                current_payout = 1000000
        else:
            current_payout = 2.0
        return current_payout

    elif blue_sum > red_sum:
        if red_sum > 0:
            current_payout = round(1 / (red_sum / totalbets), 1)
            if current_payout > 1000000:
                current_payout = 1000000
        else:
            current_payout = 2.0
        return current_payout
    else:
        current_payout = 2.0
        return current_payout

def findmentionname(json_object, name):
    for entry in json_object['user']:
        if name == entry['username']:
            return entry['mentionname']

        if name == entry['mentionname']:
            return entry['mentionname']

        namenoex = name.replace('!', '')

        if namenoex == entry['mentionname']:
            return entry['mentionname']


def updatecurrentbet(json_object, name, money):
    for entry in json_object['user']:
        if name == entry['name']:
            entry['Current Bet'] = money
            with open('bank2.txt', 'w') as outfile:
                json.dump(bank, outfile)

def updatebetpercentage(json_object, name, money):
    for entry in json_object['user']:
        if name == entry['name']:

            liandri = entry['Liandri']
            liandri = int(liandri)

            entry['Current Bet'] = money
            money = int(money)

            currentbetpercentage = (money / liandri)
            entry['Current Bet Percentage'] = currentbetpercentage

            with open('bank2.txt', 'w') as outfile:
                json.dump(bank, outfile)

def updatecurrentteam(json_object, name, team):
    for entry in json_object['user']:
        if name == entry['name']:
            entry['Current team'] = team
            with open('bank2.txt', 'w') as outfile:
                json.dump(bank, outfile)


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


def sortbymoney():
    sorted_list = dict(bank)

    sorted_list['user'] = sorted(bank['user'], key=lambda x: x['Liandri'], reverse=True)

    # n_items = take(x, sorted_list.['user']())

    print(sorted_list)

    return sorted_list


def addtargetmoney(target, amount):
    print('target =' + target)

    for entry in bank['user']:

        print(entry['name'])
        if entry['username'] == target:
            currentmoney = entry['Liandri']
            print('HEY!')
            entry['Liandri'] = currentmoney + int(amount)

            currentreceived = entry['Liandri Received']
            entry['Liandri Received'] = currentreceived + int(amount)

    with open('bank2.txt', 'w') as outfile:
        json.dump(bank, outfile)


def subtracttargetmoney(target, amount):
    print('target =' + target)

    for entry in bank['user']:

        print(entry['name'])
        if entry['username'] == target:
            currentmoney = entry['Liandri']
            print('HEY!')
            entry['Liandri'] = currentmoney - int(amount)

            currentgiven = entry['Liandri Given']
            entry['Liandri Given'] = currentgiven + int(amount)

    with open('bank2.txt', 'w') as outfile:
        json.dump(bank, outfile)


def updatemoney(message, json_object, winteam):
    for entry in json_object['user']:

        global payout
        print("PAYOUT: " + str(payout))

        currentbet = entry['Current Bet']
        currentmoney = entry['Liandri']

        totalwins = entry['Total Wins']
        totallosses = entry['Total Losses']

        previouswinnings = entry['Winnings']
        previouslosses = entry['Losses']

        if winteam == 'none':
            entry['Current Bet'] = 0
            entry['Current team'] = 'none'

            with open('bank2.txt', 'w') as outfile:
                json.dump(bank, outfile)

        else:
            # check for tie. pays out half
            if winteam == entry['Current team'] and winteam == 'tie' and entry['Current Bet'] > 0:

                winners.append(
                    str(entry['mentionname']) + '(' + str((entry['Liandri']) + entry['Current Bet']) + '=' + str(
                        entry['Liandri']) + '+' + str(entry['Current Bet']) + ')')

                entry['Liandri'] = currentmoney + (currentbet / 2)

                entry['Current Bet'] = 0
                entry['Current team'] = 'none'

            else:

                #### MULTIPLIER PAYOUT

                if winteam == entry['Current team'] and entry['Current Bet'] > 0 and entry['Current team'] == lessteam:

                    withmultiplier = entry['Current Bet'] * payout
                    withmultiplier = round(withmultiplier)
                    entry['Liandri'] = round(entry['Liandri'])
                    entry['Current Bet'] = round(entry['Current Bet'])
                    payout = round(payout)

                    winners.append(
                        str(entry['mentionname']) + '(' + str((entry['Liandri']) + (entry['Current Bet']) * payout) + '=' + str(
                            entry['Liandri']) + '+' + str(withmultiplier) + ')')


                    #entry['Liandri'] = currentmoney + currentbet
                    entry['Liandri'] = currentmoney + (currentbet*payout)

                    entry['Current Bet'] = 0
                    entry['Current team'] = 'none'
                    entry['Current Bet Percentage'] = 0
                    entry['Total Wins'] = totalwins + 1
                    entry['Winnings'] = previouswinnings + currentbet

                    print(entry)

                    with open('bank2.txt', 'w') as outfile:
                        json.dump(bank, outfile)

                #####  NORMAL PAYOUT

                elif winteam == entry['Current team'] and entry['Current Bet'] > 0:

                    winners.append(
                        str(entry['mentionname']) + '(' + str((entry['Liandri']) + entry['Current Bet']) + '=' + str(
                            entry['Liandri']) + '+' + str(entry['Current Bet']) + ')')

                    #entry['Liandri'] = currentmoney + currentbet
                    entry['Liandri'] = currentmoney + currentbet

                    entry['Current Bet'] = 0
                    entry['Current team'] = 'none'
                    entry['Current Bet Percentage'] = 0
                    entry['Total Wins'] = totalwins + 1
                    entry['Winnings'] = previouswinnings + currentbet

                    print(entry)

                    with open('bank2.txt', 'w') as outfile:
                        json.dump(bank, outfile)

                elif entry['Current Bet'] > 0:

                    losers.append(
                        str(entry['mentionname']) + '(' + str((entry['Liandri']) - entry['Current Bet']) + '=' + str(
                            entry['Liandri']) + '-' + str(entry['Current Bet']) + ')')
                    entry['Liandri'] = currentmoney - currentbet
                    entry['Losses'] = previouslosses + currentbet
                    entry['Current Bet'] = 0
                    entry['Current team'] = 'none'
                    entry['Current Bet Percentage'] = 0
                    entry['Total Losses'] = totallosses + 1
                    entry['Losses'] = previouslosses + currentbet

                    print(entry)

                    with open('bank2.txt', 'w') as outfile:
                        json.dump(bank, outfile)

        print(entry)


def giveallx(amount):
    for entry in bank['user']:
        print(type(amount))
        currentmoney = entry['Liandri']

        amount = int(amount)

        entry['Liandri'] = currentmoney + amount

        with open('bank2.txt', 'w') as outfile:
            json.dump(bank, outfile)

def setallx(amount):
    for entry in bank['user']:
        print(type(amount))

        amount = int(amount)

        entry['Liandri'] = amount

        with open('bank2.txt', 'w') as outfile:
            json.dump(bank, outfile)

def givewelfare():
    for entry in bank['user']:

        currentbankruptcies = entry['Bankruptcies']

        if entry['Liandri'] == 0:
            entry['Liandri'] = 25
            entry['Bankruptcies'] = currentbankruptcies + 1

    with open('bank2.txt', 'w') as outfile:
        json.dump(bank, outfile)


# Gives LLiandri to user if they haven't already claimed it that week
# TODO - Make this actually weekly
#
#

@bot.command()
async def register(message):
    global bank
    author = message.author
    user = author.mention
    username = message.author.display_name

    people = json.dumps(bank)
    authorstring = str(author)

    if authorstring in people:
        response = 'You are already registered' + ' ' + user
        await message.channel.send(response)

    else:
        # adds money to bank
        bank['user'].append({
            'name': str(author),
            'username': str(username),
            'mentionname': user,
            'Liandri': 100,
            'Current Bet': 0,
            'Current team': 'none',
            'Total Wins': 0,
            'Total Losses': 0,
            'Winnings': 0,
            'Losses': 0,
            'Bankruptcies': 0,
            'Liandri Given': 0,
            'Liandri Received': 0,
            'Current Bet Percentage': 0
        })

        print(bank)
        with open('bank2.txt', 'w') as outfile:
            json.dump(bank, outfile)

        response = 'You have received 100 Liandri' + ' ' + user
        await message.channel.send(response)

#
# Checks Lirandri for self
#

@bot.command()
async def liandri(message):
    author = message.author
    user = author.mention

    userliandri = findmoney(bank, str(author))

    if userliandri:
        response = f'You currently have banked {userliandri:,} Liandri {user}'
        await message.channel.send(response)
    elif userliandri == 0:
        response = 'You have used all of your liandri for this week ' + user
        await message.channel.send(response)
    else:
        response = 'You have not registered your discord account $register' + user
        await message.channel.send(response)

@bot.command()
async def total(message):
    author = message.author
    user = author.mention

    userliandri = findmoney(bank, str(author))
    olduserliandri = findmoney(legacybank, str(author))

    print(str(olduserliandri))
    totaluserliandri = userliandri + olduserliandri

    if userliandri:
        response = f'You currently have banked {totaluserliandri:,} Liandri {user}'
        await message.channel.send(response)
    elif userliandri == 0:
        response = 'You have used all of your liandri for this week ' + user
        await message.channel.send(response)
    else:
        response = 'You have not registered your discord account $register' + user
        await message.channel.send(response)

@bot.command()
async def mystats(message):
    author = message.author
    user = author.mention
    name = message.author.display_name

    #######
    sortedarray = []
    sorted = sortbymoney()

    for x in sorted['user']:
        sortedarray.append(str(x['username']))

    sortedlist = sortedarray

    index = sortedlist.index(name)

    index = index + 1
    #######

    userliandri = findmoney(bank, str(author))

    usertotalwins = findtotalwins(bank, str(author))

    usertotallosses = findtotallosses(bank, str(author))

    if usertotalwins > 0:
        ratio = usertotalwins / (usertotallosses + usertotalwins)
        ratio = round(ratio, 2)
    else:
        ratio = "none"



    userwinnings = findwinnings(bank, str(author))

    userlosses = findlosses(bank, str(author))

    userbankruptcies = findbankruptcies(bank, str(author))

    usergiven = findgiven(bank, str(author))
    userreceived = findreceived(bank, str(author))

    response = user + ':' + " Rank: " + str(index) +  " | Liandri: " + str(userliandri) + " | Bets Won: " \
               + str(usertotalwins) + " | Bets Lost: " \
               + str(usertotallosses) + " | Ratio: " + str(ratio) + " | Total Winnings: " \
               + str(userwinnings) + " | Total Losses: " + str(userlosses) + " | Bankruptcies: " \
               + str(userbankruptcies) + " | Charity Given: " + str(usergiven) + " | Charity Received: " \
               + str(userreceived)

    await message.channel.send(response)

@bot.command()
async def currentbet(message):
    author = message.author
    user = author.mention

    userbet = findcurrentbet(bank, str(author))

    if userbet:
        response = 'Your current bet is ' + str(userbet) + ' Liandri ' + user
        await message.channel.send(response)
    elif userliandri == 0:
        response = 'You do not have a current bet ' + user
        await message.channel.send(response)
    else:
        response = 'You do not have a current bet ' + user
        await message.channel.send(response)

@bot.command()
async def bets(message):
    red_sum = findsumredbets()
    blue_sum = findsumbluebets()

    if red_sum > blue_sum:
        response = (("```"
                    "Red [2.0x]: (" + str(findnumredbets()) + ") " + str(findsumredbets()) +
                     "\nBlue[" + str(findcurrentpayout()) + "x]: (" + str(findnumbluebets()) + ") " + str(findsumbluebets())) + "```")
        await message.channel.send(response)

    elif blue_sum > red_sum:
        response = (("```"
                    "Red [" + str(findcurrentpayout()) + "x]: (" + str(findnumredbets()) + ") " + str(findsumredbets()) +
                     "\nBlue[2.0x]: (" + str(findnumbluebets()) + ") " + str(findsumbluebets())) + "```")
        await message.channel.send(response)
    else:
        response = (("```"
                    "Red [2.0x]: (" + str(findnumredbets()) + ") " + str(findsumredbets()) +
                     "\nBlue[2.0x]: (" + str(findnumbluebets()) + ") " + str(findsumbluebets())) + "```")
        await message.channel.send(response)
@bot.command()
@commands.has_role("Active Members")
async def give(message, amount, target):
    author = message.author
    user = author.mention

    userbet = findcurrentbet(bank, str(author))

    targetmention = str(findmentionname(bank, target))

    print(user)
    print(targetmention)

    if user == targetmention:
        response = "You cannot give liandri to yourself."
        await message.channel.send(response)

    else:
        if betting == 1:

            response = "You cannot give liandri while betting is open."
            await message.channel.send(response)

        elif userbet > 0:

            response = "You cannot give after you have placed a bet."
            await message.channel.send(response)

        else:

            if int(amount) < 0:

                response = "You cannot steal another user's liandri."
                await message.channel.send(response)

            else:

                userliandri = findmoney(bank, str(author))

                if userliandri < int(amount):

                    response = "You do not have enough liandri for this transaction."
                    await message.channel.send(response)

                elif (int(userliandri)) - (int(amount)) < 25:

                    response = "You cannot give liandri to bring your total below 25."
                    await message.channel.send(response)

                else:

                    targetliandri = findtargetmoney(bank, str(target))

                    convertedtarget = findtargetname(bank, str(target))

                    converteduser = findtargetname(bank, str(user))

                    addtargetmoney(convertedtarget, amount)

                    subtracttargetmoney(converteduser, amount)

                    print(userliandri)
                    print(targetliandri)

                    response = user + ' has given ' + str(targetmention) + ' ' + amount + ' liandri'
                    await message.channel.send(response)


#
# opens betting
#
#

@bot.command()
@commands.has_permissions(manage_messages=True)
async def openbets(message):
    global betting
    global multiplier
    global lessteam
    global payout
    global numredbets
    global numbluebets

    numredbets = 0
    numbluebets = 0

    lessteam = None

    ### Check for any current bets
    sumcurrentbets = 0
    for entry in bank['user']:
        currentbet = entry['Current Bet']
        sumcurrentbets += currentbet
        print("sum current bets: " + str(sumcurrentbets))

    if betting == 0 and sumcurrentbets == 0:

        betting = 1
        response = 'Bets are open!'
        await message.channel.send(response)


        await asyncio.sleep(random.randint(160, 180))
        #test below
        #await asyncio.sleep(8)

        if betting == 0:
            return

        response = 'Bets close soon, last call!!'
        await message.channel.send(response)
        #uncomment
        await asyncio.sleep(random.randint(20, 120))

        if betting == 0:
            return

        response = 'Bets are closed!'
        await message.channel.send(response)



        currentbets[:] = []
        currentredbets = []
        currentbluebets = []
        currentredpercents = []
        currentbluepercents = []

        for x in bank['user']:
            if x['Current Bet'] > 0 and x['Current team'] == 'red':

                currentredbets.append(str(x['mentionname']) + '(' + str(x['Current Bet']) + ')')
                currentredpercents.append(x['Current Bet Percentage'])

            elif x['Current Bet'] > 0 and x['Current team'] == 'blue':

                currentbluebets.append(str(x['mentionname']) + '(' + str(x['Current Bet']) + ')')
                currentbluepercents.append(x['Current Bet Percentage'])

        print('PERCENTS')
        print(currentredpercents)
        print(currentbluepercents)

        redbigbetstring = currentredbets

        betredstring = str(redbigbetstring).replace(',', ':heavy_dollar_sign:')
        betredstring = betredstring.replace('[', '')
        betredstring = betredstring.replace(']', '')
        betredstring = betredstring.replace("'", '')

        bluebigbetstring = currentbluebets

        betbluestring = str(bluebigbetstring).replace(',', ':heavy_dollar_sign:')
        betbluestring = betbluestring.replace('[', '')
        betbluestring = betbluestring.replace(']', '')
        betbluestring = betbluestring.replace("'", '')

        numredbets = len(currentredbets)

        numbluebets = len(currentbluebets)

        red_sum = findsumredbets()
        blue_sum = findsumbluebets()
        totalbets = red_sum + blue_sum

        if red_sum > blue_sum:
            if blue_sum > 0:
                payout = round(1 / (blue_sum / totalbets), 1)
                if payout > 1000000:
                    payout = 1000000
            else:
                payout = 2.0

            response = '**[' + str(numredbets) + ']**' + ' **[2.0x]**' + ' **Current red bets:** ' + betredstring
            await message.channel.send(response)

            response = '**[' + str(numbluebets) + ']**' + ' **[' + str(payout) + 'x]** **Current blue bets:** ' + betbluestring
            await message.channel.send(response)

            lessteam = "blue"

        elif blue_sum > red_sum:
            if red_sum > 0:
                payout = round(1 / (red_sum / totalbets), 1)
                if payout > 1000000:
                    payout = 1000000
            else:
                payout = 2.0


            response = '**[' + str(numredbets) + ']**' + ' **[' + str(payout) + 'x]** **Red bets:** ' + betredstring
            await message.channel.send(response)

            response = '**[' + str(numbluebets) + ']**' + ' **[2.0x]** **Blue bets:** ' + betbluestring
            await message.channel.send(response)

            lessteam = "red"

        else:
            payout = 2
            response = '**[' +str(numredbets) + ']**' + ' **[2.0x]**' + ' **Current red bets:** ' + betredstring
            await message.channel.send(response)

            response = '**[' + str(numbluebets) + ']**' + ' **[2.0x]** **Blue bets:** ' + betbluestring
            await message.channel.send(response)

    elif sumcurrentbets > 0:
        response = 'There is a current bet.'
        await message.channel.send(response)
    else:
        response = 'Bets are already open.'
        await message.channel.send(response)

    betting = 0


@bot.command()
@commands.has_permissions(manage_messages=True)
async def redbets(message):

    response = 'red bets: ' + "("+str(findnumredbets()) + ") " + str(findsumredbets())
    await message.channel.send(response)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def bluebets(message):

    response = 'blue bets: ' + "("+str(findnumbluebets()) + ") " + str(findsumbluebets())
    await message.channel.send(response)


# Closes betting and applies winnings or losses

@bot.command()
@commands.has_permissions(manage_messages=True)
async def closebets(message):
    global betting
    betting = 0
    response = 'Bets are closed!'
    await message.channel.send(response)


@bot.command()
async def bet(message, arg, team):
    global betting
    global numredbets
    global redbettotal
    global bluebettotal
    global numbluebets

    author = message.author
    user = author.mention

    untuple_str = str(arg)
    betamount = int(untuple_str)

    userliandri = findmoney(bank, str(author))

    betteam = team

    sumblue = findsumbluebets()
    sumred = findsumredbets()

    if userliandri is None:

        response = 'You have not registered $register.'
        await message.channel.send(response)

    else:
        if betteam == 'red' or team == 'blue' or team == 'tie':

            if betting == 1 and userliandri >= betamount:
                author = message.author
                user = author.mention
                updatecurrentbet(bank, str(author), betamount)
                updatecurrentteam(bank, str(author), betteam)
                updatebetpercentage(bank, str(author), betamount)
                print(bank)

                if sumblue > sumred:
                    response = (user + ' has placed a ' + str(betamount) + ' Liandri bet for ' + betteam +
                                " (" + str(findcurrentpayout()) + "x/2.0x)")
                    await message.channel.send(response)
                elif sumred > sumblue:
                    response = (user + ' has placed a ' + str(betamount) + ' Liandri bet for ' + betteam +
                                " (2.0x/" + str(findcurrentpayout()) + "x)")
                    await message.channel.send(response)
                else:
                    response = user + ' has placed a ' + str(betamount) + ' Liandri bet for ' + betteam
                    await message.channel.send(response)

            elif betting == 1 and userliandri < betamount:
                response = 'You do not have enough Liandri for this bet.'
                await message.channel.send(response)

            elif betting == 1 and userliandri == 0:
                response = user + "You are bankrupt until Sunday."
                await message.channel.send(response)

            else:
                response = 'Betting is not open.'
                await message.channel.send(response)
        else:
            response = betteam + ' is not a valid team'
            await message.channel.send(response)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def winner(message, winteam):
    global winners
    global losers

    if winteam == "red" or winteam == "blue" or winteam == "none":

        updatemoney(message, bank, winteam)

        winnerstring = str(winners).replace(',', ':small_red_triangle:')
        winnerstring = winnerstring.replace('[', '')
        winnerstring = winnerstring.replace(']', '')
        winnerstring = winnerstring.replace("'", '')

        response = '**Winners:** ' + winnerstring
        await message.channel.send(response)

        loserstring = str(losers).replace(',', ':small_red_triangle_down:')
        loserstring = loserstring.replace('[', '')
        loserstring = loserstring.replace(']', '')
        loserstring = loserstring.replace("'", '')

        response = '**Losers:** ' + loserstring
        await message.channel.send(response)

        currentbets[:] = []
        winners[:] = []
        losers[:] = []

        givewelfare()

    else:
        response = winteam + " is not a valid team"
        await message.channel.send(response)


####Bets was here

@bot.command()
async def rank(message):

    author = message.author
    user = author.mention
    name = message.author.display_name

    sortedarray = []
    sorted = sortbymoney()

    for x in sorted['user']:
        sortedarray.append(str(x['username']))

    sortedlist = sortedarray

    index = sortedlist.index(name)

    index = index + 1

    response = user + ": Rank = " + str(index)

    await message.channel.send(response)

@bot.command()
async def standings(message, totalnum=None):

    sorted = sortbymoney()
    response = '**Liandri Season Totals:** '

    for x in sorted['user']:
        response += (f'{x["username"]} ({x["Liandri"]:,}) :heavy_dollar_sign: ')

    print(response)

    if totalnum is None:
        num_To_Display = 10
    else:
        num_To_Display = int(totalnum)

    standings = response.split(":heavy_dollar_sign:")[:num_To_Display]

    standings = str(standings).replace(" ', '", ' :heavy_dollar_sign: ')
    standings = standings.replace('[', '')
    standings = standings.replace(']', '')
    standings = standings.replace("'", '')
    print(standings)

    await message.channel.send(str(standings))


@bot.command()
@commands.has_permissions(administrator=True)
async def giveall(message, totalnum):

    giveallx(totalnum)

    response = '+ ' + str(totalnum) + ' for all users'

    await message.channel.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def setall(message, totalnum):

    setallx(totalnum)

    response = 'All liandri reset to ' + str(totalnum) + ' for all users'

    await message.channel.send(response)

@bot.command()
async def welfare(message):

    givewelfare()

    response = 'This command is now automatically applied when you are bankrupt and is not necessary'

    await message.channel.send(response)


global channel_ut4
global channel_garden
id_user_pugbot = 141723331471605760
id_chan_ut4 = 192460940409700352
id_chan_garden = 493208320916717578
str_puglive = 'Teams have been selected:'


@client.event
async def on_ready():

    global channel_ut4
    channel_ut4 = client.get_channel(id_chan_ut4)
    global channel_garden
    channel_garden = client.get_channel(id_chan_garden)


@client.event
async def on_message(message):

    if message.content.startswith(
            str_puglive) and message.author.id == id_user_pugbot and message.channel == channel_garden:
        await channel_ut4.send(message.content)
        await channel_ut4.send("$openbets")


bot.run(TOKEN)