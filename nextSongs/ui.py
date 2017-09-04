from PyQt5.QtCore import QVariant
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import *
from dateutil.relativedelta import relativedelta
import PyQt5.Qt as Qt
import datetime
import nextSongs.nextSongs as nextSongs
import os
import subprocess
import sys

nextSongs.Config.read_config()
st = nextSongs.SongTimer()
st.read_songs()

class QSong(QStandardItem):
    """
    QStandardItem that represents the Song title in the Song Table
    """
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setText(song.title)

class QSongDate(QStandardItem):
    """
    QStandardItem that represents the Song date in the Song Table
    """
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setText(str(song.date))

class QSongWeight(QStandardItem):
    """
    QStandardItem that represents the Song weight in the Song Table
    """
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setText(str(song.weight))

class QSongLocation(QStandardItem):
    """
    QStandardItem that represents the Song location in the Song Table
    """
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setText(str(song.location))

class QSongFilepath(QStandardItem):
    """
    QStandardItem that lets the user open a file that is defined in song.filepath
    """
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setEditable(False)
        self.setText(self.text())

    def update_text(self):
        self.setText(self.text())

    def text(self):
        if self.song.filepath != "":
            return 'open'
        else:
            ''

class QSongForceMiddleCat(QStandardItem):
    """
    Checkbox that enables/disables enforce_middle_old_category for a song in the Song Table
    """
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setEditable(False)
        self.setCheckable(True)
        if song.enforce_middle_aged_category:
            self.setCheckState(2)
        else:
            self.setCheckState(0)

class QSongCategory(QStandardItem):
    """
    QStandardItem that shows the category of a song in the song table
    """
    def __init__(self,song):
        super().__init__()
        self.song = song
        self.setEditable(False)
        # self.setCheckable(False)
        self.update_text()

    def update_text(self):
        self.setText(self.text())

    def text(self):
        if self.song.current:
            return "Current"
        for i in range(0, nextSongs.Config.middle_old_period):
            if self.song in st.get_middle_old_songs_by_slot(i):
                return "Middle; Day " + str(i + 1)
        else:
            return "Old"





def show_todays_songs():
    """
    open Todays_Songs dialog
    """
    todays_songs = Todays_Songs()
    todays_songs.exec_()

class Todays_Songs(QDialog):
    """
    This dialog shows a list of songs to practice this day
    """
    def __init__(self):
        super().__init__()
        list_popup = QTableView()
        list_popup.setWindowTitle('Todays songs')
        list_popup.setMinimumSize(600, 400)
        self.model = QStandardItemModel(list_popup)
        self.model.setHorizontalHeaderLabels(['Title', 'Location', 'File'])
        for song in st.get_songs_for_date(datetime.datetime.now()):
            item = QSong(song)
            item.setEditable(False)
            item2 = QSongLocation(song)
            item2.setEditable(False)
            item3 = QSongFilepath(song)
            item3.setEditable(False)
            self.model.appendRow([item, item2, item3])
        list_popup.setModel(self.model)
        list_popup.doubleClicked.connect(self.open_filepath)
        list_popup.resizeColumnsToContents()

        exit_btn = QPushButton('Exit')
        exit_btn.clicked.connect(self.accept)
        self.list_popup = list_popup
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.list_popup)
        self.verticalLayout.addWidget(exit_btn)

    def open_filepath(self, index):
        item = self.model.itemFromIndex(index)
        if not isinstance(item, QSongFilepath):
            return
        if item.song.filepath == "":
            return
        if sys.platform == 'linux':
            subprocess.call(["xdg-open", item.song.filepath])
        else:
            os.startfile(item.song.filepath)


class Preferences(QDialog):
    """
    Preferences Dialog
    """
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
        """
        apply configured prefereces and save them to config file
        """
        nextSongs.Config.songs_per_day = self.settings_spd.value()
        nextSongs.Config.old_songs_per_day = self.settings_ospd.value()
        nextSongs.Config.middle_old_period = self.settings_mop.value()
        nextSongs.Config.save_config()
        self.accept()


# Create a Qt application
app = QApplication(sys.argv)

