import praw,json,requests,collections,time
import constants,utils

NA_DICT={}
EU_DICT={}
def buildRedditTable(column_labels, grid):
    table = ""

    max_width = max([len(array) for array in grid])

    if len(column_labels) > max_width:
        max_width = len(column_labels)

    table += ("|" + (" {} |" * max_width) + "\n").format(*column_labels)
    table += "|" + (":-|" * max_width) + "\n"

    for array in grid:
        table += "|"
        for label in column_labels:
            if "&nbsp;" not in label:
                table += " {}"
            table += " |"

        table = table.format(*array)
        table += "\n"

    return table


def generateTable(playHistory,fd):
    playerDict={}
    table=[]
    playerArray=[]
    for game in playHistory:
        players = [key for key in fd['playerStats'][game] if "player" in key]
        for i,player_id in enumerate(players):
            player=fd['playerStats'][game][player_id]
            name = player['playerName']
            playerId =player['playerId']
            profile = "[%s](http://lolesports.com/node/%s)" % (name, playerId)
            for s in ['pentaKills','quadraKills','tripleKills','kills','deaths','assists','minionKills']:
##              Checks for bad game data, usually from unplayed games
                if player[s]=='':
                   print "FAILED for %s , %s"%(name,s)
                   player[s]=0
            kills = player['kills']
            deaths=player['deaths']
            assists=player['assists']
            cs = player['minionKills']
            pos= player['role']
            
            points=utils.calculatePlayerPoints(player)
            
            trips = player['tripleKills']
            quads = player['quadraKills']
            pents = player['pentaKills']
            teamNames=[]
            for key in fd['teamStats'][game].keys():
                if 'team' in key:
                    teamNames.append(fd['teamStats'][game][key]['teamName'])
            
            quads=quads-pents
            trips=trips-quads-pents
           
            bonus=0
            
            if player['kills'] >= 10 or player['assists'] >= 10:
                bonus = bonus+1
            if not name in playerArray:
                playerArray.append(name)
            if not name in playerDict:
                playerDict[name]={'kills':kills,'assists':assists,'deaths':deaths,'cs':cs,'pos':pos,'points':points,'profile':profile,'trips':trips,'quads':quads,'pents':pents,'bonus':bonus,'team':teamNames}
            else:
                playerDict[name]['kills']=playerDict[name]['kills']+kills
                playerDict[name]['deaths']=playerDict[name]['deaths']+deaths
                playerDict[name]['assists']=playerDict[name]['assists']+assists
                playerDict[name]['cs']=playerDict[name]['cs']+cs
                playerDict[name]['points']=playerDict[name]['points']+points
                playerDict[name]['trips']=playerDict[name]['trips']+trips
                playerDict[name]['quads']=playerDict[name]['quads']+quads
                playerDict[name]['pents']=playerDict[name]['pents']+pents
                playerDict[name]['bonus']=playerDict[name]['bonus']+bonus
                for t in teamNames:
                    if t in playerDict[name]['team']:
                        playerDict[name]['team']=t
                    
    i=0
    for player in playerArray:
        pD=playerDict[player]
        ppg=int(pD['points'])/len(playHistory)
       
        table.append([pD['profile'], "%s" % pD['points'],len(playHistory),ppg, pD['kills'], pD['deaths'], pD['assists'], pD['cs'], pD['trips'], pD['quads'], pD['pents'], pD['bonus']])
        print player+" : "+pD['team']

        if pD['role']=='Support' and i<len( playerDict.keys())-1:
            table.append(["|&nbsp;|"]*14)
        i=i+1
    return buildRedditTable(constants.PLAYER_TABLE_COLUMNS_TEAM, table)



def versusGames(teamArray,fd):
    teamA=teamArray[0]
    teamB=teamArray[1]

    playHistory=[]

    for game in fd['teamStats']:
        teams=[]
        for key in fd['teamStats'][game]:
            if 'team' in key:
                teams.append(key)
        teamNames = []
        for t in teams:
            teamNames.append(fd['teamStats'][game][t]['teamName'].lower())
            if teamA in teamNames and teamB in teamNames:
                playHistory.append(game)
    if len(playHistory)==0:
        return 0
    print playHistory
    return generateTable(playHistory,fd)



def allGames(names,fd):
    playerDict={}
    table=[]

    for game in fd['playerStats']:
        print fd['playerStats'][game].keys()
        print fd['teamStats'][game].keys()
        players = [key for key in fd['playerStats'][game] if "player" in key]
        for i,player_id in enumerate(players):
            player=fd['playerStats'][game][player_id]
            name = player['playerName']
                    
            if name.lower() in names:
                teamNames=[]
                for key in fd['teamStats'][game].keys():
                    if 'team' in key:
                        teamNames.append(fd['teamStats'][game][key]['teamName'])
 
                playerId =player['playerId']
                profile = "[%s](http://lolesports.com/node/%s)" % (name, playerId)
                
                
                for s in ['pentaKills','quadraKills','tripleKills','kills','deaths','assists','minionKills']:
