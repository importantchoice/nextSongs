import datetime
import json
import os
from appdirs import *
from dateutil.relativedelta import relativedelta
import random

class Config:
    songs_per_day = 10     # count of songs that will be played per day
    old_songs_per_day = 2  # count of old songs that will be played per day
    middle_old_period = 1  # count of middle old songs that will be played per day
    fill_up_song_list = False # fill song list until the songs_per_day count is reached

    def __inti__(self):
        pass
config = Config()

appname = 'nextSongs'
appauthor = 'random'
config_filename = os.path.join(user_data_dir(appname, appauthor), 'config.json')
data_filename = os.path.join(user_data_dir(appname, appauthor), 'data.json')

def read_config():
    if not os.path.isfile(config_filename):
        save_config()
        raise Exception("config file does not exist. try to rerun the program.")
    with open(config_filename) as data_file:    
        config = json.load(data_file)
    Config.songs_per_day = config["songs_per_day"]
    Config.old_songs_per_day = config["old_songs_per_day"]
    Config.middle_old_period = config["middle_old_period"]
    Config.fill_up_song_list = config["fill_up_song_list"]

def save_config():
    config = {}
    config["songs_per_day"] = Config.songs_per_day
    config["old_songs_per_day"] = Config.old_songs_per_day
    config["middle_old_period"] = Config.middle_old_period
    config["fill_up_song_list"] = Config.fill_up_song_list

    if not os.path.exists(os.path.dirname(config_filename)):
        try:
            os.makedirs(os.path.dirname(config_filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(config_filename, "w+") as f:
        json.dump(config, f)



class Song:
    def __init__(self, title, date, current=False):
        self.title = title
        self.date = date
        self.current = current

def get_test_songs():
    songs = []
    songs.append(Song("Rock me mama", datetime.date(2017, 8, 5), True))
    songs.append(Song("Test 1", datetime.date(2017, 8, 5)))
    songs.append(Song("Test 2", datetime.date(2017, 8, 4)))
    songs.append(Song("Test 3", datetime.date(2017, 8, 9)))
    songs.append(Song("Test 4", datetime.date(2017, 8, 1)))
    songs.append(Song("Test 5", datetime.date(2017, 8, 2)))
    songs.append(Song("Test 6", datetime.date(2017, 8, 10)))
    songs.append(Song("Test 7", datetime.date(2017, 8, 10)))
    songs.append(Song("Test 8", datetime.date(2017, 8, 10)))
    songs.append(Song("Test 9", datetime.date(2017, 8, 10)))
    songs.append(Song("Test 10", datetime.date(2017, 8, 10)))
    songs.append(Song("Test 11", datetime.date(2017, 8, 10)))
    songs.append(Song("Test 12", datetime.date(2017, 8, 10)))
    songs.append(Song("Test 13", datetime.date(2017, 8, 10)))
    songs.append(Song("Test 15", datetime.date(2017, 8, 10)))
    songs.append(Song("Test 14", datetime.date(2017, 8, 10)))
    return songs

class SongTimer:
    def __init__(self, add_test_songs=False):
        self.songs = []
        if add_test_songs:
            self.songs.extend(get_test_songs())

    def write_songs(self):
        data = {'songs': []}
        for song in self.songs:
            data["songs"].append({'title': song.title, 'date': song.date.toordinal(), 'current': song.current})

        if not os.path.exists(os.path.dirname(data_filename)):
            try:
                os.makedirs(os.path.dirname(data_filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(data_filename, "w+") as f:
            json.dump(data, f)

    def read_songs(self):
        if not os.path.isfile(data_filename):
            self.write_songs()
            raise Exception("config file does not exist. try to rerun this program")
        with open(data_filename) as data_file:    
            data = json.load(data_file)
        for song in data['songs']:
            s = Song(song['title'], datetime.date.fromordinal(song['date']), song['current'])
            self.songs.append(s)

    def get_middle_old_songs(self, songs, count):
        middle_old_songs = []
        songs = sorted(songs, key=lambda x: x.date)
        for song in songs:
            # skip current songs
            if song.current:
                continue
            if len(middle_old_songs) >= count:
                break
            middle_old_songs.append(song)
        return middle_old_songs

    def get_old_songs(self, songs, middle_old_songs_count):
        old_songs = []
        middle_old_songs = self.get_middle_old_songs(songs, middle_old_songs_count)
        # add all songs that are not in 'current' category
        for song in songs:
            if not song.current:
                old_songs.append(song)
        # remove all songs that are in 'middle old' category
        for song in middle_old_songs:
            old_songs.remove(song)
        return old_songs

    def get_songs_for_date(self, date):
        songs_today = []
        # sort songs by date
        songs = sorted(self.songs, key=lambda x: x.date)
        # append current songs
        for song in songs:
            if len(songs_today) > config.songs_per_day - config.old_songs_per_day:
                raise Exception("More songs marked as current than slots available for songs_per_day")
            if song.current:
                songs_today.append(song)
        # get count of songs in middle old category
        count_of_middle_old_songs = (config.songs_per_day - len(songs_today) - config.old_songs_per_day) * config.middle_old_period
        todays_middle_old_slot = date.timetuple().tm_yday % config.middle_old_period
        if count_of_middle_old_songs <= 0:
            raise Exception("Too many songs marked as current. current songs + old songs dont leave place for any middle old song")
        middle_old_songs = self.get_middle_old_songs(songs, count_of_middle_old_songs)
        middle_old_songs_per_day = int(count_of_middle_old_songs / config.middle_old_period)
        # add middle old songs that are in todays_middle_old_slot
        for i in range( middle_old_songs_per_day * todays_middle_old_slot, middle_old_songs_per_day * todays_middle_old_slot + middle_old_songs_per_day ):
            # break if we dont have more middle old songs
            if i >= len(middle_old_songs):
                break
            songs_today.append(middle_old_songs[i])
        # add random old songs
        old_songs = self.get_old_songs(songs, count_of_middle_old_songs)
        if config.fill_up_song_list:
            old_songs_count = config.songs_per_day - len(songs_today)
        else:
            old_songs_count = config.old_songs_per_day
        for i in range(0, old_songs_count):
            try:
                old_song = random.choice(old_songs)
            except IndexError:
                print("no old songs left")
                # break if we dont have any song left
                break
            songs_today.append(old_song)
            old_songs.remove(old_song)

        return songs_today



    

def main():
    print("reading config from", config_filename)
    read_config()
    print("loading data from", data_filename)
    st = SongTimer(True)
    d = datetime.datetime.now() + relativedelta(days=+0)
    songs_today = st.get_songs_for_date(d)
    print("Today:")
    for song in songs_today:
        print(song.title)
    d += relativedelta(days=+1)
    songs_tomorrow = st.get_songs_for_date(d)
    print("\nTomorrow:")
    for song in songs_tomorrow:
        print(song.title)
    print("storing config under", config_filename)
    save_config()
    print("storing songs under", data_filename)
    st.write_songs()

if __name__ == "__main__":
    main()
    
