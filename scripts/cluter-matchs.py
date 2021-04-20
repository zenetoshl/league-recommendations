import pandas as pd
import numpy as np
import requests
import json
from sklearn.cluster import KMeans

# Leitura do dataset
champ = pd.read_csv('participants.csv')
champ = champ.loc[champ['gameDuration'] > 1200]

# Separacao dos atributos para treinamento e clusterizacao
atributos = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6', 'magicDamageDealtToChampions', 'physicalDamageDealtToChampions', 'trueDamageDealtToChampions', 'totalHeal', 'totalUnitsHealed', 'totalDamageTaken', 'magicalDamageTaken', 'physicalDamageTaken', 'championId', 'totalMinionsKilled', 'neutralMinionsKilled', 'totalTimeCrowdControlDealt']
km = KMeans()
km.fit(champ[atributos])

# Agrupamento dos dados por label e champion id
champ['label'] = km.labels_
champ['freq'] = 1
joao = champ.groupby(['label', 'championId']).sum()

# Calculo da frequencia de escolha do champion e vitorias
joao['win'] = joao['win'] / joao['freq']
maria = joao.sort_values('label')[['win', 'freq']]
print(maria)