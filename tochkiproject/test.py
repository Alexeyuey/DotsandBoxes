import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsRectItem, QPushButton, QMainWindow
from PyQt5.QtGui import QPen, QColor, QFont
from PyQt5.QtCore import Qt, QRectF
import numpy as np


class DotsAndBoxes(QMainWindow):
    def __init__(self):
        super().__init__()

        self.size_of_board = 800  # Увеличил размер окна
        self.number_of_dots = 6
        self.symbol_size = (self.size_of_board / 3 - self.size_of_board / 8) / 2
        self.symbol_thickness = 50
        self.dot_color = QColor('#7BC043')
        self.player1_color = QColor('#0492CF')
        self.player1_color_light = QColor('#67B0CF')
        self.player2_color = QColor('#EE4035')
        self.player2_color_light = QColor('#EE7E77')
        self.Green_color = QColor('#7BC043')
        self.dot_width = 0.25 * self.size_of_board / self.number_of_dots
        self.edge_width = 0.1 * self.size_of_board / self.number_of_dots
        self.distance_between_dots = self.size_of_board / (self.number_of_dots)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Dots_and_Boxes')
        self.setGeometry(100, 100, self.size_of_board, self.size_of_board)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, self.size_of_board, self.size_of_board)

        self.play_again_button = QPushButton('Play Again', self)
        self.play_again_button.setGeometry(10, 10, 100, 30)
        self.play_again_button.clicked.connect(self.play_again)

        self.player1_starts = True
        self.reset_board = False
        self.turntext_handle = None
        self.already_marked_boxes = []

        self.play_again()

    def play_again(self):
        self.refresh_board()
        self.board_status = np.zeros(shape=(self.number_of_dots - 1, self.number_of_dots - 1))
        self.row_status = np.zeros(shape=(self.number_of_dots, self.number_of_dots - 1))
        self.col_status = np.zeros(shape=(self.number_of_dots - 1, self.number_of_dots))

        self.player1_starts = not self.player1_starts
        self.player1_turn = not self.player1_starts
        self.reset_board = False
        self.turntext_handle = None

        self.already_marked_boxes = []
        self.display_turn_text()

    def display_turn_text(self):
        text = 'Next turn: '
        if self.player1_turn:
            text += 'Player1'
            color = self.player1_color
        else:
            text += 'Player2'
            color = self.player2_color

        if self.turntext_handle:
            self.scene.removeItem(self.turntext_handle)

        font = QFont("cmr", 15, QFont.Bold)
        self.turntext_handle = self.scene.addText(text, font)
        self.turntext_handle.setDefaultTextColor(color)
        self.turntext_handle.setPos(self.size_of_board - 5 * len(text), self.size_of_board - self.distance_between_dots / 8)

    def make_edge(self, type, logical_position):
        pen = QPen()
        pen.setWidthF(self.edge_width)
        if self.player1_turn:
            pen.setColor(self.player1_color)
        else:
            pen.setColor(self.player2_color)

        line = QGraphicsLineItem()
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

        line.setLine(start_x, start_y, end_x, end_y)
        line.setPen(pen)
        self.scene.addItem(line)

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
            color = QColor('gray')

        self.scene.clear()
        font = QFont("cmr", 60, QFont.Bold)
        winner_text = self.scene.addText(text, font)
        winner_text.setDefaultTextColor(color)
        winner_text.setPos(self.size_of_board / 2 - winner_text.boundingRect().width() / 2, self.size_of_board / 3)
        font = QFont("cmr", 40, QFont.Bold)
        score_text = self.scene.addText('Scores \n', font)
        score_text.setDefaultTextColor(self.Green_color)
        score_text.setPos(self.size_of_board / 2 - score_text.boundingRect().width() / 2, 5 * self.size_of_board / 8)

        score_text = self.scene.addText('Player 1 : ' + str(player1_score) + '\nPlayer 2 : ' + str(player2_score) + '\n',
                                        font)
        score_text.setDefaultTextColor(self.Green_color)
        score_text.setPos(self.size_of_board / 2 - score_text.boundingRect().width() / 2, 3 * self.size_of_board / 4)

        self.reset_board = True
        font = QFont("cmr", 20, QFont.Bold)
        play_again_text = self.scene.addText('Click to play again \n', font)
        play_again_text.setDefaultTextColor(QColor('gray'))
        play_again_text.setPos(self.size_of_board / 2 - play_again_text.boundingRect().width() / 2, 15 * self.size_of_board / 16)

    def refresh_board(self):
        for i in range(self.number_of_dots):
            x = i * self.distance_between_dots + self.distance_between_dots / 2
            line = QGraphicsLineItem(x, self.distance_between_dots / 2, x,
                                     self.size_of_board - self.distance_between_dots / 2)
            line.setPen(QPen(Qt.gray, 2, Qt.DashLine))
            self.scene.addItem(line)

            line = QGraphicsLineItem(self.distance_between_dots / 2, x,
                                     self.size_of_board - self.distance_between_dots / 2, x)
            line.setPen(QPen(Qt.gray, 2, Qt.DashLine))
            self.scene.addItem(line)

        for i in range(self.number_of_dots):
            for j in range(self.number_of_dots):
                start_x = i * self.distance_between_dots + self.distance_between_dots / 2
                end_x = j * self.distance_between_dots + self.distance_between_dots / 2
                dot = QGraphicsEllipseItem(start_x - self.dot_width / 2, end_x - self.dot_width / 2,
                                           self.dot_width, self.dot_width)
                dot.setBrush(self.dot_color)
                dot.setPen(self.dot_color)
                self.scene.addItem(dot)

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        position = (grid_position - self.distance_between_dots / 4) // (self.distance_between_dots / 2)

        type = False
        logical_position = []
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

    def is_grid_occupied(self, logical_position, type):
        r = logical_position[0]
        c = logical_position[1]

        if type == 'row' and 0 <= r < self.number_of_dots - 1 and 0 <= c < self.number_of_dots:
            return self.row_status[c][r] == 1
        elif type == 'col' and 0 <= r < self.number_of_dots and 0 <= c < self.number_of_dots - 1:
            return self.col_status[c][r] == 1
        else:
            return False

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
            if c >= 1:
                self.board_status[c - 1][r] += val

        elif type == 'col':
            self.col_status[c][r] = 1
            if r >= 1:
                self.board_status[c][r - 1] += val

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

    def is_gameover(self):
        return (self.row_status == 1).all() and (self.col_status == 1).all()

    def shade_box(self, box, color):
        start_x = self.distance_between_dots / 2 + box[1] * self.distance_between_dots + self.edge_width / 2
        start_y = self.distance_between_dots / 2 + box[0] * self.distance_between_dots + self.edge_width / 2
        end_x = start_x + self.distance_between_dots - self.edge_width
        end_y = start_y + self.distance_between_dots - self.edge_width
        rect = QGraphicsRectItem(QRectF(start_x, start_y, end_x - start_x, end_y - start_y))
        rect.setBrush(color)
        rect.setPen(QPen(Qt.NoPen))
        self.scene.addItem(rect)

    def mousePressEvent(self, event):
        if not self.reset_board:
            grid_position = [event.pos().x(), event.pos().y()]

            # Получаем ближайшие координаты узла
            nearest_x = round(grid_position[0] / self.distance_between_dots) * self.distance_between_dots
            nearest_y = round(grid_position[1] / self.distance_between_dots) * self.distance_between_dots

            # Преобразуем координаты узла в логическую позицию
            logical_position, valid_input = self.convert_grid_to_logical_position([nearest_x, nearest_y])

            if valid_input:
                # Определяем, в какую сторону было произведено нажатие
                dx = grid_position[0] - nearest_x
                dy = grid_position[1] - nearest_y

                # Определяем, является ли нажатие ближе к вертикальной или горизонтальной линии
                if abs(dx) < abs(dy):
                    # Вертикальная линия
                    if not self.is_grid_occupied(logical_position, 'col'):
                        self.update_board('col', logical_position)
                        self.make_edge('col', logical_position)
                        self.mark_box()
                        self.refresh_board()
                        self.player1_turn = not self.player1_turn

                        if self.is_gameover():
                            self.display_gameover()
                        else:
                            self.display_turn_text()
                else:
                    # Горизонтальная линия
                    if not self.is_grid_occupied(logical_position, 'row'):
                        self.update_board('row', logical_position)
                        self.make_edge('row', logical_position)
                        self.mark_box()
                        self.refresh_board()
                        self.player1_turn = not self.player1_turn

                        if self.is_gameover():
                            self.display_gameover()
                        else:
                            self.display_turn_text()
        else:
            self.scene.clear()
            self.play_again()
            self.reset_board = False

if __name__ == '__main__':
        app = QApplication(sys.argv)
        game_instance = DotsAndBoxes()
        game_instance.show()
        sys.exit(app.exec_())

