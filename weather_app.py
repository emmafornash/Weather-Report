import os, sys
from types import NoneType
import requests
import json
import uszipcode as zc
import pycountry
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QGradient
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis
import qdarkstyle
import datetime
from collections import Counter
import math


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
        self.set_default_action.triggered.connect(self.save_default_data)
        # lambdatized the connected function to add a file argument to it
        self.load_default_action.triggered.connect(lambda checked, file='user.json': self.load_data(file))
        self.load_json_action.triggered.connect(self.load_data_from_file)
        self.temperature_forecast_chart.hide()

        # checks if user data already exists. if so, loads it
        if os.path.exists('./user.json'):
            self.load_data(file='user.json')
        else:
            self.load_default_action.setDisabled(True)

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
    
    # changes weather icon given a particular weather state
    def change_weather_icon(self, label: QLabel, weather: str, dt: int, sunrise: int, sunset: int, cloud_percentage: int) -> None:
        print(weather)
        file = "icons/inverted/"
        # 15 minute time offset in unix UTC
        sunrise_set_offet = 900
        match weather:
            case 'Clear':
                # determines which clear sky image to use, depending on the time of day
                if sunrise + sunrise_set_offet <= dt <= sunset - sunrise_set_offet:
                    file += 'sun.png'
                elif sunrise - sunrise_set_offet <= dt <= sunrise + sunrise_set_offet:
                    file += 'sunrise.png'
                elif sunset - sunrise_set_offet <= dt <= sunset + sunrise_set_offet:
                    file += 'sunset.png'
                else:
                    file += 'moon.png'
            case 'Rain':
                file += 'rainy.png'
            case 'Drizzle':
                file += 'drizzle.png'
            case 'Thunderstorm':
                file += 'storm.png'
            case 'Mist':
                file += 'fog.png'
            case 'Fog':
                file += 'fog.png'
            case 'Snow':
                file += 'snowing.png'
            case 'Clouds':
                # determines how cloudy the given area is
                if cloud_percentage <= 50:
                    if sunrise <= dt <= sunset:
                        file += 'cloudy.png'
                    else:
                        file += 'cloudy-night.png'
                else:
                    file += 'clouds.png'
            case other:
                file += 'rainy-day.png'
            
        label.setPixmap(QPixmap(file))

    # Adds any extra icons in front of the "feels like" field
    def change_extra_icon(self, weather: str, temp_and_units: tuple):
        # sets up the proper threshold values depending on the units given
        too_hot_threshold = too_cold_threshold = -1
        match temp_and_units[1]:
            case 'metric':
                too_hot_threshold = 37
                too_cold_threshold = -17
            case 'imperial':
                too_hot_threshold = 99
                too_cold_threshold = 0
            case other:
                pass
        
        # determines and draws an extra icon, if any
        file = 'icons/inverted/'
        if temp_and_units[0] >= too_hot_threshold:
            file += 'hot.png'
        elif temp_and_units[0] <= too_cold_threshold:
            file += 'cold.png'
        elif weather == 'Rain':
            file += 'umbrella.png'
        
        self.extra_icon_label.setPixmap(QPixmap(file))

    # Displays loaded weather in the GUI
    def display_weather_on_screen(self, temp: int, weather: str, humidity: int, city_name: str, country: str, feels_like: str, units: str) -> None:
        # determines the degree reading of the temperature
        ending_units = None
        if units == "metric":
            ending_units = "C"
        elif units == "imperial":
            ending_units = "F"
        
        # sets up formats via fstrings
        temperature_display = f"{temp}°{ending_units}"
        feels_like_display = f"Feels like: {feels_like}°{ending_units}"
        weather_display = f"{weather.capitalize()}"
        humidity_display = f"{humidity}%"
        city_display = f"In {city_name}, {country}"

        # sets all display strings to display on screen
        self.current_temperature.setPlainText(temperature_display)
        self.current_feels_like.setPlainText(feels_like_display)
        self.current_weather.setPlainText(weather_display)
        self.current_humidity.setPlainText(humidity_display)
        self.location_text.setPlainText(city_display)

    # Loads weather when all areas are filled
    def load_weather(self) -> None:
        zip_code = self.zipcode_edit.text()
        # loads the selected country name if not loading user data
        country_name = self.country_combo_box.currentText()
        country_code = pycountry.countries.get(name=country_name).alpha_2
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

            # requests current weather data
            weather_api_request = requests.get(BASE_API_URL + f"data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units={units}")
            api = weather_api_request.json()

            print(api)

            # grabs weather data from the requested json file
            current_temperature = round(api['main']['temp'])
            current_feels_like = round(api['main']['feels_like'])
            current_weather_desc = api['weather'][0]['description']
            current_humidity = api['main']['humidity']
            # may potentially set the name to None. keep an eye on this
            city_details = zc.SearchEngine().by_zipcode(zip_code)
            # if city details is None, then the zipcode given is not an American one
            if not isinstance(city_details, NoneType):
                city_name = f'{city_details.major_city}, {city_details.state}'
            else:
                city_name = api['name']
            country = api['sys']['country']

            self.display_weather_on_screen(current_temperature, current_weather_desc, current_humidity, city_name, country, current_feels_like, units)

            # grabs time and date and changes the main weather icon
            current_weather = api['weather'][0]['main']
            dt = api['dt']
            sunrise = api['sys']['sunrise']
            sunset = api['sys']['sunset']
            cloud_percentage = api['clouds']['all']
            self.change_weather_icon(self.weather_icon_label, current_weather, dt, sunrise, sunset, cloud_percentage)
            self.change_extra_icon(current_weather, (current_feels_like, units))

            # requests forecast data
            forecast_api_request = requests.get(BASE_API_URL + f"data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units={units}")
            forecast_api = forecast_api_request.json()

            # initializes values with current data and sets them up

            # grabs specifically the asctime weekday as an abbreviation
            current_day_of_week = datetime.datetime.fromtimestamp(dt).ctime()[:3]
            weather_buckets = [[(current_day_of_week, current_weather, cloud_percentage, current_temperature, '')]]

            weather_buckets = self.set_up_buckets(forecast_api, weather_buckets)
            # further processes the weather bucket before displaying to the forecast
            forecast_days, common_weather, forecast_clouds, forecast_temperatures = self.process_weather_forecast(weather_buckets)
            self.display_forecast_to_screen(forecast_days, common_weather, forecast_clouds, forecast_temperatures, dt, sunrise, sunset)

            # processes and adds temperature data to the linechart
            temperature_buckets = self.process_temperature_forecast(weather_buckets)
            self.display_temperature_linechart(temperature_buckets[0])
        except Exception as e:
            print(e)

    # Initializes buckets to have current weather data in them
    def set_up_buckets(self, api: json, weather_bucket: list) -> tuple:
        now = datetime.datetime.now().date()
        for forecast in api['list']:
            unix_time = forecast['dt']
            timestamp = datetime.datetime.fromtimestamp(unix_time)
            forecast_date = timestamp.date()
            # adds a new bucket if dates are different
            if now != forecast_date:
                weather_bucket.append([])
                now = forecast_date

            day_of_week = timestamp.ctime()[:3]
            weather = forecast['weather'][0]['main']
            clouds = forecast['clouds']['all']
            temperature = round(forecast['main']['temp'])
            
            # determines the prefix for time
            forecast_time = int(timestamp.strftime("%H"))
            if forecast_time <= 12:
                forecast_time = f'{forecast_time} AM'
            else:
                forecast_time = f'{forecast_time % 12} PM'

            weather_bucket[-1].append((day_of_week, weather, clouds, temperature, forecast_time))
        
        # we only need the first 5 days of forecast, so slice off the extra
        return weather_bucket[:5]

    # Processes weather forecast data for use in the temperature chart
    def process_temperature_forecast(self, weather_buckets: list) -> list:
        # adds up to 8 values from the next day's forecast to make the graph more even
        spillover = 8 - len(weather_buckets[0])
        weather_buckets[0].extend(weather_buckets[1][:spillover])
        
        # only takes the temperature reading and formatted time
        temperature_buckets = [[(reading[3], reading[4]) for reading in bucket] for bucket in weather_buckets]
        
        return temperature_buckets

    # Displays the temperature linechart to the screen
    def display_temperature_linechart(self, temperature_bucket: list) -> None:
        # initializes a line series to contain all temperature values
        series = QLineSeries(self)
        series_labels = []
        series_max = -math.inf
        series_min = math.inf
        for i in range(len(temperature_bucket)):
            val, time = temperature_bucket[i]
            series.append(i, val)
            series_labels.append(time)

            # finds temperature high and low for the ylim of the graph
            if val > series_max:
                series_max = val
            if val < series_min:
                series_min = val
        
        # sets up the labels and colors for the graph
        series.setPointLabelsVisible(True)
        series.setPointLabelsColor(Qt.white)
        series.setPointLabelsFormat("@yPoint")
        series.setPointLabelsClipping(False)
        series.setColor(Qt.yellow)

        chart = QChart()

        # sets up the labels for the x axis
        axis_x = QCategoryAxis()
        axis_x.setRange(0, 7)
        for i in range(len(series_labels)):
            label = series_labels[i]
            axis_x.append(label, i)
        axis_x.setGridLineVisible(False)
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        axis_x.setLabelsColor(Qt.white)

        # sets up the y axis
        axis_y = QValueAxis()
        axis_y.setRange(series_min - 3, series_max + 3)
        axis_y.setGridLineVisible(False)
        axis_y.setVisible(False)

        # creates and adds a background gradient
        
        # currently set to one color, the same color as everything 
        # in the background. may be changed in the future
        background_gradient = QLinearGradient()
        background_gradient.setStart(QPoint(0, 0))
        background_gradient.setFinalStop(QPoint(0, 1))
        background_gradient.setColorAt(0.0, QColor(25, 35, 45))
        background_gradient.setColorAt(1.0, QColor(25, 35, 45))
        background_gradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        chart.setBackgroundBrush(background_gradient)

        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)

        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().hide()

        # removes large margins around the chart layout for a cleaner look
        chart.layout().setContentsMargins(0, 0, 5, 0)
        chart.setBackgroundRoundness(0)

        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        self.temperature_forecast_chart.setChart(chart)
        self.temperature_forecast_chart.setRenderHint(QPainter.Antialiasing)

        self.temperature_forecast_chart.show()

    # Processes weather forecast data for use in displaying it to the screen
    def process_weather_forecast(self, weather_buckets: list) -> tuple:
        # sets up the modifications needed to change the labels succinctly 
        forecast_days = []
        most_common_weather = []
        average_clouds = []
        high_and_low_temperatures = []
        for bucket in weather_buckets:
            # finds the most common weather, cloud percentage, and max and 
            # min temperatures per bucket
            weather_list = []
            clouds = 0
            max_temp = -math.inf
            min_temp = math.inf

            for forecast in bucket:
                day, weather, cloud, temp, time = forecast
                forecast_days.append(day)
                weather_list.append(weather)
                clouds += cloud
                if temp > max_temp:
                    max_temp = temp
                if temp < min_temp:
                    min_temp = temp
            
            # adds processed values to respective lists
            val, count = Counter(weather_list).most_common(1)[0]
            most_common_weather.append(val)
            average_clouds.append(clouds / len(bucket))
            high_and_low_temperatures.append(f'{max_temp}° {min_temp}°')  
        
        # removes duplicates from forecast days
        forecast_days = list(dict.fromkeys(forecast_days))

        return forecast_days, most_common_weather, average_clouds, high_and_low_temperatures

    def display_forecast_to_screen(self, forecast_days: list, common_weather: list, clouds: list, temperatures: list, dt: int, sunrise: int, sunset: int) -> None:
        # all labels to be altered
        days_of_week_labels = [self.forecast_day_1, self.forecast_day_2, self.forecast_day_3, self.forecast_day_4, self.forecast_day_5]
        weather_labels = [self.forecast_weather_1, self.forecast_weather_2, self.forecast_weather_3, self.forecast_weather_4, self.forecast_weather_5]
        temperature_labels = [self.forecast_temp_1, self.forecast_temp_2, self.forecast_temp_3, self.forecast_temp_4, self.forecast_temp_5]
        
        for i in range(len(days_of_week_labels)):
            day = forecast_days[i]
            weather = common_weather[i]
            cloud_percentage = clouds[i]
            temp = temperatures[i]
            days_of_week_labels[i].setText(day)
            self.change_weather_icon(weather_labels[i], weather, dt, sunrise, sunset, cloud_percentage)
            temperature_labels[i].setText(temp)
        
    # Grabs and saves default user data
    def save_default_data(self) -> None:
        try:
            # grabs all data necessary
            zip_code = self.zipcode_edit.text()
            country_name = self.country_combo_box.currentText()
            api_key = self.api_key_edit.text()
            units = None
            
            # returns units in metric
            if self.metric_radio.isChecked():
                units = "metric"
            # returns units in imperial
            elif self.imperial_radio.isChecked():
                units = "imperial"
            
            # stores data in a dictionary
            data_dict = {
                'zip': zip_code,
                'country': country_name,
                'api': api_key,
                'units': units
            }

            # writes to ./user.json
            json_obj = json.dumps(data_dict, indent=4)
            
            with open("user.json", "w") as out:
                out.write(json_obj)
            
            # allows load default action to be selectable
            self.load_default_action.setDisabled(False)
        except Exception as e:
            print(e)

    # Loads data from file
    def load_data(self, file) -> None:
        with open(file, 'r') as file:
            json_obj = json.load(file)
        
        needed_fields = {"zip", "api", "country", "units"}
        if needed_fields <= json_obj.keys():
            self.zipcode_edit.setText(json_obj['zip'])
            self.api_key_edit.setText(json_obj['api'])
            self.country_combo_box.setCurrentText(json_obj['country'])
            if json_obj['units'] == 'metric':
                self.metric_radio.setChecked(True)
            else:
                self.imperial_radio.setChecked(True)
            self.load_weather()
        else:
            print("Needed fields don't exist in selected JSON file")

    # Loads a .json file from a FileDialog
    def load_data_from_file(self) -> None:
        file = QFileDialog.getOpenFileName(self, "Open File", ".", 'JSON (*.json)')[0]
        self.load_data(file)
        

def main() -> None:
    app = QApplication(sys.argv)
    window = WeatherGUI()
    sys.exit(app.exec_())

main()