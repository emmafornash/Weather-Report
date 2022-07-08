import os, sys
import requests
import json
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
import qdarkstyle

BASE_API_URL = "https://api.openweathermap.org/"

class WeatherGUI(QMainWindow):
    def __init__(self, key: str):
        super(WeatherGUI, self).__init__()
        title = "Weather"
        uic.loadUi('uis/weather_gui.ui', self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.setWindowTitle(title)
        self.show()

        self.api_key = key

        self.weather_text.setReadOnly(True)
        
        try:
            city = "London"
            country_code = "GB"
            limit = 1
            geocode_api_request = requests.get(BASE_API_URL + f"geo/1.0/direct?q={city},{country_code}&limit={limit}&appid={self.api_key}")
            api = json.loads(geocode_api_request.content)
            lat, lon = api[0]['lat'], api[0]['lon']
        except Exception as e:
            print(e)
            api = "Error"

        print(lat, lon)

        try:
            units = "metric"
            weather_api_request = requests.get(BASE_API_URL + f"data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units={units}")
            api = json.loads(weather_api_request.content)
            print(api)
            weather = api['weather'][0]['main']
            current_temperature = round(api['main']['temp'])
            humidity = api['main']['humidity']
            print(weather)
            self.weather_text.setPlainText(f"{weather}, {current_temperature}C, humidity={humidity}%")
        except Exception as e:
            print(e)



def main() -> None:
    print("Enter API Key:")
    key = str(input())

    app = QApplication(sys.argv)
    window = WeatherGUI(key)
    sys.exit(app.exec_())

main()