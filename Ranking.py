from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import requests
import time
from sklearn.preprocessing import StandardScaler
import pandas as pd
import os.path

import json
from collections import Counter
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

api_key = 'api_key=XXXXXXXXXXXXXXXXXXXXXxxx'
url = 'https://br1.api.riotgames.com/lol/'


with open('model rank predict.pkl', 'rb') as f:
    model = pickle.load(f)
app = Flask(__name__, instance_relative_config=True)
CORS(app)
def CountList(e):
    return Counter(e)
def Uniquefy(e):
    return list(set(e))
def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1

def initArima():
    champ = pd.read_csv('participants.csv')
    champ = champ.loc[champ['gameDuration'] > 1500]
    champ['played'] = 1
    gpby = champ.groupby(['participantId'])['championId'].apply(list).reset_index(name='championsPlayed')
    gpby['count'] = gpby['championsPlayed'].apply(len)
    gpby = gpby.loc[gpby['count'] > 5]
    df_usable = gpby.explode('championsPlayed')
    df_usable['played'] = 1
    df_usable.drop('count',axis='columns', inplace=True)
    df_grouped = df_usable.groupby(['participantId', 'championsPlayed'])['played'].sum()
    cesta = df_grouped.unstack(fill_value=0)
    cesta.reset_index().set_index('participantId')
    cesta = cesta.applymap(encode_units)
    frequent_itemset = apriori(cesta, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemset,metric="confidence",min_threshold=0.01)
    return frequent_itemset, rules

frequent_itemset, rules = initArima()



def getAccountid(summoner):
    response = requests.get(f'{url}summoner/v4/summoners/by-name/{summoner}?{api_key}').json()
    print(response)
    return response["accountId"]

def dfTreatment(df):
    attr = ['totalHeal', 'totalMinionsKilled', 'neutralMinionsKilled', 'gameDuration', 'deaths', 'kills', 'visionScore', 'assists', 'goldEarned', 'inhibitorKills', 'totalDamageDealtToChampions', 'longestTimeSpentLiving', 'wardsKilled']
    df_treated = df.copy()
    df_treated['assists'] = df_treated['assists'].apply(int)
    df_treated = df_treated.replace(True, 1).replace(False, 0)
    df_treated.drop_duplicates(inplace=True)
    f = dict.fromkeys(df_treated[attr], 'mean')
    df_treated_group = df_treated.groupby(['participantId'])[attr].agg(f)
    df_treated_group['wardsKilled'] = df_treated_group['wardsKilled'].fillna(0)
    ss = StandardScaler().fit(df_treated_group[attr])
    return ss.transform(df_treated_group[attr])

def makeCSV(summoner):
    if os.path.isfile(f'{summoner}.csv'):
        return pd.read_csv(f'{summoner}.csv')
    matchesInfo = []
    accountId = getAccountid(summoner)
    beginIndex = 0
    matchlistByAccount = f'{url}match/v4/matchlists/by-account/{accountId}?beginIndex={beginIndex}&endIndex=20&{api_key}'
    beginIndex += 100
    responseMatches = requests.get(matchlistByAccount)
    matchesJson = responseMatches.json()['matches']
    for match in matchesJson:
        matchId = match['gameId']
        readed = False
        matchByMatchId = f'{url}match/v4/matches/{matchId}?{api_key}'
        matchResponse = requests.get(matchByMatchId).json()
        matchId = matchResponse['gameId']
        identities = matchResponse['participantIdentities']
        duration = matchResponse['gameDuration']
        participants = matchResponse['participants']
        cont = 0
        for participant in participants:
            if(accountId == identities[cont]['player']['accountId']):
                stats = participant['stats']
                stats['gameId'] = matchId
                stats['gameDuration'] = duration
                stats['lane'] = participant['timeline']['lane']
                stats['teamId'] = participant['teamId']
                stats['championId'] = participant['championId']
                stats['spell1Id'] = participant['spell1Id']
                stats['spell2Id'] = participant['spell2Id']
                stats['participantId'] = identities[cont]['player']['accountId']
                matchesInfo.append(stats)
            cont += 1
        readed = True 
    df = pd.DataFrame(matchesInfo)
    df.to_csv(f'{summoner}.csv', index = False, header=True)
    return df

def arimaRecommendation(played):
    recommendList = []
    for i in played:
        def compare (a):
            return a.__contains__(i)
        rules = association_rules(frequent_itemset,metric="confidence",min_threshold=0.01)
        rules_test = rules[rules['antecedents'].map(compare)]
        lists = rules_test.sort_values('support', ascending=False).head(5)['consequents'].tolist()
        mapItemset = map(list, lists)
        listItems = list(mapItemset)
        newList = []
        for l in listItems:
            newList.extend(l)
        recommendList.extend(newList)
    recommendList = [s for s in recommendList if s not in played]
    recommendCount = CountList(recommendList)
    recommendCount = dict(sorted(recommendCount.items(), key=lambda item: item[1], reverse=True))
    return list(recommendCount.keys())[0:5]

def makeRecommendation(summoner):
    df = makeCSV(summoner)
    playedCount = CountList(list(df['championId']))
    playedCount = dict(sorted(playedCount.items(), key=lambda item: item[1], reverse=True))
    listpl = list(playedCount.keys())[0:5]
    print(listpl)
    return arimaRecommendation(listpl)

@app.route('/hello')
def hello():
    return 'hello'

@app.route('/ranking', methods=['GET'])
def ranking():
    if 'summoner' in request.args:
        summoner = request.args['summoner']
    else:
        return "Error: No summoner field provided. Please specify an summoner name."

    return jsonify(model.predict(dfTreatment(makeCSV(summoner))).tolist())

@app.route('/recommendation', methods=['GET'])
def recommendation():
    if 'summoner' in request.args:
        summoner = request.args['summoner']
    else:
        return "Error: No summoner field provided. Please specify an summoner name."

    return jsonify(makeRecommendation(summoner))

app.run()