class ListWindow(QWidget):
    """
    Window that holds the song list and the buttons to add, remove a song and show todays song
    """
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
 
        # Our main window will be a QTableView
        self.table = QTableView()
        self.table.setMinimumSize(600, 400)
     
        # Create an empty model for the list's data
        self.model = QStandardItemModel(self.table)
        self.model.setHorizontalHeaderLabels(['Title', 'Date', 'Weight', 'Location', 'Force middle old', 'Category', 'File'])
        self.model.itemChanged.connect(self.on_item_changed)
        self.table.doubleClicked.connect(self.open_filepath)
        self.model.setColumnCount(7)

        # Fill table with data
        for song in st.songs:
            # create an item with a caption
            item = QSong(song)
         
            # add a checkbox to it
            item.setCheckable(True)
            if song.current:
                item.setCheckState(2)
         
            # Add the item to the model
            self.model.appendRow([item, QSongDate(song), QSongWeight(song), QSongLocation(song), QSongForceMiddleCat(song), QSongCategory(song), QSongFilepath(song)])
         
        # Apply the model to the list view
        self.table.setModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(1, 1)

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

        # fit column to content size
        self.table.resizeColumnsToContents()

        # Add widgets to layout
        layout.addWidget(todays_songs_btn)
        layout.addWidget(add_btn)
        layout.addWidget(del_btn)
        layout.addWidget(self.table)
        # Show the window and run the app
        self.setLayout(layout)

    def open_filepath(self, index):
        item = self.model.itemFromIndex(index)
        if not isinstance(item, QSongFilepath):
            return
        if item.song.filepath == "":
            return
        if sys.platform == 'linux':
            subprocess.call(["xdg-open", item.song.filepath])
        else:
            os.startfile(item.song.filepath)

    def set_filepath(self):
        """
        opens a dialog to ask for filepath of selected song and sets it
        """
        if len(self.table.selectedIndexes()) == 0:
            return
        fname = QFileDialog.getOpenFileName(self, 'Open file', 
                         os.path.expanduser('~'), "All (*.*)")[0]
        if fname == "":
            return
        indices = [self.table.selectedIndexes()[0]]
        for index in indices:
            item = self.model.itemFromIndex(index)
            item.song.filepath = fname
        self.table.resizeColumnsToContents()
        self.update_categories()
        st.write_songs()

    def remove_filepath(self):
        """
        removes the filepath attribute from a selected song
        """
        if len(self.table.selectedIndexes()) == 0:
            return
        indices = [self.table.selectedIndexes()[0]]
        for index in indices:
            item = self.model.itemFromIndex(index)
            item.song.filepath = ""
        self.table.resizeColumnsToContents()
        self.update_categories()
        st.write_songs()


    def delete_selected_song(self):
        """
        deletes the first selected song
        """
        if len(self.table.selectedIndexes()) == 0:
            return
        indices = [self.table.selectedIndexes()[0]]
        for i in indices:
            item = self.model.itemFromIndex(i)
            st.songs.remove(item.song)
            self.model.removeRow(i.row())
        self.table.resizeColumnsToContents()
        st.write_songs()
        self.update_categories()

    def add_song(self):
        """
        Adds a new song element to the table
        """
        song = nextSongs.Song("Song Title", datetime.datetime.now().date())
        st.songs.append(song)
        item = QSong(song)
        item_middle_aged_cb = QSongForceMiddleCat(song)
        item_middle_aged_cb.setCheckable(True)

        item.setCheckable(True)
        if song.current:
            item.setCheckState(2)
        self.model.appendRow([item, QSongDate(song), QSongWeight(song), QSongLocation(song), item_middle_aged_cb, QSongCategory(song), QSongFilepath(song)])
        self.table.resizeColumnsToContents()
        # Scroll table down, select inserted column and go into edit mode for first cell
        self.table.scrollToBottom()
        self.table.selectRow(self.model.rowCount() - 1)
        self.table.edit(self.table.selectedIndexes()[0])
        # save songs
        st.write_songs()
        self.update_categories()

    def on_item_changed(self, item):
        """
        callback function to update song items according to the change that happened
        """
        if isinstance(item, QSong):
            # change song title and its current-state
            item.song.title = item.text()
            item.song.current = item.checkState()
        elif isinstance(item, QSongDate):
            # try to change date of the song. if it fails, reset to old date
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
            # try to change weight of a song. otherwise reset to old weight
            try:
                new_weight = int(item.text())
                item.song.weight = new_weight
            except:
                item.setText(str(item.song.weight))
        elif isinstance(item, QSongLocation):
            # change location of a song
            item.song.location = item.text()
        elif isinstance(item, QSongForceMiddleCat):
            # change enforce_middle_aged_category of a song
            item.song.enforce_middle_aged_category = item.checkState()
        # save changes to file
        st.write_songs()

        # update categories
        self.update_categories()

    def update_categories(self):
        """
        updates category text of all songs in the table
        """
        for i in range(self.model.rowCount()):
            for j in range(self.model.columnCount()):
                cell = self.model.itemFromIndex(self.model.index(i,j))
                if hasattr(cell, 'update_text'):
                    cell.update_text()
                if isinstance(cell, QSongCategory):
                    cell.update_text()




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def get_icon_path(self):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, 'icons', 'icon.png')

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('nextSongs')
        self.setWindowIcon(QIcon(self.get_icon_path()))

        self.list = ListWindow()
        self.setCentralWidget(self.list)

        # Exit Action
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        # Print Action
        printAct = QAction(QIcon('print.png'), '&Print', self)
        printAct.setShortcut('Ctrl+P')
        printAct.setStatusTip('Print training set')
        printAct.triggered.connect(self.show_print_dialog)

        # Show Preferences Action
        prefAct = QAction(QIcon('preferences.png'), '&Preferences', self)
        prefAct.setShortcut('Ctrl+S')
        prefAct.triggered.connect(self.show_preferences)

        # Set Filepath for selected song Action
        filepathSetAction = QAction(QIcon('filepath.png'), '&Set Fielpath', self)
        filepathSetAction.setShortcut('Ctrl+F')
        filepathSetAction.triggered.connect(self.list.set_filepath)

        # Remove Filepath for selected song action
        filepathRemoveAction = QAction(QIcon('filepath.png'), '&Remove Fielpath', self)
        filepathRemoveAction.setShortcut('Ctrl+R')
        filepathRemoveAction.triggered.connect(self.list.remove_filepath)

        # Menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(prefAct)
        fileMenu.addAction(printAct)
        fileMenu.addAction(exitAct)
        songMenu = menubar.addMenu('&Song')
        songMenu.addAction(filepathSetAction)
        songMenu.addAction(filepathRemoveAction)

        self.show()

    def show_print_dialog(self):
        """
        opens a dialog to ask for how many days we want to print training sets.
        then generates the content that will be printed.
        Finally opens the dialog to print this content
        """
        item, ok = QInputDialog.getInt(self, "Days to print", "How many days should be printed?", 7)
        if not item or not ok:
            return
        days = item
        doc = QTextDocument()
        cursor = QTextCursor(doc)
        cursor.insertHtml("<h1>Training Set: " + str(datetime.datetime.now().date()) + " - " + str(datetime.datetime.now().date() + relativedelta(days=+days-1)) + "</h1><p>")
        cursor.insertHtml(self.generate_printable_html_table(days))
        printer = QPrinter()
        def handlePaintRequest(printer):
            doc.print_(printer)
        dialog = QPrintPreviewDialog(printer)
        dialog.paintRequested.connect(handlePaintRequest)
        dialog.exec_()

    def generate_printable_html_table(self, days):
        """
        generates the html table that will be printed.
        :param days: int; for how many days shall a traing set be generated
        """
        exclude_old_songs = []
        table = "<table style='padding-right: 10px;'>'"
        for i in range(days):
            date = datetime.datetime.now().date() + relativedelta(days=+i)
            table += "<tr><td>" + str(date) + ":</td></tr>"
            songs_for_day =  st.get_songs_for_date(datetime.datetime.now().date() + relativedelta(days=+i), exclude_old_songs)
            exclude_old_songs.extend(songs_for_day)
            # reset exclude_old_songs for next day if all old songs were played
            reset_day = int(len(st.get_old_songs()) / nextSongs.Config.old_songs_per_day)
            if (i + 1) % reset_day == 0:
                exclude_old_songs = []
            for song in songs_for_day:
                table += "<tr><td></td><td>" + song.location + "<td></td><td></td><td>" + song.title + '</td></tr>'
        return table

    def show_preferences(self):
        """
        opens preferences dialog and updates category texts in the table afterwards
        """
        prefs = Preferences()
        prefs.exec_()
        self.list.update_categories()


def main():
    widget = MainWindow()
    app.exec_()

if __name__ == "__main__":
    main()
