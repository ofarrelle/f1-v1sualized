import requests
import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from mpl_prettify import *
from visualizers.visualizer import Visualizer

class SeasonCompletionVisualizer(Visualizer):
    season_num_races = 0
    race_table = None

    def __init__(self, season, round):
        super().__init__(season, round)
        self.race_table = self.set_race_table()
        

    def visualize(self):
        image_paths = []
        if self.round > 1 and (self.round % 3 == 0 or self.season_num_races == self.round):
            image_paths.append(self.tweet_image_world_map())

        return image_paths


    def tweet_text(self):
        tweet_text = f"Following the {self.name}, we are {float(self.round) / self.season_num_races:.0%} of the way through the {self.season} season."
        if self.season_num_races - self.round != 0:
            tweet_text += f"\nThere are {self.season_num_races - self.round} races remaining."
        return tweet_text

    
    def tweet_image_world_map(self):
        locations = pd.DataFrame([ self.race_table[i]['Circuit']['Location'] for i in range(self.round) ])
        locations['lat'] = locations['lat'].astype('float')
        locations['long'] = locations['long'].astype('float')

        long_lims = (locations.long.min() - 10, locations.long.max() + 10)
        lat_lims = (locations.lat.min() - 5, locations.lat.max() + 5)

        fig, ax = plt.subplots(figsize=(12,8))
        countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

        countries.plot(color="lightgrey", ax=ax)
        locations.plot(x="long", y="lat", kind="line", c=PASTEL_RED, ax=ax)
        for index,row in locations.iterrows():
            ax.text(x=row.long-2, y=row.lat+2, s=index+1, fontsize=14)
            ax.text(
                x = long_lims[1] + 2, 
                y = lat_lims[1] - (lat_lims[1]-lat_lims[0]) * (index+1) / 22, 
                s=f"{index+1} - {row.locality}, {row.country}", 
                fontsize=14
            )

        ax.tick_params(axis='both', which='both', bottom=False, left=False, labelbottom=False, labelleft=False)
        ax.set_xlim(long_lims)
        ax.set_ylim(lat_lims)
        ax.set_xlabel('')
        ax.text(x=long_lims[0]+3, y=lat_lims[1]-4, s='How Did We Get Here?', fontsize=20, c=PASTEL_PRISMARINE)
        ax.get_legend().remove()

        fname = f"tweet_media/{self.season}_{self.round}_travel_map.png"
        fig.savefig(fname, transparent=False, bbox_inches='tight')
        return fname


    def set_race_table(self):
        season_url = "http://ergast.com/api/f1/{season}.json".format(season=self.season)
        season_response = requests.get(season_url)
        season_dict = json.loads(season_response.text)
        self.season_num_races = int(season_dict['MRData']['total'])
        return season_dict['MRData']['RaceTable']['Races']