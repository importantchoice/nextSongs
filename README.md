`nextSongs` shows the next set of songs, which you can practice on your
instrument. Therefor it uses a category based approach, you might know from
vocabulary trainer.

![nextSongs UI Screenshot](https://raw.githubusercontent.com/importantchoice/nextSongs/master/Screenshots/nextSongs.png)

# The idea

All songs are divided into three categories: `current`, `middle old` and `old`.

* Songs in the `current` category will appear every day.
* Songs in the `middle old` category will appear every n-th day. This interval can be configured.
* Songs in the `old` category will appear randomly

The count of songs in `middle old` category will be dynamically calculated.

# Installation

```
$ pip install -r requirements.txt
$ python setup.py install
```

# Preferences

The preferences window can be reached via `File->Preferences`. Here following settings can be made:

* `Songs per day` - This is the overall count of songs that will be displayed per day.
* `Old songs per day` - Defines how many songs will be taken from `old` category.
* `Interval to repeat all middle old songs` - This is the count of days you need to play all songs in `middle old` category.

If you want more songs to be in `middle old` category, you can either play more songs each day (increase `Songs per day` value), or increase the `Interval to repeat all middle old songs`.
