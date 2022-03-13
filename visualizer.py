from abc import abstractmethod
import requests
import json
from datetime import datetime

class Visualizer:
    season = None
    round = None
    name = None
    date = None
    track = None


    def __init__(self, season, round):
        self.season = int(season)
        self.round = int(round)
        self.fill_race_info()


    def fill_race_info(self):
        race_url = "http://ergast.com/api/f1/{season}/{round}.json".format(season=self.season, round=self.round)
        race_response = requests.get(race_url)
        race_dict = json.loads(race_response.text)
        race_table = race_dict['MRData']['RaceTable']['Races'][0]

        self.name = race_table['raceName']
        self.date = datetime.strptime(race_table['date'], "%Y-%m-%d")
        self.track = race_table['Circuit']['circuitName']

    @abstractmethod
    def visualize(self):
        pass