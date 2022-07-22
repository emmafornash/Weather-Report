# Weather App

A minimalist weather app in Python, using data from OpenWeatherMap.

![weatherapp](https://user-images.githubusercontent.com/89596994/180513685-4664abb3-7069-45cf-8f83-7260a6d27ede.gif)

## Key Features

- Current weather and forecast from anywhere in the world
- Temperature and Precipitation graphs from your selected location

## How to Use

### Dependencies

- [uszipcode](https://github.com/MacHu-GWU/uszipcode-project)
- [pycountry](https://github.com/flyingcircusio/pycountry)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- [PyQt-Charts](https://www.riverbankcomputing.com/software/pyqtchart/)
- [QDarkStyle](https://github.com/ColinDuquesnoy/QDarkStyleSheet)

### Instructions

1. Clone this project
2. Install the dependencies above - `pip install -r requirements.txt`
3. Obtain an API key from [OpenWeatherMap](https://openweathermap.org/price) (it's free!)
4. Run `weather_app.py`

Fill in the required fields for API key and postal code, choose your country (typing makes it easier), and press "Get Weather." After a small delay, your selected location's weather will appear.

## Attributions

- <a href="https://www.flaticon.com/free-icons/weather" title="weather icons">Weather icons created by Freepik - Flaticon</a>
- [Weather Data acquired from OpenWeatherMap's API](https://openweathermap.org/)

## Known and potential issues

- When loading new weather data, the forecast graph for temperature and precipitation will not load text properly unless moused over
- Many countries may have issues with some of their postal codes. I have squashed as many of the bugs I could find, but many more might exist

## License
[MIT](https://choosealicense.com/licenses/mit/)
