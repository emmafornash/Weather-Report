import os, sys
import requests
import json
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtSvg
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
import qdarkstyle

BASE_API_URL = "https://api.openweathermap.org/"

class WeatherGUI(QMainWindow):
    def __init__(self):
        super(WeatherGUI, self).__init__()
        title = "Weather"
        uic.loadUi('uis/weather_gui.ui', self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.setWindowTitle(title)
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.show()

        self.get_weather.clicked.connect(self.load_weather)

    # Gets the latitude and longitude from a particular zipcode
    def get_lat_and_lon(self, zip_code: str, country_code: str, api_key: str) -> tuple:
        try:
            # grabs geographical data and gets the latitude and longitude from it
            geocode_api_request = requests.get(BASE_API_URL + f"geo/1.0/zip?zip={zip_code},{country_code}&appid={api_key}")
            api = geocode_api_request.json()
            lat, lon = api['lat'], api['lon']
            return lat, lon
        except Exception as e:
            print(e)
    
    # Displays loaded weather in the GUI
    def display_weather_on_screen(self, temp: int, weather: str, humidity: int, city_name: str, units: str) -> None:
        # determines the degree reading of the temperature
        ending_units = None
        if units == "metric":
            ending_units = "C"
        elif units == "imperial":
            ending_units = "F"
        
        # sets up formats via fstrings
        temperature_display = f"{temp}°{ending_units}"
        weather_display = f"{weather}"
        humidity_display = f"Humidity: {humidity}%"
        city_display = f"In {city_name}"

        # sets all display strings to display on screen
        self.current_temperature.setPlainText(temperature_display)
        self.current_weather.setPlainText(weather_display)
        self.current_humidity.setPlainText(humidity_display)
        self.location_text.setPlainText(city_display)

    # Loads weather when all areas are filled
    def load_weather(self) -> None:
        zip_code = self.zipcode_edit.text()
        country_code = "US"
        api_key = self.api_key_edit.text()
        units = None

        try:
            # grabs latitude and longitude of zipcode for the api
            lat, lon = self.get_lat_and_lon(zip_code, country_code, api_key)
            
            # returns units in metric
            if self.metric_radio.isChecked():
                units = "metric"
            # returns units in imperial
            elif self.imperial_radio.isChecked():
                units = "imperial"

            weather_api_request = requests.get(BASE_API_URL + f"data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units={units}")
            api = weather_api_request.json()

            # grabs weather data from the requested json file
            current_temperature = round(api['main']['temp'])
            current_weather = api['weather'][0]['main']
            current_humidity = api['main']['humidity']
            city_name = api['name']

            self.display_weather_on_screen(current_temperature, current_weather, current_humidity, city_name, units)
        except Exception as e:
            print(e)

def main() -> None:
    app = QApplication(sys.argv)
    window = WeatherGUI()
    sys.exit(app.exec_())

main()