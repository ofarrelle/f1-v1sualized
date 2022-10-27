import tinydb
import requests
import json

from tweeter import Tweeter
from visualizers.season import SeasonVisualizer
from visualizers.season_completion import SeasonCompletionVisualizer
from visualizers.laps import LapTimeVisualizer

DEBUG_MODE = False

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

visualizers = {
    'season': SeasonVisualizer(season, round),
    'laps': LapTimeVisualizer(season, round),
    'season_completion': SeasonCompletionVisualizer(season, round)
}
visualizer_order = ['season', 'laps', 'season_completion']

image_paths = [ 
    image_path 
    for visualizer_name in visualizer_order 
    for image_path in visualizers[visualizer_name].visualize() 
]
print(image_paths)

if DEBUG_MODE:
    exit()

tweeter = Tweeter()
post = {
    'text': visualizers['season_completion'].tweet_text(), 
    'image_paths': image_paths
}
print(tweeter.tweet(post))
    
exit()

