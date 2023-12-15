import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtCore import Qt
import numpy as np

class DotsAndBoxes(QMainWindow):
    def __init__(self, size_of_board, number_of_dots):
        super().__init__()

        self.size_of_board = size_of_board
        self.number_of_dots = number_of_dots
        self.symbol_size = (self.size_of_board / 3 - self.size_of_board / 8) / 2
        self.distance_between_dots = self.size_of_board / (self.number_of_dots)
        self.dot_radius = 0.25 * self.size_of_board / self.number_of_dots
        self.edge_width = 0.1 * self.size_of_board / self.number_of_dots

        self.init_ui()

    def init_ui(self):
        self.scene = QGraphicsScene(self)

        # Create QGraphicsView and set the scene
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.setGeometry(100, 100, self.size_of_board, self.size_of_board)
        self.setWindowTitle('Dots and Boxes')

        self.draw_board()

    def draw_board(self):
        for i in range(self.number_of_dots):
            for j in range(self.number_of_dots):
                x = j * self.distance_between_dots
                y = i * self.distance_between_dots
                dot = QGraphicsEllipseItem(x - self.dot_radius, y - self.dot_radius,
                                           2 * self.dot_radius, 2 * self.dot_radius)
                dot.setBrush(Qt.black)
                self.scene.addItem(dot)

        self.edges = np.zeros(shape=(self.number_of_dots - 1, self.number_of_dots - 1), dtype=QGraphicsLineItem)

        for i in range(self.number_of_dots - 1):
            for j in range(self.number_of_dots - 1):
                x = (j + 0.5) * self.distance_between_dots
                y = (i + 0.5) * self.distance_between_dots
                line = QGraphicsLineItem(x, y, x + self.distance_between_dots, y)
                line.setPen(Qt.NoPen)
                self.edges[i][j] = line
                self.scene.addItem(line)

                line = QGraphicsLineItem(x, y, x, y + self.distance_between_dots)
                line.setPen(Qt.NoPen)
                self.edges[i][j] = line
                self.scene.addItem(line)

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        col = int(x / self.distance_between_dots)
        row = int(y / self.distance_between_dots)

        if 0 < x % self.distance_between_dots < self.edge_width and 0 < y % self.distance_between_dots < self.edge_width:
            self.edges[row][col].setPen(Qt.red)
            self.edges[row][col].setZValue(1)

        elif 0 < x % self.distance_between_dots < self.edge_width and \
                0 < (y - self.distance_between_dots) % self.distance_between_dots < self.edge_width:
            self.edges[row - 1][col].setPen(Qt.red)
            self.edges[row - 1][col].setZValue(1)

        elif 0 < (x - self.distance_between_dots) % self.distance_between_dots < self.edge_width and \
                0 < y % self.distance_between_dots < self.edge_width:
            self.edges[row][col - 1].setPen(Qt.red)
            self.edges[row][col - 1].setZValue(1)

        elif 0 < (x - self.distance_between_dots) % self.distance_between_dots < self.edge_width and \
                0 < (y - self.distance_between_dots) % self.distance_between_dots < self.edge_width:
            self.edges[row - 1][col - 1].setPen(Qt.red)
            self.edges[row - 1][col - 1].setZValue(1)

        self.check_boxes()

    def check_boxes(self):
        # Implement box-checking logic here
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dots_and_boxes_app = DotsAndBoxes(600, 6)
    dots_and_boxes_app.show()
    sys.exit(app.exec_())
