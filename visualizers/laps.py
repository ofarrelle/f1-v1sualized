import requests
import json
import pandas as pd
import time
import matplotlib.pyplot as plt
from mpl_prettify import *

from visualizers.visualizer import Visualizer

class LapTimeVisualizer(Visualizer):
    lap_table = None
    drivers = None

    def __init__(self, season, round):
        super().__init__(season, round)
        self.lap_table = self.set_lap_table()
        self.drivers = self.set_driver_map()
    
    def visualize(self):
        text = self.tweet_text()
        image_paths = [
            self.tweet_image_lap_positions()
        ]
        return {
            'text':text, 
            'image_paths':image_paths
        }


    def tweet_text(self):
        tweet_text = f"Lap by lap charts!"
        return tweet_text

    def tweet_image_lap_positions(self):
        grid_positions = self.lap_table[self.lap_table['lap']==0].sort_values('position', ascending=True).reset_index(drop=True)
        grid_positions =  grid_positions.merge(self.drivers, how='left', on='driverId')

        fig, ax = plt.subplots(figsize=(12,6))
        sns.lineplot(
            data=self.lap_table,
            x='lap', y='inverse_position', 
            hue='driverId', style='name_hash',
            ax=ax
        )

        for index,row in grid_positions.iterrows():
            ax.text(x = -3, y = -0.2 - (index+1), s = row.code, fontsize=12)
            ax.text(x = 1+self.lap_table['lap'].max(), y = -0.2 - (index+1), s = index+1, fontsize=12)

        ax.tick_params(axis='x', which='both', labelbottom=False)
        ax.tick_params(axis='y', which='both', labelleft=False)
        ax.set(xlabel='Laps', ylabel='')
        ax.set_title('Positions by Lap', fontsize=16)
        ax.get_legend().remove()

        fname = f"tweet_media/{self.season}_{self.round}_lap_positions.png"
        fig.savefig(fname, transparent=False, bbox_inches='tight')
        return fname

    
    def set_lap_table(self):
        race_results_url = "http://ergast.com/api/f1/{season}/{round}/results.json".format(
            season=self.season, round=self.round
        )
        race_results_response = requests.get(race_results_url)
        race_results_dict = json.loads(race_results_response.text)
        results = race_results_dict['MRData']['RaceTable']['Races'][0]['Results']

        lap_table = []

        for result in results:
            driverId = result['Driver']['driverId']
            grid_slot = int(result['grid'])
            num_laps = int(result['laps'])
            
            if num_laps == 0:
                break
            
            lap_table.append({
                'driverId': driverId,
                'position': grid_slot,
                'time': 0.0,
                'lap': 0
            })

            laptimes_url = "http://ergast.com/api/f1/{season}/{round}/drivers/{driver}/laps.json?limit={num_laps}".format(
                season=self.season, round=self.round, driver=driverId, num_laps=num_laps
            )
            laptimes_response = requests.get(laptimes_url)
            laptimes_dict = json.loads(laptimes_response.text)
            laptimes_results = laptimes_dict['MRData']['RaceTable']['Races'][0]['Laps']

            for lap in laptimes_results:
                lap_num = int(lap['number'])
                position = int(lap['Timings'][0]['position'])
                time = lap['Timings'][0]['time']
                lap_table.append({
                    'driverId': driverId,
                    'position': position,
                    'time': time,
                    'lap': lap_num
                })
        
        lap_df = pd.DataFrame(lap_table)
        lap_df['time'] = lap_df['time'].apply(stopwatchToSeconds)
        lap_df['position'] = lap_df['position'].astype('int')
        lap_df['inverse_position'] = -1 * lap_df['position']
        lap_df['name_hash'] = lap_df['driverId'].apply(lambda n: hash(n) % 2)
        return lap_df.copy()


    def set_driver_map(self):
        drivers_url = "http://ergast.com/api/f1/{season}/drivers.json".format(season=self.season)
        drivers_response = requests.get(drivers_url)
        drivers_dict = json.loads(drivers_response.text)
        drivers = drivers_dict['MRData']['DriverTable']['Drivers']
        return pd.DataFrame(drivers)[['driverId','familyName','code']].copy()


def stopwatchToSeconds(s):
    if isinstance(s, float):
        return s
    if (not isinstance(s, str)) or (s.find('.')==-1):
        return float('NaN')
    
    colonIndex = s.find(':')
    minutes = s[0 : colonIndex if colonIndex>=0 else 0]
    dotIndex = s.find('.')
    seconds = s[colonIndex+1 : dotIndex]
    millis = s[dotIndex+1 : ]
    return int(seconds) + int(millis)/1000 + 60*(0 if len(minutes)==0 else int(minutes))