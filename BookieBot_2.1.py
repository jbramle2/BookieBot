# BookieBot.py
import os
import json
import discord
import asyncio
import sys
from discord.ext import commands
from itertools import islice

from dotenv import load_dotenv

load_dotenv()

TOKEN = ''

client = discord.Client()
bot = commands.Bot('$')

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
        print("PAYOUT" + str(payout))

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


@bot.command()
async def weekly(message):

    author = message.author
    user = author.mention

    response = 'This command is outdated and you should receive 100 Liandri every Sunday.'

    await message.channel.send(response)

    response = 'Use $register to register for betting' + ' ' + user

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
        response = 'You currently have ' + str(userliandri) + ' Liandri ' + user
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
        response = 'You currently have banked ' + str(totaluserliandri) + ' Liandri ' + user
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

    if betting == 0:

        betting = 1
        response = 'Bets are open for the next 10 minutes!'
        await message.channel.send(response)


        await asyncio.sleep(480)
        #test below
        #await asyncio.sleep(8)

        if betting == 0:
            return

        response = 'Bets close in 2 minutes!!'
        await message.channel.send(response)
        #uncomment
        await asyncio.sleep(120)

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

        if len(currentredpercents) > 0:
            totalredpercentage = sum(currentredpercents) / len(currentredpercents)
            print(totalredpercentage)
        else:
            totalredpercentage = 1

        if len(currentbluepercents) > 0:
            totalbluepercentage = sum(currentbluepercents) / len(currentbluepercents)
            print(totalbluepercentage)
        else:
            totalbluepercentage = 1

        #calculates the payout based on bets against other team

        if numredbets > numbluebets:
            divide = numbluebets / numredbets
            prepayout = 1 - divide

            payout = prepayout * (multiplier)

            extrapayout = payout - 2
            payout = 2 + (extrapayout * totalbluepercentage)
            print('PAYOUT ' + str(payout))

            payout = round(payout, 1)

            lessteam = "blue"

        #was elif
        if numbluebets > numredbets:
            divide = numredbets / numbluebets
            prepayout = 1 - divide

            payout = prepayout * (multiplier)

            extrapayout = payout - 2
            payout = 2 + (extrapayout * totalredpercentage)
            print('PAYOUT ' + str(payout))

            payout = round(payout, 1)

            lessteam = "red"

        if lessteam == "red":

            response = '**[' +str(numredbets) + ']**' + ' **[' + str(payout) + 'x]** **Current red bets:** ' + betredstring
            await message.channel.send(response)

            response = '**[' + str(numbluebets) + ']**' + ' **[2.0x]** **Current blue bets:** ' + betbluestring
            await message.channel.send(response)

        elif lessteam == "blue":

            response = '**[' +str(numredbets) + ']**' + ' **[2.0x]**' + ' **Current red bets:** ' + betredstring
            await message.channel.send(response)

            response = '**[' + str(numbluebets) + ']**' + ' **[' + str(payout) + 'x]** **Current blue bets:** ' + betbluestring
            await message.channel.send(response)

        else:

            response = '**[' + str(numredbets) + ']** **Current red bets:** ' + betredstring
            await message.channel.send(response)

            response = '**[' + str(numbluebets) + ']** **Current blue bets:** ' + betbluestring
            await message.channel.send(response)


    else:
        response = 'Bets are already open.'
        await message.channel.send(response)

    betting = 0
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

    if userliandri is None:

        response = 'You have not registered $register.'
        await message.channel.send(response)

    else:
        if betteam == 'red' or team == 'blue' or team == 'tie':

            if betting == 1 and userliandri >= betamount:
                author = message.author
                user = author.mention
                response = user + ' has placed a ' + str(betamount) + ' Liandri bet for ' + betteam
                updatecurrentbet(bank, str(author), betamount)
                updatecurrentteam(bank, str(author), betteam)
                updatebetpercentage(bank, str(author), betamount)
                print(bank)
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

    sortedarray = []
    sorted = sortbymoney()

    for x in sorted['user']:
        sortedarray.append(str(x['username']) + '(' + str(x['Liandri']) + ')')

    redbigbetstring = sortedarray

    betredstring = str(redbigbetstring).replace(',', ':heavy_dollar_sign:')
    betredstring = betredstring.replace('[', '')
    betredstring = betredstring.replace(']', '')
    betredstring = betredstring.replace("'", '')

    print(totalnum)
    print(type(totalnum))

    if totalnum is None:
        poop = 10
    else:
        poop = int(totalnum)

    test = betredstring.split(":heavy_dollar_sign:")[:poop]

    test = str(test).replace(',', ':heavy_dollar_sign:')
    test = test.replace('[', '')
    test = test.replace(']', '')
    test = test.replace("'", '')

    print(betredstring)
    print(test)
    response = '**Liandri Season Totals:** ' + str(test)
    await message.channel.send(response)


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
