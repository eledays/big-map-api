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
        self.static_api_server = 'https://static-maps.yandex.ru/1.x/'
        self.geocoder_api_server = 'https://geocode-maps.yandex.ru/1.x/'
        self.map_zoom = 15
        self.delta = .005
        self.map_ll = [37.621601, 55.753460]
        self.map_l = 'map'
        self.static_api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.geocoder_api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        self.pt = None
        self.address = ''
        self.postal_code = ''
        self.refresh_map()

    def initUI(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setWindowTitle("Большая карта")
        self.setGeometry(100, 100, 840, 600)

        self.line_edit = QLineEdit(self)
        self.line_edit.setGeometry(50, 10, 300, 30)

        self.search_button = QPushButton("Искать", self)
        self.search_button.setGeometry(360, 10, 100, 30)
        self.search_button.clicked.connect(self.search_location)

        self.search_button = QPushButton("Сбросить", self)
        self.search_button.setGeometry(470, 10, 100, 30)
        self.search_button.clicked.connect(self.clear_location)

        self.theme_button = QPushButton("Сменить тему", self)
        self.theme_button.setGeometry(680, 170, 140, 30)
        self.theme_button.clicked.connect(self.toggle_theme)
        
        self.is_dark_theme = False

        self.map_label = QLabel(self)
        self.map_label.setGeometry(50, 50, 600, 400)

        self.address_label = QLabel(self)
        self.address_label.setGeometry(50, 460, 600, 30)

        self.toggle_postal_code_button = QPushButton("Почтовый индекс", self)
        self.toggle_postal_code_button.setGeometry(680, 210, 140, 30)
        self.toggle_postal_code_button.clicked.connect(self.toggle_postal_code)

        self.is_postal_code_enabled = False
        
    def refresh_map(self):
        map_params = {
            "ll": ",".join(map(str, self.map_ll)),
            "l": self.map_l,
            "z": self.map_zoom,
            'theme': 'dark' if self.is_dark_theme else 'light',
            'apikey': self.static_api_key,
            'pt': self.pt
        }
        response = requests.get(self.static_api_server, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print('http code:', response.status_code, f'({response.reason}), {response.url}')
            return
        
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.map_label.setPixmap(self.pixmap)

        address = self.address
        if self.is_postal_code_enabled:
            address += ' ' + self.postal_code
        self.address_label.setText(address)

    def keyPressEvent(self, event):
        self.setFocus()
        if event.key() == Qt.Key.Key_BracketRight and self.map_zoom < 21:
            self.map_zoom += 1
        elif event.key() == Qt.Key.Key_BracketLeft and self.map_zoom > 0:
            self.map_zoom -= 1
        
        elif event.key() == Qt.Key.Key_Left or event.key() == Qt.Key.Key_A:
            self.map_ll[0] -= self.delta
        elif event.key() == Qt.Key.Key_Right or event.key() == Qt.Key.Key_D:
            self.map_ll[0] += self.delta
        elif event.key() == Qt.Key.Key_Up or event.key() == Qt.Key.Key_W:
            self.map_ll[1] += self.delta    
        elif event.key() == Qt.Key.Key_Down or event.key() == Qt.Key.Key_S:
            self.map_ll[1] -= self.delta

        self.refresh_map()
            
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #333333;
                }
                QPushButton {
                    background-color: #444444;  
                    color: white;
                    border: 1px solid #555555;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
                QLineEdit {
                    background-color: #444444;
                    color: white;
                    border: 1px solid #555555;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("") 
        self.refresh_map()

    def search_location(self):
        search_query = self.line_edit.text()
        if not search_query:
            return
            
        geocoder_params = {
            "apikey": self.geocoder_api_key,
            "geocode": search_query,
            "format": "json"
        }
        
        response = requests.get(self.geocoder_api_server, params=geocoder_params)
        
        if not response:
            print("Ошибка выполнения запроса:")
            print('http code:', response.status_code, f'({response.reason}), {response.url}')
            return
            
        json_response = response.json()
        
        features = json_response["response"]["GeoObjectCollection"]["featureMember"]
        if not features:
            print("Ничего не найдено")
            return
            
        point_str = features[0]["GeoObject"]["Point"]["pos"]
        self.address = features[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
        self.postal_code = features[0]["GeoObject"]['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
        self.map_ll = list(map(float, point_str.split()))
        
        self.pt=f'{self.map_ll[0]},{self.map_ll[1]}'
        self.refresh_map()

    def clear_location(self):
        self.address_label.clear()
        self.line_edit.clear()
        self.pt = None
        self.refresh_map()

    def toggle_postal_code(self):
        self.is_postal_code_enabled = not self.is_postal_code_enabled
        self.refresh_map()
        

if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    main_window.initUI()
    main_window.show()
    sys.exit(app.exec())
