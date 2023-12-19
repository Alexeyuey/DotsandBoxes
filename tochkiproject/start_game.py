import sys
import sqlite3
from PyQt5 import uic
from main_game import DotsAndBoxes
from PyQt5.QtWidgets import QVBoxLayout, QGraphicsLineItem, QApplication, QMainWindow, QGraphicsScene, \
    QGraphicsView, QGraphicsEllipseItem, QDialog, QMessageBox, QWidget, QPushButton, QLabel, QGridLayout, QColorDialog, \
    QTableWidgetItem, QLineEdit, QGraphicsRectItem
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QTabletEvent
import numpy as np


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwin.ui', self)

        self.settingsbut.clicked.connect(self.go_set)
        self.exbut.clicked.connect(self.dialog_exit)
        self.startbut.clicked.connect(self.go_start)
        self.ratedbut.clicked.connect(self.go_rate)

    def go_start(self):
        self.gs = Players()
        self.gs.show()
        self.hide()

    def go_set(self):
        self.g = SetWin()
        self.g.show()
        self.hide()

    def go_rate(self):
        self.gr = TableRate()
        self.gr.show()
        self.hide()

    def dialog_exit(self, s):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Выйти?")
        dlg.setText("Вы действительно хотите выйти?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button == QMessageBox.Yes:
            window.show()
            sys.exit(app.exec_())


class Players(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('player1.ui', self)
        self.bd = sqlite3.connect("tabrate.db")
        self.pushButton.clicked.connect(self.player_name)
        self.count_clckd = 0
        self.player1 = None
        self.player2 = None

    def player_name(self):
        try:
            cur = self.bd.cursor()
            self.count_clckd += 1
            if self.count_clckd == 1:
                cur.execute("""SELECT name from ezrated""")
                if cur.fetchone():
                    cur.execute(f"INSERT INTO ezrated VALUES ('{self.lineEdit.text()}', '{0}')")
                    self.bd.commit()
                self.lineEdit.setText("")
            if self.count_clckd == 2:
                self.player2 = self.lineEdit.text()
                cur.execute("""SELECT name from bluerate""")
                if cur.fetchone():
                    cur.execute(f"INSERT INTO bluerate VALUES ('{self.lineEdit.text()}', '{0}')")
                    self.bd.commit()
                self.gs = DotsAndBoxes()
                self.gs.setGeometry(100, 100, self.gs.size_of_board + 100, self.gs.size_of_board + 100)
                self.gs.show()
                self.hide()
        except Exception as e:
            print(e)



class SetWin(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('setwin.ui', self)

        self.back.clicked.connect(self.back_set)
        self.volbut.clicked.connect(self.volset)

    def back_set(self):
        self.bs = MainMenu()
        self.bs.show()
        self.hide()

    def volset(self):
        pass

    def sizedesk(self):
        pass


class TableRate(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ratewin.ui', self)

        self.pushButton.clicked.connect(self.back_tr)

        self.bd = sqlite3.connect("tabrate.db")
        cur = self.bd.cursor()
        result = cur.execute(f"""
        SELECT name Player, max(score) Score from ezrated
        GROUP by name
        ORDER by score DESC
        limit 20
        """).fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

        resultt = cur.execute(f"""
                SELECT name Player, max(score) Score from bluerate
                GROUP by name
                ORDER by score DESC
                limit 20
                """).fetchall()
        for i, elem in enumerate(resultt):
            for j, val in enumerate(elem):
                self.tableWidget_2.setRowCount(len(resultt))
                self.tableWidget_2.setColumnCount(len(resultt[0]))
                self.tableWidget_2.setItem(i, j, QTableWidgetItem(str(val)))

    def back_tr(self):
        self.bs = MainMenu()
        self.bs.show()
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
