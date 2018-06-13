#cakeDay Crawler

import os
import praw
import time
from datetime import datetime
import sys
import re
import concurrent.futures
import encodings.idna
import httplib2

username = "" ## REMOVED BEFORE UPLOADING TO GITHUB
password = "" ## REMOVED BEFORE UPLOADING TO GITHUB
r = praw.Reddit("") ## REMOVED BEFORE UPLOADING TO GITHUB
#r.login(username, password)

sitePrefix = "http://www.redditcakeday.com/index.php?username="
months=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
            'October', 'November', 'December']
dayLst = []
dayDic = {}

minAge = 14

def getUsers(sub="all",limit=1000):
    users=set()
    for u in r.get_comments(sub,limit=limit):
        users.add(str(u.author))
    return users


def getCakeday(user):
    resp,cont = httplib2.Http().request(sitePrefix+user)
    cont = str(cont)
    if user is None:
        print("\n"+user+" = None")
        return None
    if getUserDaysOld(user, cont) > minAge:
        openTag = cont.find('<span class="cakeday-title">')
        closTag = cont.find('</span>',openTag)
        res = cont[openTag+28:closTag]
        if len(res)>36:
            print("\nError w/user: "+user)
            return getCakeday(user)
        return res
    else:
        return None


def getUserDaysOld(user,pageCont):
    joinInfo = re.findall("[ADFJMNOSabceghilmnoprstuvy]+ \d\d, 20[01]\d",pageCont)
    try:
        joinDate = joinInfo[0]
        dateFormat = "%B %d, %Y"
        return (datetime.today()-datetime.strptime(joinDate,dateFormat)).days
    except IndexError:
        #print("<<"+user+">> \n"+pageCont+"\n\n"+str(re.findall("[ADFJMNOSabceghilmnoprstuvy]+ \d\d, 20[01]\d",pageCont))+"\n")
        #getUserDaysOld(user,pageCont)
        return -1

    
def isUserRecorded(user):
    try:
        f=open("Cakeday_Log_All-dayNum.tsv")
        lyns=f.readlines()
        f.close()
        for lyn in lyns:
            lst = lyn.split("\t") #Tab seperates username from bday
            if lst[0].lower()==user.lower():
                return True
        return False
    except FileNotFoundError:
        return False

    
def logInfo_ReturnNew(user,cakeday):
    newUsersParsed = 0
    if isUserRecorded(user) == False:
        newUsersParsed+=1
        outpt = user+"\t"+cakeday+"\n"
        f=open("Cakeday_Log_All-dayNum.tsv","a")
        f.write(outpt)
        f.close()
    return newUsersParsed


def getNumRecUsers():
    f = open("Cakeday_Log_All-dayNum.tsv")
    lyns = f.readlines()
    f.close()
    return len(lyns)


def initCakedayDic():
    for m in months:
        for d in range(32):
            if d<10:
                d="0"+str(d)
            else:
                d=str(d)
            dayLst.append(m+" "+d)
    for day in dayLst:
        dayDic[day] = 0


def getCakedayDic():
    f=open("Cakeday_Log_All-dayNum.tsv")
    lyns=f.readlines()
    f.close()
    for lyn in lyns:
        cd = lyn.split("\t")[1].replace("\n","")
        try:
            dayDic[cd]=dayDic[cd]+1
        except KeyError:
            print("\nerror with user "+lyn.split("\t")[0])
    return dayDic       


def search(sub="all",limit=1000):
    startTym = time.time()
    users=getUsers(sub, limit)
    users2parse = len(users)
    tenPercTot = round(users2parse/10)
    usersParsed = 0
    newUsersTot = 0
    print("Analyzing {} found users ...".format(len(users)))
    percFin = 0
    for user in users:
        percParsed = round((usersParsed / users2parse)*100,2)
        usersParsed += 1
        cakeday = getCakeday(user)
        if cakeday is None:
            continue
        newUsersTot += logInfo_ReturnNew(user,cakeday)
        if usersParsed % tenPercTot == 0 and percFin <= 100:
            percFin += 10
            print("{}%".format(percFin),end='..')
    elapsedTym = round(time.time()-startTym)
    m = elapsedTym // 60
    s = elapsedTym-(m*60)
    elapsedTym = "{}m {}s".format(m,s)
    print("\n-> {} new users! (Total = {})\nTime Elapsed = {}\n".format(newUsersTot,getNumRecUsers(),elapsedTym))


def getCurrentTime():
    tymTup = time.localtime()
    tod = "AM"
    h = tymTup[3]
    if h>12:
        h=12-h
    if h<0 or h==12:
        h*=-1
        tod = "PM"
    m = tymTup[4]
    s = tymTup[5]
    tym = "{}:{} {}".format(h,m,tod)
    return tym


def main():
    while getNumRecUsers() < 500000: #500,000
        try:
            subRed = r.get_random_subreddit(nsfw=False)
        except RedirectException:
            return main()
        print("\n[{}] - {}".format(subRed, getCurrentTime()))
        search(subRed, 1000)
        time.sleep(5)

main()
                                                        
##initCakedayDic()
##cd=getCakedayDic()
##for d in dayLst:
##    try:
##        print(cd[d])
##    except:
##        pass
