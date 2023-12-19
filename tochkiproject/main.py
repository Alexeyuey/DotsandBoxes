import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QGraphicsLineItem, QApplication, QMainWindow, QGraphicsScene, \
    QGraphicsView, QGraphicsEllipseItem, QDialog, QMessageBox, QWidget, QPushButton, QLabel, QGridLayout, QColorDialog, \
    QTableWidgetItem, QLineEdit
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QTabletEvent
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


class DotsAndBoxes(QWidget):
    def __init__(self):
        super().__init__()
        self.bd = sqlite3.connect("tabrate.db")
        self.size_of_board = 600
        self.number_of_dots = 6
        self.symbol_size = (self.size_of_board / 3 - self.size_of_board / 8) / 2
        self.dot_color = '#7BC043'
        self.player1_color = '#0492CF'
        self.player1_color_light = '#0492CF'
        self.player2_color = '#EE4035'
        self.player2_color_light = '#EE7E77'
        self.Green_color = '#7BC043'
        self.dot_width = 0.25 * self.size_of_board / self.number_of_dots
        self.edge_width = 0.1 * self.size_of_board / self.number_of_dots
        self.row_status = np.zeros((self.number_of_dots, self.number_of_dots))
        self.col_status = np.zeros((self.number_of_dots, self.number_of_dots))
        self.distance_between_dots = self.size_of_board / (self.number_of_dots)
        self.player1_score = 0
        self.player2_score = 0
        self.additional_move_condition_player1 = False
        self.additional_move_condition_player2 = False
        self.player1_starts = True

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dots and Boxes')

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        # можно убрать, чистый визуал
        # self.view.setRenderHint(QPainter.Antialiasing, True)

        cur = self.bd.cursor()

        self.mouse_click = lambda event: self.click(event)

        layout = QVBoxLayout()
        layout.addWidget(self.view)

        self.turn_label = QLabel(
            f'Следующий ход: Игрок 1',
            self)
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

    def check_box_closed(self, box):
        # Логика для проверки, был ли квадрат закрыт
        r, c = box
        return (
                self.row_status[r][c] == 1
                and self.col_status[r][c] == 1
                and self.row_status[r + 1][c] == 1
                and self.col_status[r][c + 1] == 1
        )

    def mark_box(self):
        boxes = np.argwhere(self.board_status == -4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) != []:
                self.already_marked_boxes.append(list(box))
                color = self.player1_color_light
                self.shade_box(box, color)

                # Проверка, был ли закрыт квадрат и начисление очка
                if self.check_box_closed(box):
                    self.player1_score += 1  # Игрок 1 получил очко
                    self.additional_move_condition_player1 = True  # Установка флага для дополнительного хода

        boxes = np.argwhere(self.board_status == 4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) != []:
                self.already_marked_boxes.append(list(box))
                color = self.player2_color_light
                self.shade_box(box, color)

                if self.check_box_closed(box):
                    if self.player1_turn:
                        self.player1_score += 1  # Игрок 1 получил очко
                        self.additional_move_condition_player1 = True  # Установка флага для дополнительного хода
                    else:
                        self.player2_score += 1  # Игрок 2 получил очко
                        self.additional_move_condition_player2 = True  # Установка флага для дополнительного хода

                        # Проверка, был ли последний закрытый квадрат
                        if self.is_last_box_closed():
                            self.player1_turn = not self.player1_turn  # Смена хода после последнего закрытого квадрата
                            self.display_turn_text()  # Обновление отображения текущего хода

                            # Определение координат последнего закрытого квадрата
                            last_closed_box_coords = self.get_last_closed_box_coords()
                            if last_closed_box_coords:
                                # Закрашивание последнего закрытого квадрата в цвет текущего игрока
                                self.shade_box(last_closed_box_coords, self.get_current_player_color())

    def get_current_player_color(self):
        # Получение цвета текущего игрока
        return self.player1_color if self.player1_turn else self.player2_color

    def is_last_box_closed(self):
        # Проверка, был ли последний закрытый квадрат
        return np.all(self.board_status != 0)  # Возвращает True, если нет открытых квадратов

    def get_last_closed_box_coords(self):
        # Получение координат последнего закрытого квадрата
        return np.argwhere(self.board_status == 4 if self.player1_turn else -4)[0]

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
        for i in range(self.number_of_dots - 1):
            for j in range(self.number_of_dots - 1):
                if (
                        self.row_status[i][j] == 0
                        or self.col_status[i][j] == 0
                        or self.row_status[i + 1][j] == 0
                        or self.col_status[i][j + 1] == 0
                ):
                    return False
        return True

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
            cur = self.bd.cursor()
            text = 'Игрок 1 выиграл! '
            color = self.player1_color
            cur.execute("""SELECT name from ezrated""")
            pl1_last = cur.execute('SELECT name FROM ezrated ORDER BY id DESC LIMIT 1')
            if cur.fetchone():
                cur.execute(f"INSERT INTO ezrated VALUES ('{pl1_last}', '{player1_score}')")
                self.bd.commit()
        elif player2_score > player1_score:
            cur = self.bd.cursor()
            text = 'Игрок 2 Выиграл! '
            color = self.player2_color
            cur.execute("""SELECT name from bluerate""")
            pl2_last = cur.execute('SELECT name FROM bluerate ORDER BY id DESC LIMIT 1')
            if cur.fetchone():
                cur.execute(f"INSERT INTO ezrated VALUES ('{pl2_last}', '{player2_score}')")
                self.bd.commit()
        else:
            text = 'Ничья :('
            color = 'gray'

        self.scene.clear()
        self.scene.addText(text, QFont('cmr', 60, QFont.Bold)).setDefaultTextColor(QColor(color))

        score_text = 'Scores \n'
        self.scene.addText(score_text, QFont('cmr', 40, QFont.Bold)).setDefaultTextColor(QColor(self.Green_color))

        score_text = 'Player 1 : ' + str(player1_score) + '\n'
        score_text += 'Player 2 : ' + str(player2_score) + '\n'
        self.scene.addText(score_text, QFont('cmr', 30, QFont.Bold)).setDefaultTextColor(QColor(self.Green_color))

        self.reset_board = True

        score_text = 'Чтобы начать еще раз - нажмите кнопку "Играть еще раз" \n'
        self.scene.addText(score_text, QFont('cmr', 10, QFont.Bold)).setDefaultTextColor(QColor('gray'))


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
        text = 'Следующий ход: '
        if self.player1_turn:
            text += 'Игрок 1'
            color = self.player1_color
        else:
            text += 'Игрок 2'
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

                        # Дополнительный ход при получении очка
                        if self.additional_move_condition():
                            self.additional_move()

    def additional_move_condition(self):
        if self.additional_move_condition_player1 and self.player1_turn:
            return True
        elif self.additional_move_condition_player2 and not self.player1_turn:
            return True
        return False

    def additional_move(self):
        # дополнительный ход, если успею
        pass

    def reset_additional_move_flags(self):
        # сброс флага после доп хода
        self.additional_move_condition_player1 = False
        self.additional_move_condition_player2 = False

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
