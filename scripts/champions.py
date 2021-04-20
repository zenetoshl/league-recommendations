import pandas as pd
import requests
import json

champ_json = requests.get('http://ddragon.leagueoflegends.com/cdn/11.8.1/data/en_US/champion.json')
champ = pd.read_json(path_or_buf=json.dumps(champ_json.json()))
champId = pd.DataFrame(columns=['id', 'Champion Name', 'Champion Category'])
for i in champ['data']:
    # print({'id':i['key'], 'Champion Name':i['id']})
    champId = champId.append({'id':i['key'], 'Champion Name':i['id'], 'Champion Category':i['tags']}, ignore_index=True)
champId.set_index('id', inplace=True)
champId.to_csv('championsId.csv')
