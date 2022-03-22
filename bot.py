import tinydb
import requests
import json

from tweeter import Tweeter
from visualizers.season import SeasonVisualizer
from visualizers.season_completion import SeasonCompletionVisualizer
from visualizers.laps import LapTimeVisualizer

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

if DEBUG_MODE==False and len(matches) != 0:
    print('No new races')
    exit()

print('New race found!')
if not DEBUG_MODE:
    db.insert({ 'season':season, 'round':round })

visualizers = [
    SeasonCompletionVisualizer(season, round),
    SeasonVisualizer(season, round),
    LapTimeVisualizer(season, round)
]
posts = [ visualizer.visualize() for visualizer in visualizers ]
print(posts)

if DEBUG_MODE:
    exit()

tweeter = Tweeter()
for post in posts:
    print(tweeter.tweet(post))
    
exit()

