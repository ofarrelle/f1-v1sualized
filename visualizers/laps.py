from matplotlib import image
import time as pytime
import requests
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_prettify import *

from visualizers.visualizer import Visualizer

class LapTimeVisualizer(Visualizer):
    lap_table = None
    drivers = None

    def __init__(self, season, round, highlighted_finisher=1):
        super().__init__(season, round)
        self.lap_table = self.set_lap_table()
        self.drivers = self.set_driver_map()
        self.highlighted_driver = self.set_highlighted_driver(highlighted_finisher)
        self.num_finishers_to_display = max(7, highlighted_finisher)
    
    def visualize(self):
        image_paths = [
            self.tweet_image_time_deltas(),
            self.tweet_image_lap_positions()
        ]
        
        image_paths = [x for x in image_paths if x!=""]
        return image_paths


    def tweet_text(self):
        tweet_text = f"Lap by lap charts!"
        return tweet_text

    def tweet_image_lap_positions(self):
        grid_positions = self.lap_table.query('lap == 0').sort_values('position', ascending=True).reset_index(drop=True)
        grid_positions = grid_positions.merge(self.drivers, how='left', on='driverId')
        
        driver_line_styles = grid_positions[['driverId', 'position']].copy()
        driver_line_styles['line_type'] = driver_line_styles['position'].apply(
            lambda p: 0 if p%2 == 0 else 1
        )
        driver_line_styles['line_thickness'] = driver_line_styles['position'].apply(
            lambda p: 4 if p%4 in (0,1) else 3
        )
        driver_line_styles = driver_line_styles.drop('position', axis=1)

        lap_positions = self.lap_table.merge(driver_line_styles, how='left', on='driverId')

        fig, ax = plt.subplots(figsize=(12,6))
        sns.lineplot(
            data=lap_positions,
            x='lap', y='inverse_position', 
            hue='driverId', 
            style='line_type', size='line_thickness',
            ax=ax
        )

        for index,row in grid_positions.iterrows():
            ax.text(x = -3, y = -0.2 - (index+1), s = row.code, fontsize=12)
            ax.text(x = 1+lap_positions['lap'].max(), y = -0.2 - (index+1), s = index+1, fontsize=12)

        ax.tick_params(axis='x', which='both', labelbottom=False)
        ax.tick_params(axis='y', which='both', labelleft=False)
        ax.set(xlabel='Laps', ylabel='')
        ax.set_title('Positions by Lap', fontsize=16)
        ax.get_legend().remove()

        fname = f"tweet_media/{self.season}_{self.round}_lap_positions.png"
        fig.savefig(fname, transparent=False, bbox_inches='tight')
        return fname

    def tweet_image_lap_times(self):
        final_lap_data_by_driver = self.get_final_lap_data()
        finishers = final_lap_data_by_driver.sort_values('position')['driverId']
    
        top_drivers = finishers.iloc[0:2].to_list()
        other_drivers = finishers.iloc[2:].sample(2).to_list()
        sampled_drivers = top_drivers + other_drivers

        lap_times = self.lap_table.query(f'lap != 0 & driverId in {sampled_drivers}')
        fastest_lap = lap_times['time'].min()
        lap_times = lap_times.query(f'time < {1.06*fastest_lap}')
        lap_times = lap_times.merge(self.drivers, how='inner', on='driverId')

        fig, ax = plt.subplots(figsize=(12,6))
        sns.lineplot(
            data=lap_times,
            x='lap', y='time', 
            hue='familyName',
            ax=ax
        )
        ax.set(
            title='Lap Times (excluding pit stops, safety cars)',
            xlabel='Lap', ylabel='Time (seconds)'
        )
        ax.get_legend().set_title('')

        fname = f"tweet_media/{self.season}_{self.round}_lap_times.png"
        fig.savefig(fname, transparent=False, bbox_inches='tight')
        return fname

    def tweet_image_time_deltas(self):
        final_lap_data_by_driver = self.get_final_lap_data()
        finishers = final_lap_data_by_driver.sort_values('position')['driverId']
        sampled_drivers = finishers.iloc[0:self.num_finishers_to_display].to_list()

        lap_times = self.lap_table.query(f'lap != 0 & driverId in {sampled_drivers}').copy()
        # https://stackoverflow.com/questions/32847800/how-can-i-use-cumsum-within-a-group-in-pandas
        lap_times['cum_time'] = lap_times.groupby('driverId')['time'].transform(pd.Series.cumsum)
        
        benchmark_lap_times = lap_times[lap_times['driverId'].isin(sampled_drivers)][['lap','time']].groupby(by='lap').median()
        benchmark_lap_times += 1 # slow down benchmark for plotting
        benchmark_cum_times = benchmark_lap_times.cumsum().reset_index()
        benchmark_cum_times = benchmark_cum_times.rename(columns={'time':'benchmark_cum_time'})
        benchmark_cum_times['benchmark_cum_time'] = benchmark_cum_times['benchmark_cum_time'] + 0.5
        
        lap_times = lap_times.merge(benchmark_cum_times, on='lap', how='inner')
        lap_times['interval'] = lap_times['benchmark_cum_time'] - lap_times['cum_time']
        lap_times = lap_times.merge(self.drivers, how='inner', on='driverId')

        lap_times['line_thickness'] = lap_times['driverId'].apply(
            lambda x: 4 if x==self.highlighted_driver else 3
        )
        fig, ax = plt.subplots(figsize=(12,6))
        sns.lineplot(
            data=lap_times,
            x='lap', y='interval', 
            hue='familyName',
            size = 'line_thickness',
            ax=ax
        )
        ax.set(
            title=f'Race Progression of the top {len(sampled_drivers)}',
            xlabel='Lap', ylabel='Seconds Ahead/Behind'
        )
        
        sampled_drivers_family_names = self.drivers.set_index('driverId').loc[sampled_drivers, 'familyName'].to_list()
        ax.legend(sampled_drivers_family_names)

        fname = f"tweet_media/{self.season}_{self.round}_time_deltas.png"
        fig.savefig(fname, transparent=False, bbox_inches='tight')
        return fname
    
    def benchmark_driver(self, sampled_drivers):
        return sampled_drivers[2]

    def set_lap_table(self):
        race_results_url = "http://ergast.com/api/f1/{season}/{round}/results.json".format(
            season=self.season, round=self.round
        )
        race_results_response = requests.get(race_results_url)
        race_results_dict = json.loads(race_results_response.text)
        results = race_results_dict['MRData']['RaceTable']['Races'][0]['Results']

        lap_table = []
        grid_table = []

        for result in results:
            pytime.sleep(0.5)

            driverId = result['Driver']['driverId']
            grid_slot = int(result['grid'])
            num_laps = int(result['laps'])
            
            if num_laps == 0:
                break
            
            grid_table.append({
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
        
        # deal with pit lane starters in grid table
        max_grid_used = max([x['position'] for x in grid_table])
        pit_lane_starters_seen = 0
        # uniqueify and rebalance pit lane grid indices
        for x in grid_table:
            if x['position'] == 0:
                pit_lane_starters_seen += 1
                x['position'] = max_grid_used + pit_lane_starters_seen                        
            lap_table.append(x)

        lap_df = pd.DataFrame(lap_table)
        lap_df['time'] = lap_df['time'].apply(stopwatchToSeconds)
        lap_df['position'] = lap_df['position'].astype('int')
        lap_df['inverse_position'] = -1 * lap_df['position']
        return lap_df.copy()


    def set_driver_map(self):
        drivers_url = "http://ergast.com/api/f1/{season}/drivers.json".format(season=self.season)
        drivers_response = requests.get(drivers_url)
        drivers_dict = json.loads(drivers_response.text)
        drivers = drivers_dict['MRData']['DriverTable']['Drivers']
        drivers_df = pd.DataFrame(drivers)[['driverId','familyName','code']]
        return drivers_df.copy()

    def get_final_lap_data(self):
        max_lap_by_driver = self.lap_table.groupby('driverId')['lap'].max().reset_index()
        final_lap_data_by_driver = max_lap_by_driver.merge(self.lap_table, how="inner", on=['driverId','lap'])
        return final_lap_data_by_driver
    
    def set_highlighted_driver(self, finish_pos):
        final_lap_data_by_driver = self.get_final_lap_data()
        return final_lap_data_by_driver.query(f'position == {finish_pos}')['driverId'].iloc[0]


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