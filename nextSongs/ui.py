import nextSongs.nextSongs as nextSongs
from dateutil.relativedelta import relativedelta
import datetime
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from PyQt5.QtPrintSupport import *
import PyQt5.Qt as Qt

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

class QSongLocation(QStandardItem):
    def __init__(self, song):
        super().__init__()
        self.song = song
        self.setText(str(song.location))

class QSongForceMiddleCat(QStandardItem):
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
            if self.song in st.get_middle_aged_songs_by_slot(i):
                return "Middle; Day " + str(i + 1)
        else:
            return "Old"





def show_todays_songs():
    todays_songs = Todays_Songs()
    todays_songs.exec_()

class Todays_Songs(QDialog):
    def __init__(self):
        super().__init__()
        list_popup = QTableView()
        list_popup.setWindowTitle('Todays songs')
        list_popup.setMinimumSize(600, 400)
        model = QStandardItemModel(list_popup)
        model.setHorizontalHeaderLabels(['Title', 'Location'])
        for song in st.get_songs_for_date(datetime.datetime.now()):
            item = QSong(song)
            item.setEditable(False)
            item2 = QSongLocation(song)
            item2.setEditable(False)
            model.appendRow([item, item2])
        list_popup.setModel(model)
        list_popup.resizeColumnsToContents()

        exit_btn = QPushButton('Exit')
        exit_btn.clicked.connect(self.accept)
        self.list_popup = list_popup
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.list_popup)
        self.verticalLayout.addWidget(exit_btn)


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

class ListWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
 
        # Our main window will be a QTableView
        self.table = QTableView()
        self.table.setMinimumSize(600, 400)
     
        # Create an empty model for the list's data
        self.model = QStandardItemModel(self.table)
        self.model.setHorizontalHeaderLabels(['Title', 'Date', 'Weight', 'Location', 'Force middle old', 'Category'])
        self.model.itemChanged.connect(self.on_item_changed)
        self.model.setColumnCount(6)

        # Fill table with data
        for song in st.songs:
            # create an item with a caption
            item = QSong(song)
         
            # add a checkbox to it
            item.setCheckable(True)
            if song.current:
                item.setCheckState(2)
         
            # Add the item to the model
            self.model.appendRow([item, QSongDate(song), QSongWeight(song), QSongLocation(song), QSongForceMiddleCat(song), QSongCategory(song)])
         
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
        self.update_categories()

    def add_song(self):
        song = nextSongs.Song("Song Title", datetime.datetime.now().date())
        st.songs.append(song)
        item = QSong(song)
        item_middle_aged_cb = QSongForceMiddleCat(song)
        item_middle_aged_cb.setCheckable(True)

        item.setCheckable(True)
        if song.current:
            item.setCheckState(2)
        self.model.appendRow([item, QSongDate(song), QSongWeight(song), QSongLocation(song), item_middle_aged_cb, QSongCategory(song)])
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
        elif isinstance(item, QSongLocation):
            item.song.location = item.text()
        elif isinstance(item, QSongForceMiddleCat):
            item.song.enforce_middle_aged_category = item.checkState()
        st.write_songs()

        # update categories
        self.update_categories()

    def update_categories(self):
        for i in range(self.model.rowCount()):
            for j in range(self.model.columnCount()):
                cell = self.model.itemFromIndex(self.model.index(i,j))
                if isinstance(cell, QSongCategory):
                    cell.update_text()




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('nextSongs')

        self.list = ListWindow()
        self.setCentralWidget(self.list)

        # Menu
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        printAct = QAction(QIcon('print.png'), '&Print', self)
        printAct.setShortcut('Ctrl+P')
        printAct.setStatusTip('Print trainingset')
        printAct.triggered.connect(self.show_print_dialog)

        prefAct = QAction(QIcon('preferences.png'), '&Preferences', self)
        prefAct.setShortcut('Ctrl+S')
        prefAct.triggered.connect(self.show_preferences)
        

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(prefAct)
        fileMenu.addAction(printAct)
        fileMenu.addAction(exitAct)

        self.show()

    def show_print_dialog(self):
        item, ok = QInputDialog.getInt(self, "Days to print", "How many days should be printed?", 7)
        if not item or not ok:
            return
        days = item
        doc = QTextDocument()
        cursor = QTextCursor(doc)
        cursor.insertHtml("<h1>Trainingset: " + str(datetime.datetime.now().date()) + " - " + str(datetime.datetime.now().date() + relativedelta(days=+days-1)) + "</h1><p>")
        cursor.insertHtml(self.generate_printable_html_table(days))
        printer = QPrinter()
        def handlePaintRequest(printer):
            doc.print_(printer)
        dialog = QPrintPreviewDialog(printer)
        dialog.paintRequested.connect(handlePaintRequest)
        dialog.exec_()

    def generate_printable_html_table(self, days):
        table = "<table style='padding-right: 10px;'>'"
        for i in range(days):
            date = datetime.datetime.now().date() + relativedelta(days=+i)
            table += "<tr><td>" + str(date) + ":</td></tr>"
            for song in st.get_songs_for_date(datetime.datetime.now().date() + relativedelta(days=+i)):
                table += "<tr><td></td><td>" + song.location + "<td></td><td></td><td>" + song.title + '</td></tr>'
            # table += '\n'
        return table

    def show_preferences(self):
        prefs = Preferences()
        prefs.exec_()
        self.list.update_categories()

def main():
    widget = MainWindow()
    app.exec_()

if __name__ == "__main__":
    main()
