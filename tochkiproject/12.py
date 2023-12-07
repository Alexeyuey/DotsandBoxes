import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QGraphicsLineItem, QApplication, QMainWindow, QGraphicsScene, \
    QGraphicsView, QGraphicsEllipseItem, QDialog, QMessageBox, QWidget, QPushButton, QLabel, QGridLayout, QColorDialog
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtWidgets import QGraphicsRectItem
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
        self.gs = DotsAndBoxes()
        self.gs.setGeometry(100, 100, self.gs.size_of_board + 100, self.gs.size_of_board + 100)
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


class DotsAndBoxes(QWidget):
    def __init__(self, sizeboard):
        super().__init__()

        self.size_of_board = 600
        self.number_of_dots = 6
        self.symbol_size = (self.size_of_board / 3 - self.size_of_board / 8) / 2
        self.symbol_thickness = 50
        self.dot_color = '#7BC043'
        self.player1_color = '#0492CF'
        self.player1_color_light = '#67B0CF'
        self.player2_color = '#EE4035'
        self.player2_color_light = '#EE7E77'
        self.Green_color = '#7BC043'
        self.dot_width = 0.25 * self.size_of_board / self.number_of_dots
        self.edge_width = 0.1 * self.size_of_board / self.number_of_dots
        self.row_status = np.zeros(shape = (self.number_of_dots, self.number_of_dots))
        self.col_status = np.zeros(shape = (self.number_of_dots, self.number_of_dots))
        self.distance_between_dots = self.size_of_board / (self.number_of_dots)
        self.player1_starts = True

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dots and Boxes')

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing, True)

        self.view.mousePressEvent = lambda event: self.click(event)

        layout = QVBoxLayout()
        layout.addWidget(self.view)

        self.play_again_button = QPushButton('Play Again')
        self.play_again_button.clicked.connect(self.playAgain)
        layout.addWidget(self.play_again_button)

        self.turn_label = QLabel('Next turn: Player1', self)
        layout.addWidget(self.turn_label)

        self.setLayout(layout)

        self.playAgain()

    def playAgain(self):
        self.refreshBoard()
        self.board_status = np.zeros(shape = (self.number_of_dots - 1, self.number_of_dots - 1))
        self.row_status = np.zeros(shape = (self.number_of_dots, self.number_of_dots))
        self.col_status = np.zeros(shape = (self.number_of_dots, self.number_of_dots))

        self.player1_starts = not self.player1_starts
        self.player1_turn = not self.player1_starts
        self.reset_board = False
        self.turntext_handle = []

        self.already_marked_boxes = []
        self.display_turn_text()

        self.already_marked_boxes = []
        self.display_turn_text()

    def is_grid_occupied(self, logical_position, type):
        r = logical_position[0]
        c = logical_position[1]
        occupied = True

        if 0 <= c < self.number_of_dots and 0 <= r < self.number_of_dots:
            if type == 'row' and self.row_status[c][r] == 0:
                occupied = False
            elif type == 'col' and self.col_status[c][r] == 0:
                occupied = False

        return occupied

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        position = (grid_position - self.distance_between_dots / 4) // (self.distance_between_dots / 2)

        type = False
        logical_position = []
        if 0 <= position[1] < self.number_of_dots * 2 - 1 and 0 <= position[0] < self.number_of_dots * 2 - 1:
            if position[1] % 2 == 0 and (position[0] - 1) % 2 == 0:
                r = int((position[0] - 1) // 2)
                c = int(position[1] // 2)
                logical_position = [r, c]
                type = 'row'
            elif position[0] % 2 == 0 and (position[1] - 1) % 2 == 0:
                c = int((position[1] - 1) // 2)
                r = int(position[0] // 2)
                logical_position = [r, c]
                type = 'col'

        return logical_position, type

    def mark_box(self):
        boxes = np.argwhere(self.board_status == -4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) != []:
                self.already_marked_boxes.append(list(box))
                color = self.player1_color_light
                self.shade_box(box, color)

        boxes = np.argwhere(self.board_status == 4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) != []:
                self.already_marked_boxes.append(list(box))
                color = self.player2_color_light
                self.shade_box(box, color)

    def update_board(self, type, logical_position):
        r = logical_position[0]
        c = logical_position[1]
        val = 1
        if self.player1_turn:
            val = -1

        if c < (self.number_of_dots - 1) and r < (self.number_of_dots - 1):
            self.board_status[c][r] += val

        if type == 'row':
            self.row_status[c][r] = 1
            if c >= 1 and r < (self.number_of_dots - 1):
                self.board_status[c - 1][r] += val

        elif type == 'col':
            self.col_status[c][r] = 1
            if r >= 1 and c < (self.number_of_dots - 1):
                self.board_status[c][r - 1] += val

    def is_gameover(self):
        total_edges = (self.number_of_dots - 1) * 2
        current_sum = np.sum(np.abs(self.board_status))
        print(f"Current sum of board_status: {current_sum}, Total edges: {total_edges}")
        return current_sum == total_edges

    def make_edge(self, type, logical_position):
        if type == 'row':
            start_x = self.distance_between_dots / 2 + logical_position[0] * self.distance_between_dots
            end_x = start_x + self.distance_between_dots
            start_y = self.distance_between_dots / 2 + logical_position[1] * self.distance_between_dots
            end_y = start_y
        elif type == 'col':
            start_y = self.distance_between_dots / 2 + logical_position[1] * self.distance_between_dots
            end_y = start_y + self.distance_between_dots
            start_x = self.distance_between_dots / 2 + logical_position[0] * self.distance_between_dots
            end_x = start_x

        if self.player1_turn:
            color = self.player1_color
        else:
            color = self.player2_color

        edge_item = QGraphicsLineItem(start_x, start_y, end_x, end_y)
        pen = QPen(QColor(color))
        pen.setWidth(int(self.edge_width))
        edge_item.setPen(pen)

        edge_item.setZValue(1)

        self.scene.addItem(edge_item)

    def make_edge(self, type, logical_position):
        if type == 'row':
            start_x = self.distance_between_dots / 2 + logical_position[0] * self.distance_between_dots
            end_x = start_x + self.distance_between_dots
            start_y = self.distance_between_dots / 2 + logical_position[1] * self.distance_between_dots
            end_y = start_y
        elif type == 'col':
            start_y = self.distance_between_dots / 2 + logical_position[1] * self.distance_between_dots
            end_y = start_y + self.distance_between_dots
            start_x = self.distance_between_dots / 2 + logical_position[0] * self.distance_between_dots
            end_x = start_x

        if self.player1_turn:
            color = self.player1_color
        else:
            color = self.player2_color

        edge_item = QGraphicsLineItem(start_x, start_y, end_x, end_y)
        pen = QPen(QColor(color))
        pen.setWidth(int(self.edge_width))
        edge_item.setPen(pen)

        edge_item.setZValue(1)

        self.scene.addItem(edge_item)

    def display_gameover(self):
        player1_score = len(np.argwhere(self.board_status == -4))
        player2_score = len(np.argwhere(self.board_status == 4))

        if player1_score > player2_score:
            text = 'Winner: Player 1 '
            color = self.player1_color
        elif player2_score > player1_score:
            text = 'Winner: Player 2 '
            color = self.player2_color
        else:
            text = 'It\'s a tie'
            color = 'gray'

        self.scene.clear()
        self.scene.addText(text, QFont('cmr', 60, QFont.Bold)).setDefaultTextColor(QColor(color))

        score_text = 'Scores \n'
        self.scene.addText(score_text, QFont('cmr', 40, QFont.Bold)).setDefaultTextColor(QColor(self.Green_color))

        score_text = 'Player 1 : ' + str(player1_score) + '\n'
        score_text += 'Player 2 : ' + str(player2_score) + '\n'
        self.scene.addText(score_text, QFont('cmr', 30, QFont.Bold)).setDefaultTextColor(QColor(self.Green_color))

        self.reset_board = True

        score_text = 'Click "Play Again" to play again \n'
        self.scene.addText(score_text, QFont('cmr', 20, QFont.Bold)).setDefaultTextColor(QColor('gray'))

    def refreshBoard(self):
        for i in range(self.number_of_dots):
            x = i * self.distance_between_dots + self.distance_between_dots / 2
            self.scene.addLine(x, self.distance_between_dots / 2, x,
                               self.size_of_board - self.distance_between_dots / 2,
                               QPen(QColor('gray'), self.dot_width))

            self.scene.addLine(self.distance_between_dots / 2, x,
                               self.size_of_board - self.distance_between_dots / 2, x,
                               QPen(QColor('gray'), self.dot_width))

        for i in range(self.number_of_dots):
            for j in range(self.number_of_dots):
                start_x = i * self.distance_between_dots + self.distance_between_dots / 2
                end_x = j * self.distance_between_dots + self.distance_between_dots / 2

                dot_item = QGraphicsEllipseItem(start_x - self.dot_width / 2, end_x - self.dot_width / 2,
                                                self.dot_width, self.dot_width)
                dot_item.setBrush(QColor(self.dot_color))
                self.scene.addItem(dot_item)

    def display_turn_text(self):
        text = 'Next turn: '
        if self.player1_turn:
            text += 'Player1'
            color = self.player1_color
        else:
            text += 'Player2'
            color = self.player2_color

        self.turn_label.setText(text)
        self.turn_label.setStyleSheet(f'color: {color}')

    def shade_box(self, box, color):
        start_x = self.distance_between_dots / 2 + box[1] * self.distance_between_dots
        start_y = self.distance_between_dots / 2 + box[0] * self.distance_between_dots
        end_x = start_x + self.distance_between_dots
        end_y = start_y + self.distance_between_dots

        box_item = QGraphicsRectItem(start_x, start_y, end_x - start_x, end_y - start_y)
        box_item.setBrush(QColor(color))
        self.scene.addItem(box_item)

    def click(self, event):
        if not self.reset_board:
            grid_position = [event.x(), event.y()]
            logical_position, valid_input = self.convert_grid_to_logical_position(grid_position)

            if 0 <= logical_position[0] < self.number_of_dots and 0 <= logical_position[1] < self.number_of_dots:
                if valid_input and not self.is_grid_occupied(logical_position, valid_input):
                    self.update_board(valid_input, logical_position)
                    self.make_edge(valid_input, logical_position)
                    self.mark_box()
                    self.refreshBoard()
                    self.player1_turn = not self.player1_turn

                    if self.is_gameover():
                        self.display_gameover()
                    else:
                        self.display_turn_text()

    def click(self, event):
        if not self.reset_board:
            grid_position = [event.x(), event.y()]
            logical_position, valid_input = self.convert_grid_to_logical_position(grid_position)
            if 0 <= grid_position[0] <= self.size_of_board and 0 <= grid_position[1] <= self.size_of_board:
                if valid_input and not self.is_grid_occupied(logical_position, valid_input):
                    self.update_board(valid_input, logical_position)
                    self.make_edge(valid_input, logical_position)
                    self.mark_box()
                    self.refreshBoard()
                    self.player1_turn = not self.player1_turn

                    if self.is_gameover():
                        self.display_gameover()
                    else:
                        self.display_turn_text()

    def mousePressEvent(self, event):
        if not self.reset_board:
            grid_position = [event.x(), event.y()]
            logical_position, valid_input = self.convert_grid_to_logical_position(grid_position)
            if valid_input and not self.is_grid_occupied(logical_position, valid_input):
                self.update_board(valid_input, logical_position)
                self.make_edge(valid_input, logical_position)
                self.mark_box()
                self.refreshBoard()
                self.player1_turn = not self.player1_turn

                if self.is_gameover():
                    self.display_gameover()
                else:
                    self.display_turn_text()
        else:
            self.scene.clear()
            self.playAgain()
            self.reset_board = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
