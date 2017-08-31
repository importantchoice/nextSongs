import nextSongs
import datetime
import sys
from PyQt4.QtGui import *

st = nextSongs.SongTimer(True)

class QSong(QStandardItem):
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setText(song.title)

class QSongDate(QStandardItem):
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setText(str(song.date))

def on_item_changed(item):
    """
    if current status changed, apply it also to its song item
    """
    item.song.title = item.text()
    item.song.current = item.checkState()

def show_todays_songs():
    for song in st.get_songs_for_date(datetime.datetime.now()):
        print(song.title)

    

# Create a Qt application
app = QApplication(sys.argv)
widget = QWidget()
layout = QGridLayout()
 
# Our main window will be a QListView
list = QListView()
list.setWindowTitle('Example List')
list.setMinimumSize(600, 400)
 
# Create an empty model for the list's data
model = QStandardItemModel(list)
model.itemChanged.connect(on_item_changed)
model.setColumnCount(2)

for song in st.songs:
    # create an item with a caption
    item = QSong(song)
    item.setColumnCount(2)
    item.appendColumn([QSongDate(song)])
 
    # add a checkbox to it
    item.setCheckable(True)
    if song.current:
        item.setCheckState(2)
 
    # Add the item to the model
    model.appendRow([item, QSongDate(song)])
 
# Apply the model to the list view
list.setModel(model)

# Create add button
todays_songs_btn = QPushButton('Todays Songs')
todays_songs_btn.clicked.connect(show_todays_songs)
todays_songs_btn.resize(todays_songs_btn.sizeHint())

def delete_selected_song():
    for i in list.selectedIndexes():
        item = model.itemFromIndex(i)
        st.songs.remove(item.song)
        model.removeRow(i.row())

del_btn = QPushButton('Remove Song')
del_btn.clicked.connect(delete_selected_song)
del_btn.resize(del_btn.sizeHint())


# Add widgets to layout
layout.addWidget(todays_songs_btn)
layout.addWidget(del_btn)
layout.addWidget(list)
# Show the window and run the app
widget.setLayout(layout)
widget.show()
app.exec_()
