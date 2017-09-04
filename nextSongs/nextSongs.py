from appdirs import *
from dateutil.relativedelta import relativedelta
from enum import Enum
import datetime
import json
import logging
import os
import random


logger = logging.getLogger('nextSongs')

class Config:
    """
    static class that holds the configuration
    """
    songs_per_day = 10     # count of songs that will be played per day
    old_songs_per_day = 2  # count of old songs that will be played per day
    middle_old_period = 1  # count of middle old songs that will be played per day
    fill_up_song_list = False # fill song list until the songs_per_day count is reached
    shuffle_middle_old = True # wheather to shuffle middle old song list or not

    def __inti__(self):
        pass

    @staticmethod
    def read_config():
        """
        reads configuration from config file
        """
        if not os.path.isfile(config_filename):
            Config.save_config()
            raise Exception("config file does not exist. try to rerun the program.")
        with open(config_filename) as data_file:    
            config = json.load(data_file)
        Config.songs_per_day = config["songs_per_day"]
        Config.old_songs_per_day = config["old_songs_per_day"]
        Config.middle_old_period = config["middle_old_period"]
        Config.fill_up_song_list = config["fill_up_song_list"]

    @staticmethod
    def save_config():
        """
        saves configuration to config file
        """
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


config = Config()
appname = 'nextSongs'
appauthor = 'random'
config_filename = os.path.join(user_data_dir(appname, appauthor), 'config.json')
data_filename = os.path.join(user_data_dir(appname, appauthor), 'data.json')



class SongFlags(Enum):
    FORCE_MIDDLE_OLD = 1
    REMOVE_FROM_PLAYABLE = 2

class Song:
    """
    Object that represents a song in the song list
    """
    def __init__(self, title, date, current=False, middle_old=False):
        self.title = title
        self.date = date
        self.current = current
        # self.enforce_middle_aged_category = middle_old
        self.flags = []
        self.location = ""
        self.weight = 1
        self.filepath = ""

    def is_force_middle_old(self):
        return SongFlags.FORCE_MIDDLE_OLD in self.flags

    def set_force_middle_old(self, b):
        if b and SongFlags.FORCE_MIDDLE_OLD not in self.flags:
            self.flags.append(SongFlags.FORCE_MIDDLE_OLD)
            self.set_playable(True)
        elif not b and SongFlags.FORCE_MIDDLE_OLD in self.flags:
            self.flags.remove(SongFlags.FORCE_MIDDLE_OLD)

    def is_playable(self):
        return not SongFlags.REMOVE_FROM_PLAYABLE in self.flags

    def set_playable(self, b):
        if b and SongFlags.REMOVE_FROM_PLAYABLE in self.flags:
            self.flags.remove(SongFlags.REMOVE_FROM_PLAYABLE)
        elif not b and SongFlags.REMOVE_FROM_PLAYABLE not in self.flags:
            self.flags.append(SongFlags.REMOVE_FROM_PLAYABLE)
            self.set_force_middle_old(False)

    def __repr__(self):
        return "<Song(Title: " + self.title + ")>"

