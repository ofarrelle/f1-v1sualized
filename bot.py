import tinydb
import requests
import json

from ui import UI
from tweeter import Tweeter
from visualizers.season import SeasonVisualizer
from visualizers.season_completion import SeasonCompletionVisualizer
from visualizers.laps import LapTimeVisualizer


def run_app(DEBUG_MODE, URL_SEASON, URL_RACE, TWEET_TEXT_REPLACEMENT):
    searched_race_results_url = "http://ergast.com/api/f1/{season}/{race}/results.json".format(season=URL_SEASON, race=URL_RACE)
    searched_race_results_response = requests.get(searched_race_results_url)
    searched_race_results = json.loads(searched_race_results_response.text)
    race_table = searched_race_results['MRData']['RaceTable']['Races'][0]

    season = race_table['season']
    round = race_table['round']
    gp_name = race_table['raceName']

    db = tinydb.TinyDB('races_seen.json')
    Races = tinydb.Query()
    matches = db.search(
        (Races.season == season) & 
        (Races.round == round) 
    )

    if DEBUG_MODE == False and len(matches) != 0:
        print('No new races')
        return

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
        return

    tweeter = Tweeter()
    tweet_text = TWEET_TEXT_REPLACEMENT if len(TWEET_TEXT_REPLACEMENT) > 0 else visualizers['season_completion'].tweet_text()
    post = {
        'text': tweet_text,
        'image_paths': image_paths
    }
    print(tweeter.tweet(post, season, gp_name)) 
    return

if __name__ == "__main__":
    ui = UI()
    ui.launch_ui()

    DEBUG_MODE = ui.debug_mode
    URL_SEASON = ui.season.get()
    URL_RACE = ui.race.get()
    TWEET_TEXT_REPLACEMENT = ui.tweet_text_replacement

    run_app(DEBUG_MODE, URL_SEASON, URL_RACE, TWEET_TEXT_REPLACEMENT)
