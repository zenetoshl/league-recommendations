import pandas as pd

champ = pd.read_json('champions.json')
champId = pd.DataFrame(columns=['id', 'Champion Name', 'Champion Category'])
for i in champ['data']:
    # print({'id':i['key'], 'Champion Name':i['id']})
    champId = champId.append({'id':i['key'], 'Champion Name':i['id'], 'Champion Category':i['tags']}, ignore_index=True)
champId.set_index('id', inplace=True)
champId.to_csv('championsId.csv')
