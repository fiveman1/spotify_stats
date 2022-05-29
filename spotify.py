import json
import os
import pathlib
from typing import Dict

def add_count(s, d, c=1):
    if s in d:
        d[s] += c
    else:
        d[s] = c

def write_to_json(name : str, d : Dict, idx=1):
    with open(name + ".json", "w", encoding='utf8') as file:
        s = {k: v for k, v in sorted(d.items(), key=lambda item: item[idx], reverse=True)}
        json.dump(s, file, ensure_ascii=False)

class Track:

    def __init__(self, album : str, artist : str, track : str, uri : str):
        self.album = album
        self.artist = artist
        self.track = track
        self.uri = uri

    def __hash__(self):
        return hash(self.uri)

    def __eq__(self, other):
        return isinstance(other, Track) and self.uri == other.uri

    @staticmethod
    def from_dict(d) -> "Track":
        return Track(d["master_metadata_album_album_name"],
                     d["master_metadata_album_artist_name"],
                     d["master_metadata_track_name"],
                     d["spotify_track_uri"][14:])

class YearTracker:

    def __init__(self, year : str):
        self.year = year
        self.tracks : Dict[Track, int] = {}

    def add_track(self, track):
        add_count(track, self.tracks)

    def create_stats(self, all_albums, all_artists, all_tracks) -> int:
        dir = str(self.year) + "/"
        if not os.path.exists(dir):
            os.mkdir(dir)
        albums = {}
        artists = {}
        tracks = {}
        total = 0
        for track, count in self.tracks.items():
            add_count(track.album, albums, count)
            add_count(track.artist, artists, count)
            add_count(track.track, tracks, count)
            add_count(track.album, all_albums, count)
            add_count(track.artist, all_artists, count)
            add_count(track.track, all_tracks, count)
            total += count
        write_to_json(dir + "albums", albums)
        write_to_json(dir + "artists", artists)
        write_to_json(dir + "tracks", tracks)
        return total

    def __hash__(self):
        return hash(self.year)

    def __eq__(self, other):
        return isinstance(other, YearTracker) and self.year == other.year

def main():
    uri_to_track = {}
    year_trackers : Dict[str, YearTracker] = {}

    year_to_minutes = {}

    for path in pathlib.Path("imports").iterdir():
        if path.is_file():
            with open(path, "r", encoding="utf-8") as file:
                for d in json.load(file):
                    uri = d["spotify_track_uri"]
                    duration = d["ms_played"]
                    year = d["ts"][:4]
                    if year in year_to_minutes:
                        year_to_minutes[year] += duration
                    else:
                        year_to_minutes[year] = duration
                    if duration < 30000 or uri is None:
                        continue
                    id = uri[14:]
                    if id in uri_to_track:
                        track = uri_to_track[id]
                    else:
                        track = Track.from_dict(d)
                        uri_to_track[id] = track
                    
                    if year in year_trackers:
                        tracker = year_trackers[year]
                    else:
                        tracker = YearTracker(year)
                        year_trackers[year] = tracker
                    tracker.add_track(track)
                    add_count(track, uri_to_track)
                    

    all_albums = {}
    all_artists = {}
    all_tracks = {}
    years = {}
    for tracker in year_trackers.values():
        years[tracker.year] = tracker.create_stats(all_albums, all_artists, all_tracks)

    dir = "all_time/"
    if not os.path.exists(dir):
        os.mkdir(dir)

    for name, d in {"albums":all_albums, "artists":all_artists, "tracks":all_tracks}.items():
        write_to_json(dir + name, d)

    write_to_json(dir + "years", years, 0)
    write_to_json(dir + "minutes", {y: m // 60000 for y, m in year_to_minutes.items()}, 0)
        
if __name__ == "__main__":
    main()
