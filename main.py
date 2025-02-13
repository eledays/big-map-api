from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import requests
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.api_server = 'https://static-maps.yandex.ru/1.x/'
        self.map_zoom = 15
        self.delta = .005
        self.map_ll = [37.621601, 55.753460]
        self.map_l = 'map'
        self.refresh_map()

    def initUI(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setWindowTitle("Большая карта")
        self.setGeometry(100, 100, 800, 600)

        self.line_edit = QLineEdit(self)
        self.line_edit.setGeometry(50, 10, 300, 30)

        self.search_button = QPushButton("Искать", self)
        self.search_button.setGeometry(360, 10, 100, 30)

        self.scheme_button = QPushButton("Схема", self)
        self.scheme_button.setGeometry(680, 50, 100, 30)

        self.satellite_button = QPushButton("Спутник", self)
        self.satellite_button.setGeometry(680, 90, 100, 30)

        self.hybrid_button = QPushButton("Гибрид", self)
        self.hybrid_button.setGeometry(680, 130, 100, 30)

        self.map_label = QLabel(self)
        self.map_label.setGeometry(50, 50, 600, 400)
        
    def refresh_map(self):
        map_params = {
            "ll": ",".join(map(str, self.map_ll)),
            "l": self.map_l,
            "z": self.map_zoom
        }
        response = requests.get(self.api_server, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print('http code:', response.status_code, '(', response.reason, ')')
            return
        
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.map_label.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        self.setFocus()
        if event.key() == Qt.Key.Key_BracketRight and self.map_zoom < 21:
            self.map_zoom += 1
        elif event.key() == Qt.Key.Key_BracketLeft and self.map_zoom > 0:
            self.map_zoom -= 1
        
        elif event.key() == Qt.Key.Key_Left:
            self.map_ll[0] -= self.delta
        elif event.key() == Qt.Key.Key_Right:
            self.map_ll[0] += self.delta
        elif event.key() == Qt.Key.Key_Up:
            self.map_ll[1] += self.delta    
        elif event.key() == Qt.Key.Key_Down:
            self.map_ll[1] -= self.delta

        self.refresh_map()
            

if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.initUI()
    main_window.show()
    sys.exit(app.exec())