##                    Checks for bad game data, usually from unplayed games
                    if player[s]=='':
                        print "FAILED for %s , %s"%(name,s)
                        player[s]=0
            
                kills = player['kills']
                deaths=player['deaths']
                assists=player['assists']
                cs = player['minionKills']
                pentas = player['pentaKills'] if player['pentaKills'] >0 else 0
                quads = int(player['quadraKills']) if player['quadraKills'] >0 else 0
                quads = quads-pentas             
                trips = int(player['tripleKills']) if player['tripleKills'] >0 else 0
                trips = trips-quads-pentas
                bonus = 1 if (player['kills'] >= 10 or player['assists'] >= 10) else 0
                points=utils.calculatePlayerPoints(player)

                
                
                if not name in playerDict:
##                    if this is the first game for the player add them to the playerDict
                    playerDict[name]={}
                    playerDict[name]['totals']={'kills':kills,'assists':assists,'deaths':deaths,'cs':cs,'points':points,'profile':profile,'trips':trips,'quads':quads,'pents':pentas,'bonus':bonus,'count':1}
                    gameNum='Game_1'
                else:
                    pT={}
                    pD=playerDict[name]['totals']
                    pT['kills']=int(pD['kills'])+int(kills)
                    pT['assists']=pD['assists']+assists
                    pT['deaths']=pD['deaths']+deaths
                    pT['cs']=pD['cs']+cs
                    pT['pents']=pD['pents']+pentas
                    pT['quads']=pD['quads']+quads
                    pT['trips']=pD['trips']+trips
                    pT['bonus']=pD['bonus']+bonus
                    pT['count']=pD['count']+1
                    pT['points']=pD['points']+points
                    gameNum='Game_'+str(pT['count'])
                    playerDict[name]['totals']={'kills':pT['kills'],'assists':pT['assists'],'deaths':pT['deaths'],'cs':pT['cs'],'points':pT['points'],'trips':pT['trips'],'quads':pT['quads'],'pents':pT['pents'],'bonus':pT['bonus'],'count':pT['count'],'profile':profile}
                playerDict[name][gameNum]={'kills':kills,'assists':assists,'deaths':deaths,'cs':cs,'points':points,'trips':trips,'quads':quads,'pents':pentas,'bonus':bonus,'teams':teamNames}
                    
    
    if len(playerDict.keys())==0:
        #return empty if no player found. 0 is used to know to ignore the tourney
        return (0,{})
    
    for player in playerDict.keys():
        
        pD=playerDict[player]['totals']
        c=int(pD['count'])
        table.append([pD['profile'], "%.2f" % pD['points'],pD['count'], pD['kills'], pD['deaths'], pD['assists'], pD['cs'], pD['trips'], pD['quads'], pD['pents'], pD['bonus']])
        pA=pD
        for key in pD:
            if not key =='profile' and not key=='pos' and not key=='count':
                pA[key]=format(float(pA[key])/c,'.2f')
        table.append(['*Average*', "%s" % pA['points'],'-', pA['kills'], pA['deaths'], pA['assists'], pA['cs'], pA['trips'], pA['quads'], pA['pents'], pA['bonus']])

    detailedTables={}
    if detailed:
        for player in playerDict.keys():
            detailedTables[player]=[]
            teamArray=[]
            keys=[]
            for key in playerDict[player]:
                if not key=='totals':
                    teamArray=teamArray+playerDict[player][key]['teams']
                    keys.append(key)
                
            playerTeam=utils.mostCommon(teamArray)
            teamArray=list(set(teamArray))
            teamArray.remove(playerTeam)
            
            detailedTables[player].append("|%s| GAMES| &nbsp;&nbsp;&nbsp;&nbsp; | K^^[+2] | D^^[-0.5] | A^^[+1.5] | CS^^[+0.01] | &nbsp;&nbsp;&nbsp;&nbsp; | Trips^^[+2] | Quads^^[+5] | Pents^^[+10] | K/A Bonus^^[+2] |&nbsp;&nbsp;&nbsp;&nbsp;| Points| PPG |"%player.upper())
            div='|:-|'
            for x in range(14):
                div+=':-:|'
            detailedTables[player].append(div)
            for team in teamArray:
                tKills=tDeaths=tAssists=tCS=tGames=tTrips=tQuads=tPentas=tBonus=tPoints=0
                for game in keys:
                    vsTeam=''
                    playerGame=playerDict[player][game]
                    for gameteam in playerGame['teams']:
                        if not gameteam == playerTeam:
                            vsTeam=gameteam
       
       
                    if vsTeam==team:
           
                        tKills+=playerGame['kills']
                        tDeaths+=playerGame['deaths']
                        tAssists+=playerGame['assists']
                        tCS+=playerGame['cs']
                        tTrips+=playerGame['trips']
                        tQuads+=playerGame['quads']
                        tPentas+=playerGame['pents']
                        tBonus+=playerGame['bonus']
                        tPoints+=playerGame['points']
                        tGames+=1
                
                detailedTables[player].append("|vs %s | %s  | | %s|%s|%s|%s| |%s|%s|%s|%s| |%s|%.2f|"%(team,tGames,tKills,tDeaths,tAssists,tCS,tTrips,tQuads,tPentas,tBonus,tPoints,tPoints/tGames))
   
    return (table,detailedTables)

    
