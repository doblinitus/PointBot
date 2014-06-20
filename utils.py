import constants

def cleanNames(nameArray):
    #checks names against the global correction to fix any shorthand
    count=0
    for t in nameArray:
        if t in constants.PLAYER_CORRECTION_DICT.keys():
            print t
            nameArray[count]=constants.PLAYER_CORRECTION_DICT[t]
        count=count+1
    return nameArray

def cleanTeams(teamArray):
    #checks names against the global correction to fix any shorthand
    count=0
    for t in teamArray:
        if t in constants.CORRECTION_DICT.keys():
            teamArray[count]=constants.CORRECTION_DICT[t]
        count=count+1
    return teamArray

def calculatePlayerPoints(player_json):
    #Calculates Points 
    for s in ['pentaKills','quadraKills','tripleKills','kills','deaths','assists','minionKills']:
                if player_json[s]=='':
                    player_json[s]=0
    points = 0
    points += 2 * int(player_json['kills'])
    points += -0.5 * int(player_json['deaths'])
    points += 1.5 * int(player_json['assists'])

    points += 0.01 * int(player_json['minionKills'])

    points += 2 * int(player_json['tripleKills'])
    points += 3 * int(player_json['quadraKills'])
    points += 5 * int(player_json['pentaKills'])

    if int(player_json['assists']) >= 10 or int(player_json['kills']) >= 10:
        points += 2
    return points

def mostCommon(wordList):
    #Finds most common item in an array
    word_counter={}
    for word in wordList:
        if word in word_counter:
            word_counter[word]+=1
        else:
            word_counter[word]=1
    popular_words = sorted(word_counter, key = word_counter.get, reverse = True)
    return popular_words[0]


