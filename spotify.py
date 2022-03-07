import json
import os
import pathlib
from typing import Dict

album_count = {}
artist_count = {}
track_count = {}
year_count = {}
year_trackers : Dict[int, "YearTracker"] = {}

def add_count(s, d):
    if s in d:
        d[s] += 1
    else:
        d[s] = 1

def write_to_json(name : str, d : Dict, idx=1):
    with open(name + ".json", "w", encoding='utf8') as file:
        s = {k: v for k, v in sorted(d.items(), key=lambda item: item[idx], reverse=True)}
        json.dump(s, file, ensure_ascii=False)

class YearTracker:

    def __init__(self, year : int):
        self.year = year
        self.albums : Dict[str, int] = {}
        self.artists : Dict[str, int] = {}
        self.tracks : Dict[str, int] = {}
    
    def add_album(self, album):
        add_count(album, self.albums)

    def add_artist(self, artist):
        add_count(artist, self.artists)

    def add_track(self, track):
        add_count(track, self.tracks)

    def write(self):
        dir = str(self.year) + "/"
        if not os.path.exists(dir):
            os.mkdir(dir)
        write_to_json(dir + "albums", self.albums)
        write_to_json(dir + "artists", self.artists)
        write_to_json(dir + "tracks", self.tracks)

for path in pathlib.Path("imports").iterdir():
    if path.is_file():
        with open(path, "r") as file:
            for d in json.load(file):
                album = d["albumName"]
                artist = d["artistName"]
                track = d["trackName"]
                year = d["time"][:4]
                add_count(album, album_count)
                add_count(artist, artist_count)
                add_count(track, track_count)
                add_count(year, year_count)
                if year not in year_trackers:
                    year_trackers[year] = YearTracker(year)
                tracker = year_trackers[year]
                tracker.add_album(album)
                tracker.add_artist(artist)
                tracker.add_track(track)

p = "all_time/"
if not os.path.exists(p):
    os.mkdir(p)
for name, d in {"albums":album_count, "artists":artist_count, "tracks":track_count}.items():
    write_to_json(p + name, d)

write_to_json(p + "years", year_count, 0)

for tracker in year_trackers.values():
    tracker.write()