def findTeamNames(task):
##    Searches the comment 'task' for team names
    text=task.body
    print task
    text=text.replace(constants.BOTNAME+" ",'').replace('\n','').lower()
    teamNames=text.split(' vs ')
    print teamNames
    teams=utils.cleanTeams(teamNames)
    return teams

def findSoloName(task, detailed=False):
    text=task.body
    print text
    #text=text[text.find(constants.BOTNAME+" "):]
    if detailed:
        text=text.replace(' detailed ',' ')
    text=text.replace(constants.BOTNAME+" ",'').replace('\n','').lower()
    text=text.strip(' ')
    names=text.split(' ')
    names=utils.cleanNames(names)
    return names


user_agent=("FLCS_pointbot at your service")

reddit=praw.Reddit(user_agent=user_agent)
username='FLCS_pointbot'
reddit.login(username,'xxxxxx')

FLCS=reddit.get_subreddit('FantasyLCS')

while True:
    pointReport=[]
    
    

    for comment in FLCS.get_comments(limit=500):
      if not str(comment).lower().find(constants.BOTNAME)==-1:
          pointReport.append(comment)
    removeComs=[]
    for comment in pointReport:
        #if username in str(comment.author):
        #    removeComs.append(comment)
        for reply in comment.replies:
            if username in str(reply.author):
                removeComs.append(comment)
    
    
    for rC in removeComs:
        try:
            pointReport.remove(rC)
        except:
            print "%s already removed"%rC

    if len(pointReport)>0:
        text=requests.get('http://na.lolesports.com/api/gameStatsFantasy.json?tournamentId=%s'%constants.REGION["NA"]).text
        NA_DICT=json.loads(text,object_pairs_hook=collections.OrderedDict)
        text=requests.get('http://na.lolesports.com/api/gameStatsFantasy.json?tournamentId=%s'%constants.REGION["EU"]).text
        EU_DICT=json.loads(text,object_pairs_hook=collections.OrderedDict)
    
    for comment in pointReport:
        detailed=False
        if not str(comment).find(' vs ')==-1:
            teams=findTeamNames(comment)
            
            if len(teams)==2:
                
                rTable=versusGames(teams,NA_DICT)
                if rTable==0:
                    rTable=versusGames(teams,EU_DICT)
                    if rTable==0:
                        post="FAILED TO FIND GAMES for %s vs %s"%(teams[0].title(),teams[1].title())
        
                if not rTable==0:
                    post=''#%s vs. %s\n'%(teams[0].upper(),teams[1].upper())
                    post += "    \n\n"
                    post+=rTable
                
                comment.reply(post)
                time.sleep(1)
        else:
            if not str(comment).find(' detailed ')==-1:
                detailed=True
            else:
                detailed=False
            
            
            namesFull=findSoloName(comment,detailed)
            print namesFull
                
            if detailed:
                maxLength=3
            length=int(len(namesFull)/maxLength)+1
            nameArray=[]
            name10array=[]
            for name in namesFull:
                if len(name10array)==maxLength :
                    nameArray.append(name10array)
                    name10array=[]
                name10array.append(name)
            if len(name10array)>0:
                nameArray.append(name10array)
            print nameArray
                
            
            for names in nameArray:
                naTable,naDT=allGames(names,NA_DICT)
                euTable,euDT=allGames(names,EU_DICT)
                allDT=dict(euDT.items()+naDT.items())
                
                table=[]
                if not (naTable==0 and euTable == 0):
                
                    post=""
                    if not naTable==0:
                        for item in naTable:
                            table.append(item)
                    if not euTable==0:
                        for item in euTable:
                            table.append(item)
            
                    for name in names:
                        post+="%s  "%name.upper()
                    post += "    \n\n"
                    post+=buildRedditTable(constants.PLAYER_TABLE_COLUMNS,table)
                
                    post+='\n'
                    
                    
                    
                    for key in allDT:
                        
                        for line in allDT[key]:
                            post+=line
                            post+='  \n'
                        post+='\n'

                    comment.reply(post)
                    time.sleep(1)
                else:
                    post='No Games found for '
                    for name in names:
                        post=post+name
                    comment.reply(post)
                    print post
                    time.sleep(1)
                

    time.sleep(300)
