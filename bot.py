import tinydb
import requests
import json
from season_visualizer import SeasonVisualizer
from tweeter import Tweeter

DEBUG_MODE = True

db = tinydb.TinyDB('races_seen.json')

last_race_results_url = "http://ergast.com/api/f1/current/last/results.json"
last_race_results_response = requests.get(last_race_results_url)
last_race_results = json.loads(last_race_results_response.text)
race_table = last_race_results['MRData']['RaceTable']['Races'][0]

season = race_table['season']
round = race_table['round']

Races = tinydb.Query()
matches = db.search(
    (Races.season == season) & 
    (Races.round == round) 
)

if len(matches) != 0:
    print('No new races')
    exit()

print('Today is race day!')
db.insert({ 'season':season, 'round':round })

visualizers = [
    SeasonVisualizer(season, round)
]
posts = [ visualizer.visualize() for visualizer in visualizers ]

if DEBUG_MODE:
    print(posts)
    exit()

tweeter = Tweeter()
for post in posts:
    print(tweeter.tweet(post))
    
exit()

