import nextSongs.nextSongs as nextSongs
# import nextSongs as nextSongs
import datetime
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

nextSongs.Config.read_config()
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

class QSongWeight(QStandardItem):
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setText(str(song.weight))


def show_todays_songs():
    todays_songs = Todays_Songs()
    todays_songs.exec_()

class Todays_Songs(QDialog):
    def __init__(self):
        super().__init__()
        list_popup = QListView()
        list_popup.setWindowTitle('Todays songs')
        list_popup.setMinimumSize(600, 400)
        model = QStandardItemModel(list_popup)
        for song in st.get_songs_for_date(datetime.datetime.now()):
            item = QSong(song)
            model.appendRow(item)
        list_popup.setModel(model)

        exit_btn = QPushButton('Exit')
        exit_btn.clicked.connect(self.accept)
        self.list_popup = list_popup
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.list_popup)
        self.verticalLayout.addWidget(exit_btn)

def show_preferences():
    prefs = Preferences()
    prefs.exec_()

class Preferences(QDialog):
    def __init__(self):
        super().__init__()
        self.settings_spd = QSpinBox()
        self.settings_spd.setMinimum(1)
        self.settings_spd.setSingleStep(1);
        self.settings_spd.setValue(nextSongs.Config.songs_per_day)
        self.settings_ospd = QSpinBox()
        self.settings_ospd.setMinimum(0)
        self.settings_ospd.setSingleStep(1);
        self.settings_ospd.setValue(nextSongs.Config.old_songs_per_day)
        self.settings_mop = QSpinBox()
        self.settings_mop.setMinimum(1)
        self.settings_mop.setSingleStep(1);
        self.settings_mop.setValue(nextSongs.Config.middle_old_period)
        self.btn_save = QPushButton('Save')
        self.btn_save.clicked.connect(self.save_prefs)
        self.btn_exit = QPushButton('Cancel')
        self.btn_exit.clicked.connect(self.accept)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(QLabel("Songs per day: "))
        self.verticalLayout.addWidget(self.settings_spd)
        self.verticalLayout.addWidget(QLabel("Old songs per day: "))
        self.verticalLayout.addWidget(self.settings_ospd)
        self.verticalLayout.addWidget(QLabel("Interval to repeat all middle old songs: "))
        self.verticalLayout.addWidget(self.settings_mop)
        self.verticalLayout.addWidget(self.btn_save)
        self.verticalLayout.addWidget(self.btn_exit)

    def save_prefs(self, i):
        nextSongs.Config.songs_per_day = self.settings_spd.value()
        nextSongs.Config.old_songs_per_day = self.settings_ospd.value()
        nextSongs.Config.middle_old_period = self.settings_mop.value()
        nextSongs.Config.save_config()
        self.accept()


# Create a Qt application
app = QApplication(sys.argv)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
 
        # Our main window will be a QTableView
        self.table = QTableView()
        self.table.setWindowTitle('nextSongs')
        self.table.setMinimumSize(600, 400)
     
        # Create an empty model for the list's data
        self.model = QStandardItemModel(self.table)
        self.model.setHorizontalHeaderLabels(['Title', 'Date', 'Weight'])
        self.model.itemChanged.connect(self.on_item_changed)
        self.model.setColumnCount(3)

        # Fill table with data
        for song in st.songs:
            # create an item with a caption
            item = QSong(song)
         
            # add a checkbox to it
            item.setCheckable(True)
            if song.current:
                item.setCheckState(2)
         
            # Add the item to the model
            self.model.appendRow([item, QSongDate(song), QSongWeight(song)])
         
        # Apply the model to the list view
        self.table.setModel(self.model)

        # Create add button
        add_btn = QPushButton('Add Song')
        add_btn.clicked.connect(self.add_song)
        add_btn.resize(add_btn.sizeHint())

        # Create todays songs button
        todays_songs_btn = QPushButton('Todays Songs')
        todays_songs_btn.clicked.connect(show_todays_songs)
        todays_songs_btn.resize(todays_songs_btn.sizeHint())

        # Create delete button
        del_btn = QPushButton('Remove Song')
        del_btn.clicked.connect(self.delete_selected_song)
        del_btn.resize(del_btn.sizeHint())

        # Create exit button
        exit_btn = QPushButton('Exit')
        exit_btn.clicked.connect(sys.exit)
        exit_btn.resize(exit_btn.sizeHint())

        # Create open_prefs button
        open_prefs_btn = QPushButton('Open Preferences')
        open_prefs_btn.clicked.connect(show_preferences)
        open_prefs_btn.resize(open_prefs_btn.sizeHint())

        # fit column to content size
        self.table.resizeColumnsToContents()

        # Add widgets to layout
        layout.addWidget(todays_songs_btn)
        layout.addWidget(add_btn)
        layout.addWidget(del_btn)
        layout.addWidget(self.table)
        layout.addWidget(open_prefs_btn)
        layout.addWidget(exit_btn)
        # Show the window and run the app
        self.setLayout(layout)

    def delete_selected_song(self):
        if len(self.table.selectedIndexes()) == 0:
            return
        indices = [self.table.selectedIndexes()[0]]
        for i in indices:
            item = self.model.itemFromIndex(i)
            st.songs.remove(item.song)
            self.model.removeRow(i.row())
        self.table.resizeColumnsToContents()
        st.write_songs()

    def add_song(self):
        song = nextSongs.Song("Song Title", datetime.datetime.now().date())
        st.songs.append(song)
        item = QSong(song)

        item.setCheckable(True)
        if song.current:
            item.setCheckState(2)
        self.model.appendRow([item, QSongDate(song), QSongWeight(song)])
        self.table.resizeColumnsToContents()
        # Scroll table down, select inserted column and go into edit mode for first cell
        self.table.scrollToBottom()
        self.table.selectRow(self.model.rowCount() - 1)
        self.table.edit(self.table.selectedIndexes()[0])
        # save songs
        st.write_songs()

    def on_item_changed(self, item):
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
        elif isinstance(item, QSongWeight):
            try:
                new_weight = int(item.text())
                item.song.weight = new_weight
            except:
                item.setText(str(item.song.weight))
        st.write_songs()

def main():
    widget = MainWindow()
    widget.show()
    app.exec_()

if __name__ == "__main__":
    main()
