import nextSongs
import datetime
import sys
from PyQt4.QtGui import *

st = nextSongs.SongTimer()
st.read_songs()

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
    if 'current' status changed, apply it also to its song item
    also change date if it was changed
    """
    if isinstance(item, QSong):
        item.song.title = item.text()
        item.song.current = item.checkState()
    elif isinstance(item, QSongDate):
        try:
            d = item.text().split('-')
            year = int(d[0])
            month = int(d[1])
            day = int(d[2])
            d = datetime.date(year, month, day)
            item.song.date = d
            item.setText(str(item.song.date))

        except:
            item.setText(str(item.song.date))
    st.write_songs()

def show_todays_songs():
    list_popup = QListView()
    list_popup.setWindowTitle('Todays songs')
    list_popup.setMinimumSize(600, 400)
    model = QStandardItemModel(list_popup)
    for song in st.get_songs_for_date(datetime.datetime.now()):
        print(song.title)
        item = QSong(song)
        model.appendRow(item)
    list_popup.setModel(model)


    dialog = QDialog()
    # Create exit button
    exit_btn = QPushButton('Exit')
    exit_btn.clicked.connect(dialog.accept)
    dialog.list_popup = list_popup
    dialog.verticalLayout = QVBoxLayout(dialog)
    dialog.verticalLayout.addWidget(dialog.list_popup)
    dialog.verticalLayout.addWidget(exit_btn)
    dialog.exec_()

# Create a Qt application
app = QApplication(sys.argv)
widget = QWidget()
layout = QGridLayout()
 
# Our main window will be a QTableView
# list = QListView()
list = QTableView()
list.setWindowTitle('Example List')
list.setMinimumSize(600, 400)
 
# Create an empty model for the list's data
model = QStandardItemModel(list)
model.setHorizontalHeaderLabels(['Title', 'Date'])
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
def add_song():
    song = nextSongs.Song("Song Title", datetime.datetime.now().date())
    st.songs.append(song)
    item = QSong(song)
    item.setColumnCount(2)
    item.appendColumn([QSongDate(song)])
    item.setCheckable(True)
    if song.current:
        item.setCheckState(2)
    model.appendRow([item, QSongDate(song)])
    list.resizeColumnsToContents()
    st.write_songs()

add_btn = QPushButton('Add Song')
add_btn.clicked.connect(add_song)
add_btn.resize(add_btn.sizeHint())

# Create todays songs button
todays_songs_btn = QPushButton('Todays Songs')
todays_songs_btn.clicked.connect(show_todays_songs)
todays_songs_btn.resize(todays_songs_btn.sizeHint())

# Create delete button
def delete_selected_song():
    if len(list.selectedIndexes()) == 0:
        return
    indices = [list.selectedIndexes()[0]]
    for i in indices:
        item = model.itemFromIndex(i)
        st.songs.remove(item.song)
        model.removeRow(i.row())
    list.resizeColumnsToContents()
    st.write_songs()

del_btn = QPushButton('Remove Song')
del_btn.clicked.connect(delete_selected_song)
del_btn.resize(del_btn.sizeHint())

# Create exit button
exit_btn = QPushButton('Exit')
exit_btn.clicked.connect(exit)
exit_btn.resize(exit_btn.sizeHint())

# fit column to content size
list.resizeColumnsToContents()

# Add widgets to layout
layout.addWidget(todays_songs_btn)
layout.addWidget(add_btn)
layout.addWidget(del_btn)
layout.addWidget(list)
layout.addWidget(exit_btn)
# Show the window and run the app
widget.setLayout(layout)
widget.show()
app.exec_()
