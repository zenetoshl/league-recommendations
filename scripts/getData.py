import requests
import time
import pandas as pd
# golbal variables
api_key = 'api_key=RGAPI-d0d1a606-4ae4-4818-88db-e32869b60c17'
url = 'https://br1.api.riotgames.com/lol/'
matchesInfo = []
challengerSummoners = f'{url}league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?{api_key}'
response = requests.get(challengerSummoners)
summoners = response.json()['entries']
for summoner in summoners:
    try:
        summonerId = summoner['summonerId']
        accountBySummoner = f'{url}summoner/v4/summoners/{summonerId}?{api_key}'
        account = requests.get(accountBySummoner).json()
        accountId = account['accountId']
        beginIndex = 0
        while beginIndex < 200:
            print(accountId + " index: " + str(beginIndex) + " Size: " + str(len(matchesInfo)))
            try:
                matchlistByAccount = f'{url}match/v4/matchlists/by-account/{accountId}?beginIndex={beginIndex}&{api_key}'
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
                            duration = matchResponse['gameDuration']
                            participants = matchResponse['participants']
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
                                matchesInfo.append(stats)
                            readed = True
                        except Exception:
                            print("Reconectando")
                            readed = False
                            time.sleep(5)
            except Exception:
                print("Reconectando")
                time.sleep(30)
                df = pd.DataFrame(matchesInfo)
                df.to_csv('participants.csv', index = False, header=True)
    except Exception:
        print("Reconectando")
        time.sleep(30)
        df = pd.DataFrame(matchesInfo)
        df.to_csv('participants.csv', index = False, header=True)

df = pd.DataFrame(matchesInfo)
df.to_csv('participants.csv', index = False, header=True)