from PyQt5.QtWidgets import QVBoxLayout, QGraphicsLineItem, QApplication, QMainWindow, QGraphicsScene, \
    QGraphicsView, QGraphicsEllipseItem, QDialog, QMessageBox, QWidget, QPushButton, QLabel, QGridLayout, QColorDialog, \
    QTableWidgetItem, QLineEdit, QGraphicsRectItem
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QTabletEvent
import sqlite3
import numpy as np


class DotsAndBoxes(QWidget):
    def __init__(self):
        super().__init__()
        self.bd = sqlite3.connect("tabrate.db")
        self.board_size = 600
        self.quantity_dots = 6
        self.symbol_size = (self.board_size / 3 - self.board_size / 8) / 2
        self.dot_color = '#000000'
        self.player1_color = '#0000FF'
        self.player1_color_light = '#00008B'
        self.player2_color = '#FF0000'
        self.player2_color_light = '#DC143C'
        self.Green_color = '#7BC043'
        self.dot_width = 0.25 * self.board_size / self.quantity_dots
        self.edge_width = 0.1 * self.board_size / self.quantity_dots
        self.row_status = np.zeros((self.quantity_dots, self.quantity_dots))
        self.col_status = np.zeros((self.quantity_dots, self.quantity_dots))
        self.dots_space = self.board_size / (self.quantity_dots)
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

        self.replay()

    def replay(self):
        self.refreshBoard()
        self.board_status = np.zeros(shape = (self.quantity_dots - 1, self.quantity_dots - 1))
        self.row_status = np.zeros(shape = (self.quantity_dots, self.quantity_dots))
        self.col_status = np.zeros(shape = (self.quantity_dots, self.quantity_dots))

        self.player1_starts = not self.player1_starts
        self.player1_turn = not self.player1_starts
        self.reset_board = False
        self.turntext_handle = []

        self.already_marked_boxes = []
        self.screen_motion()

        self.already_marked_boxes = []
        self.screen_motion()

    def is_grid_occupied(self, logical_position, type):
        r = logical_position[0]
        c = logical_position[1]
        occupied = True

        if 0 <= c < self.quantity_dots and 0 <= r < self.quantity_dots:
            if type == 'row' and self.row_status[c][r] == 0:
                occupied = False
            elif type == 'col' and self.col_status[c][r] == 0:
                occupied = False

        return occupied

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        position = (grid_position - self.dots_space / 4) // (self.dots_space / 2)

        type = False
        logical_position = []
        if 0 <= position[1] < self.quantity_dots * 2 - 1 and 0 <= position[0] < self.quantity_dots * 2 - 1:
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
                    self.player1_score += 1
                    self.additional_move_condition_player1 = True  # Установка флага для дополнительного хода

        boxes = np.argwhere(self.board_status == 4)
        for box in boxes:
            if list(box) not in self.already_marked_boxes and list(box) != []:
                self.already_marked_boxes.append(list(box))
                color = self.player2_color_light
                self.shade_box(box, color)

                if self.check_box_closed(box):
                    if self.player1_turn:
                        self.player1_score += 1
                        self.additional_move_condition_player1 = True  # Установка флага для дополнительного хода
                    else:
                        self.player2_score += 1
                        self.additional_move_condition_player2 = True  # Установка флага для дополнительного хода

                        # Проверка, был ли последний закрытый квадрат
                        if self.is_last_box_closed():
                            self.player1_turn = not self.player1_turn  # Смена хода после последнего закрытого квадрата
                            self.screen_motion()  # Обновление отображения текущего хода

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

        if c < (self.quantity_dots - 1) and r < (self.quantity_dots - 1):
            self.board_status[c][r] += val

        if type == 'row':
            self.row_status[c][r] = 1
            if c >= 1 and r < (self.quantity_dots - 1):
                self.board_status[c - 1][r] += val

        elif type == 'col':
            self.col_status[c][r] = 1
            if r >= 1 and c < (self.quantity_dots - 1):
                self.board_status[c][r - 1] += val

    def is_gameover(self):
        for i in range(self.quantity_dots - 1):
            for j in range(self.quantity_dots - 1):
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
            start_x = self.dots_space / 2 + logical_position[0] * self.dots_space
            end_x = start_x + self.dots_space
            start_y = self.dots_space / 2 + logical_position[1] * self.dots_space
            end_y = start_y
        elif type == 'col':
            start_y = self.dots_space / 2 + logical_position[1] * self.dots_space
            end_y = start_y + self.dots_space
            start_x = self.dots_space / 2 + logical_position[0] * self.dots_space
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
            cur.execute("SELECT name, score FROM ezrated ORDER BY id DESC LIMIT 1")
            last_entry = cur.fetchone()
            if last_entry:
                last_name, current_score = last_entry
                cur.execute("UPDATE ezrated SET score = ? WHERE name = ?", (player1_score, last_name))
                self.bd.commit()
        elif player2_score > player1_score:
            cur = self.bd.cursor()
            text = 'Игрок 2 выиграл! '
            color = self.player2_color
            cur.execute("SELECT name, score FROM bluerate ORDER BY id DESC LIMIT 1")
            last_entry = cur.fetchone()
            if last_entry:
                last_name, current_score = last_entry
                cur.execute("UPDATE bluerate SET score = ? WHERE name = ?", (player2_score, last_name))
                self.bd.commit()
        else:
            text = 'Ничья :('
            color = 'gray'

        self.scene.clear()
        self.scene.addText(text, QFont('cmr', 150, QFont.Bold)).setDefaultTextColor(QColor(color))

        score_text = 'Scores \n'
        self.scene.addText(score_text, QFont('cmr', 40, QFont.Bold)).setDefaultTextColor(QColor(self.Green_color))

        score_text = 'Player 1 : ' + str(player1_score) + '\n'
        score_text += 'Player 2 : ' + str(player2_score) + '\n'
        self.scene.addText(score_text, QFont('cmr', 30, QFont.Bold)).setDefaultTextColor(QColor(self.Green_color))

        self.reset_board = True

        score_text = 'Чтобы начать еще раз - нажмите кнопку "Играть еще раз" \n'
        self.scene.addText(score_text, QFont('cmr', 10, QFont.Bold)).setDefaultTextColor(QColor('gray'))
        new_game_button = QPushButton('Играть еще раз')
        new_game_button.clicked.connect(self.replay) 
        self.scene.addWidget(new_game_button)

    def refreshBoard(self):
        for i in range(self.quantity_dots):
            x = i * self.dots_space + self.dots_space / 2
            self.scene.addLine(x, self.dots_space / 2, x,
                               self.board_size - self.dots_space / 2,
                               QPen(QColor('gray'), self.dot_width))

            self.scene.addLine(self.dots_space / 2, x,
                               self.board_size - self.dots_space / 2, x,
                               QPen(QColor('gray'), self.dot_width))

        for i in range(self.quantity_dots):
            for j in range(self.quantity_dots):
                start_x = i * self.dots_space + self.dots_space / 2
                end_x = j * self.dots_space + self.dots_space / 2

                dot_item = QGraphicsEllipseItem(start_x - self.dot_width / 2, end_x - self.dot_width / 2,
                                                self.dot_width, self.dot_width)
                dot_item.setBrush(QColor(self.dot_color))
                self.scene.addItem(dot_item)

    def screen_motion(self):
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
        start_x = self.dots_space / 2 + box[1] * self.dots_space
        start_y = self.dots_space / 2 + box[0] * self.dots_space
        end_x = start_x + self.dots_space
        end_y = start_y + self.dots_space

        box_item = QGraphicsRectItem(start_x, start_y, end_x - start_x, end_y - start_y)
        box_item.setBrush(QColor(color))
        self.scene.addItem(box_item)

    def click(self, event):
        if not self.reset_board:
            grid_position = [event.x(), event.y()]
            logical_position, valid_input = self.convert_grid_to_logical_position(grid_position)
            if 0 <= grid_position[0] <= self.board_size and 0 <= grid_position[1] <= self.board_size:
                if valid_input and not self.is_grid_occupied(logical_position, valid_input):
                    self.update_board(valid_input, logical_position)
                    self.make_edge(valid_input, logical_position)
                    self.mark_box()
                    self.refreshBoard()
                    self.player1_turn = not self.player1_turn

                    if self.is_gameover():
                        self.display_gameover()
                    else:
                        self.screen_motion()

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
                    self.screen_motion()
        else:
            self.scene.clear()
            self.replay()
            self.reset_board = False