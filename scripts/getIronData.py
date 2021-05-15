import requests
import time
import pandas as pd
# golbal variables
matchesInfo = []
try:
    api_key = 'api_key=RGAPI-9fd53595-4208-440a-b192-ab0f4383df8e'
    url = 'https://br1.api.riotgames.com/lol/'
    challengerSummoners = f'{url}league/v4/entries/RANKED_SOLO_5x5/IRON/IV?{api_key}'
    response = requests.get(challengerSummoners)
    summoners = response.json()
    for summoner in summoners:
        try:
            summonerId = summoner['summonerId']
            accountBySummoner = f'{url}summoner/v4/summoners/{summonerId}?{api_key}'
            account = requests.get(accountBySummoner).json()
            accountId = account['accountId']
            beginIndex = 0
            while beginIndex < 10:
                print(accountId + " index: " + str(beginIndex) + " Size: " + str(len(matchesInfo)))
                try:
                    matchlistByAccount = f'{url}match/v4/matchlists/by-account/{accountId}?beginIndex={beginIndex}&endIndex=40&{api_key}'
                    beginIndex += 100
                    responseMatches = requests.get(matchlistByAccount)
                    matchesJson = responseMatches.json()['matches']
                    for match in matchesJson:
                        matchId = match['gameId']
                        readed = False
                        while not readed:
                            try:
                                matchByMatchId = f'{url}match/v4/matches/{matchId}?{api_key}'
                                matchResponse = requests.get(matchByMatchId).json()
                                matchId = matchResponse['gameId']
                                identities = matchResponse['participantIdentities']
                                duration = matchResponse['gameDuration']
                                participants = matchResponse['participants']
                                cont = 0
                                for participant in participants:
                                    stats = participant['stats']
                                    stats['gameId'] = matchId
                                    stats['gameDuration'] = duration
                                    stats['lane'] = participant['timeline']['lane']
                                    stats['participantId'] = participant['participantId']
                                    stats['teamId'] = participant['teamId']
                                    stats['championId'] = participant['championId']
                                    stats['spell1Id'] = participant['spell1Id']
                                    stats['spell2Id'] = participant['spell2Id']
                                    stats['participantId'] = identities[cont]['player']['accountId']
                                    matchesInfo.append(stats)
                                    cont += 1
                                readed = True
                                
                            except Exception as e:
                                print(e)
                                print("Reconectando")
                                readed = False
                                time.sleep(5)
                except Exception:
                    print("Reconectando")
                    time.sleep(30)
                    df = pd.DataFrame(matchesInfo)
                    df.to_csv('ironParticipants.csv', index = False, header=True)
        except Exception:
            print("Reconectando")
            time.sleep(30)
            df = pd.DataFrame(matchesInfo)
            df.to_csv('ironParticipants.csv', index = False, header=True)
except KeyboardInterrupt:
    print('interrompendo')
    df = pd.DataFrame(matchesInfo)
    df.to_csv('ironParticipants.csv', index = False, header=True)
    time.sleep(5)
    exit(0)

df = pd.DataFrame(matchesInfo)
df.to_csv('ironParticipants.csv', index = False, header=True)