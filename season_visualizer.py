import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from mpl_prettify import *
import time

from visualizer import Visualizer

class SeasonVisualizer(Visualizer):
    points_table = None

    def __init__(self, season, round):
        super().__init__(season, round)
        self.points_table = self.set_season_points_table()
    
    def visualize(self):
        text = self.tweet_text()
        image_paths = [
            self.tweet_image_wdc_standings()
        ]
        return {
            'text':text, 
            'image_paths':image_paths
        }


    def tweet_text(self):
        season_url = "http://ergast.com/api/f1/{season}.json".format(season=self.season)
        season_response = requests.get(season_url)
        season_dict = json.loads(season_response.text)
        num_races = int(season_dict['MRData']['total'])

        tweet_text = f"Following today's {self.name}, we are {float(self.round) / num_races:.0%} of the way though the {self.season} season."
        if num_races - self.round != 0:
            tweet_text += f"\nThere are {num_races - self.round} races remaining."

        return tweet_text


    def tweet_image_wdc_standings(self):
        current_points = self.points_table[self.points_table['round'] == self.round][['name','points']].copy()

        fig, ax = plt.subplots(figsize=(12,4))
        plt.xticks(rotation=45)
               
        diff_points = None
        diff_points_container = None
        if self.round > 1:
            previous_points = self.points_table[self.points_table['round'] == self.round-1][['name','points']].copy()
            diff_points = current_points.merge(previous_points, on='name', how='left')
            diff_points = diff_points.rename(columns={'points_x':'current', 'points_y':'previous'})
            diff_points = diff_points.fillna(0)
            diff_points['diff'] = diff_points.current - diff_points.previous
            diff_points = diff_points.sort_values('current', ascending=False)

            diff_points_container = ax.bar(
                diff_points.name, diff_points['diff'], 
                bottom=diff_points.previous, 
                label=f'Points Obtained from Race', color=PASTEL_PRISMARINE
            )
            previous_points_container = ax.bar(
                diff_points.name, diff_points.previous, 
                label=f'Points Prior to Race', color=PASTEL_AQUA
            )
            ax.bar_label(
                diff_points_container, 
                diff_points.current, 
                padding=0, size=10.0
            )
            ax.legend(frameon=False)
        else:
            current_points_container = ax.bar(
                current_points.name, current_points.points, 
                label=f'Before {self.name}', color=PASTEL_AQUA
            )
            ax.bar_label(
                current_points_container, 
                current_points.points, 
                padding=0, size=10.0
            )

        ax.set_yticks([])
        ax.set_title(f"Driver's Championship Points after {self.name}")

        fname = f"tweet_media/{self.season}_{self.round}_wdc_standings.png"
        plt.savefig(fname, transparent=False, bbox_inches='tight')
        return fname


    def set_season_points_table(self):
        standings = []
        for i in range(self.round):
            time.sleep(0.5)
            round = i+1
            standings_url = "http://ergast.com/api/f1/2021/{round}/driverStandings.json".format(round=round)
            standings_response = requests.get(standings_url)
            standings_dict = json.loads(standings_response.text)
            standings_results = standings_dict['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

            for i in range(int(standings_dict['MRData']['total'])):
                name = standings_results[i]['Driver']['familyName']
                points = standings_results[i]['points']
                standings.append({
                    'name':name,
                    'round':round,
                    'points':int(float(points))
                })
        
        return pd.DataFrame(standings)