def get_test_songs():
    """
    function to generate test songs
    :return: list-of-Song
    """
    songs = []
    songs.append(Song("Rock me mama", datetime.date(2017, 8, 5), True))
    songs.append(Song("Test 1", datetime.date(2017, 8, 5)))
    songs.append(Song("Test 2", datetime.date(2017, 8, 4)))
    songs.append(Song("Test 3", datetime.date(2017, 8, 9)))
    songs.append(Song("Test 4", datetime.date(2017, 8, 1)))
    songs.append(Song("Test 5", datetime.date(2017, 8, 2)))
    songs.append(Song("Test 6", datetime.date(2017, 8, 10)))
    songs.append(Son/g("Test 7", datetime.date(2017, 8, 10)))
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
    """
    object that holds the list of songs and provides methods to generate lists of songs to practice
    """
    def __init__(self, add_test_songs=False):
        self.songs = []
        if add_test_songs:
            self.songs.extend(get_test_songs())

    def get_playable_songs(self):
        """
        generates a list of songs the user wants to play
        :return: list-of-Song
        """
        return list(filter(lambda x: x.is_playable(), self.songs))

    def write_songs(self):
        """
        save songs into file
        """
        data = {'songs': []}
        for song in self.songs:
            flags = []
            for flag in song.flags:
                flags.append(flag.name)

            data["songs"].append({'title': song.title, 
                'date': song.date.toordinal(), 
                'weight': song.weight,
                'current': song.current,
                'location': song.location,
                'filepath': song.filepath,
                'flags': flags
                })

        if not os.path.exists(os.path.dirname(data_filename)):
            try:
                os.makedirs(os.path.dirname(data_filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(data_filename, "w+") as f:
            json.dump(data, f)

    def read_songs(self):
        """
        read songs from file
        """
        if not os.path.isfile(data_filename):
            self.write_songs()
            raise Exception("config file does not exist. try to rerun this program")
        with open(data_filename) as data_file:    
            data = json.load(data_file)
        for song in data['songs']:
            s = Song(song['title'], datetime.date.fromordinal(song['date']), song['current'])
            s.weight = song['weight']
            if 'location' in song.keys():
                s.location = song['location']
            if 'enforce_middle_old' in song.keys() and song['enforce_middle_old']:
                # legace option
                s.flags.append(SongFlags.FORCE_MIDDLE_OLD)
            if 'flags' in song.keys():
                for flag in song['flags']:
                    s.flags.append(SongFlags[flag])

            if 'filepath' in song.keys():
                s.filepath = song['filepath']
            self.songs.append(s)

    def get_middle_old_songs(self, date=None):
        """
        generates a list of middle old songs
        :param date: the date the middle old song list will be generated for. if empty, the list won't be shuffled
        :return: list-of-Songs
        """
        count = self.get_count_of_middle_old_songs()
        middle_old_songs = []
        songs = list(reversed(sorted(self.get_playable_songs(), key=lambda x: x.date)))
        # add enforced middle old songs
        for song in songs:
            if len(middle_old_songs) >= count:
                break
            if song.is_force_middle_old() and not song.current:
                middle_old_songs.append(song)

        for song in songs:
            # skip current songs
            if song.current or song.is_force_middle_old():
                continue
            if len(middle_old_songs) >= count:
                break
            middle_old_songs.append(song)

        # shuffle list if option is enabled
        if Config.shuffle_middle_old and date is not None:
            seed_date = date.timetuple().tm_yday - date.timetuple().tm_yday % Config.middle_old_period
            oldRandomState = random.getstate()
            random.seed(seed_date)
            random.shuffle(middle_old_songs)
            random.setstate(oldRandomState)

        return middle_old_songs

    def get_old_songs(self, exclude_songs=[]):
        """
        generates a list of old songs
        :param exclude_songs: list-of-Songs that will be excluded from the generated list
        :return: list-of-Songs
        """
        songs = self.get_playable_songs()
        middle_old_songs_count = self.get_count_of_middle_old_songs()
        old_songs = []
        middle_old_songs = self.get_middle_old_songs()
        # add all songs that are not in 'current' category
        for song in songs:
            if not song.current and song not in middle_old_songs and song not in exclude_songs:
                old_songs.append(song)
        return old_songs

    def expand_old_songs(self, old_songs):
        """
        duplicates songs in a list according to their weight, so that songs with a higher weight will be chosen more often
        :param old_songs: list of old songs
        :return: list-of-Songs
        """
        expanded_old_songs = []
        for song in old_songs:
            for i in range(0, song.weight):
                expanded_old_songs.append(song)
        return expanded_old_songs

    def get_count_of_middle_old_songs(self):
        """
        calculates the count of songs that will be in the list of middle old songs
        :return: int
        """
        if config.songs_per_day <= len(self.get_playable_songs()):
            return (config.songs_per_day - len(self.get_current_songs()) - config.old_songs_per_day) * config.middle_old_period
        else:
            # if less songs are available than should be played on a day, use
            # count of available songs instead of configured daily songs as
            # base to calculate middle old songs per day
            return (len(self.get_playable_songs()) - len(self.get_current_songs()) - config.old_songs_per_day) * config.middle_old_period

    def get_middle_old_songs_by_slot(self, slot, date=None):
        """
        generates the list of middle old songs for a slot
        :param slot: int; the day in the middle old interval
        :param date: the date, this list will be generated for. If None the list of middle old songs won't be shuffled
        :return: list-of-Songs
        """
        songs_today = []
        songs = self.get_playable_songs()
        count_of_middle_old_songs = self.get_count_of_middle_old_songs()
        todays_middle_old_slot = slot
        if count_of_middle_old_songs <= 0:
            # raise Exception("Too many songs marked as current. current songs + old songs dont leave place for any middle old song")
            logger.warning("Too many songs marked as current. current songs + old songs dont leave place for any middle old song")
        middle_old_songs = self.get_middle_old_songs(date)
        middle_old_songs_per_day = int(count_of_middle_old_songs / config.middle_old_period)
        # add middle old songs that are in todays_middle_old_slot
        for i in range( middle_old_songs_per_day * todays_middle_old_slot, middle_old_songs_per_day * todays_middle_old_slot + middle_old_songs_per_day ):
            # break if we dont have more middle old songs
            if i >= len(middle_old_songs):
                break
            songs_today.append(middle_old_songs[i])
        return songs_today

    def get_current_songs(self):
        """
        generates a list of current songs
        :return: list-of-Songs
        """
        songs = self.get_playable_songs()
        songs_today = []
        for song in songs:
            if len(songs_today) > config.songs_per_day - config.old_songs_per_day:
                # raise Exception("More songs marked as current than slots available for songs_per_day")
                logger.warning("More songs marked as current than slots available for songs_per_day")
            if song.current:
                songs_today.append(song)
        return songs_today

    def get_songs_for_date(self, date, exclude_songs=[]):
        """
        generate list of songs for a given date
        :param date: datetime.date object representing the day, the list is generated for
        :param exclude_songs: list of Song. Songs that will be excluded while generating old_songs list
        :return: list of song
        """
        songs_today = []
        # sort songs by date
        songs = list(reversed(sorted(self.get_playable_songs(), key=lambda x: x.date)))
        # append current songs
        songs_today.extend(self.get_current_songs())

        # get count of songs in middle old category
        todays_middle_old_slot = date.timetuple().tm_yday % config.middle_old_period
        songs_today.extend(self.get_middle_old_songs_by_slot(todays_middle_old_slot, date))

        # add random old songs
        # get old songs, excluding exclude_songs
        old_songs = self.get_old_songs(exclude_songs)
        # if old_song list is smaller than old_songs_per_day get old_songs without exluding any songs
        if len(old_songs) < config.old_songs_per_day:
            old_songs = self.get_old_songs()

        if config.fill_up_song_list:
            old_songs_count = config.songs_per_day - len(songs_today)
        else:
            old_songs_count = config.old_songs_per_day
        for i in range(0, old_songs_count):
            try:
                old_song = random.choice(self.expand_old_songs(old_songs))
            except IndexError:
                logger.warning("no old songs left")
                # break if we dont have any song left
                break
            songs_today.append(old_song)
            old_songs.remove(old_song)

        return songs_today



    

def main():
    print("reading config from", config_filename)
    Config.read_config()
    print("loading data from", data_filename)
    st = SongTimer()
    st.read_songs()
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
    Config.save_config()
    print("storing songs under", data_filename)
    st.write_songs()

if __name__ == "__main__":
    main()
