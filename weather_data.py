# wheather_data.py
"""
    Code that gets weather data using OpenWeatherMap API
    
    Gets weather data using OpenWeatherMap API
    -> Gets current weather
    -> Gets rain forecast
    eg: get_weather("City")
        get_rain_forecast("City")
"""

import os
import pytz
import requests
from datetime import datetime
from dotenv import load_dotenv

def get_api():
    load_dotenv()
    return os.getenv('OPENWEATHER_API_KEY')

# MARK: Weather
def get_weather(CITY: str = 'Kozhikode'):
    API_KEY = get_api()
    URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'
    
    try:
        response = requests.get(URL)
        
        if response.status_code == 200:
            weather_data = response.json()
            
            city_name = weather_data['name']
            weather_main = weather_data['weather'][0]['main']
            weather_description = weather_data['weather'][0]['description']
            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            
            print(f"\033[32mCurrent weather in {city_name}:\033[0m")
            print(f"\033[32mCondition: {weather_main} ({weather_description})\033[0m")
            print(f"\033[32mTemperature: {temperature}°C\033[0m")
            print(f"\033[32mHumidity: {humidity}%\033[0m")
            print(f"\033[32mWind Speed: {wind_speed} m/s\033[0m")
            print("-" * 40)
            
            return temperature, humidity, wind_speed, weather_main
        else:
            print(f"\033[31mError: Unable to fetch current weather data. Status code: {response.status_code}\033[0m")
    
    except requests.exceptions.RequestException as e:
        print(f"\033[31mAn error occurred while fetching current weather: {e}\033[0m")

# MARK: Rain forecast
def get_rain_forecast(CITY: str = 'Kozhikode', timezone : str = 'Asia/Kolkata'):
    API_KEY = get_api()
    URL = f'http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric'
    
    try:
        response = requests.get(URL)
        
        if response.status_code == 200:
            forecast_data = response.json()
            
            i = 0
            rain_3h: int = 0
            rain_6h: int = 0
            rain_9h: int = 0
            rain_12h: int = 0
            
            # Iterate over the forecast list (which contains 3-hour intervals)
            for forecast in forecast_data['list']:
                city_timezone = pytz.timezone(timezone)
                
                # Get the timestamp of the forecast
                timestamp = forecast['dt']
                
                # Convert the timestamp to the city's local time
                local_time = datetime.fromtimestamp(timestamp, city_timezone)
                forecast_time = local_time.strftime('%H:%M:%S %d-%m-%Y')
                
                # Extract rain data (if available)
                rain = forecast.get('rain', {}).get('3h', 0)  # Rain in the next 3 hours
                
                # Print the forecast time and rain data
                print(f"\033[32mForecast for {forecast_time}:\033[0m")
                if rain > 0:
                    print(f"\033[32mExpected Rain: {rain} mm\033[0m")
                else:
                    print("\033[32mNo rain expected.\033[0m")
                
                print(forecast['dt_txt'])
                print("-" * 40)
                
                if i == 0:
                    rain_3h = rain
                elif i == 1:
                    rain_6h = rain
                elif i == 2:
                    rain_9h = rain
                elif i == 3:
                    rain_12h = rain
                i += 1
                
                if rain_12h:
                    print(f"\033[32mRain forecast for next 3 hours: {rain_3h} mm\033[0m")
                    print(f"\033[32mRain forecast for the next 6 hours: {rain_6h} mm\033[0m")
                    print(f"\033[32mRain forecast for the next 9 hours: {rain_9h} mm\033[0m")
                    print(f"\033[32mRain forecast for the next 12 hours: {rain_12h} mm\033[0m")
                    break
                    
            return rain_3h, rain_6h, rain_9h, rain_12h
        
        else:
            print(f"\033[31mError: Unable to fetch weather forecast data. Status code: {response.status_code}\033[0m")
    
    except requests.exceptions.RequestException as e:
        print(f"\033[31mAn error occurred while fetching future rain forecast: {e}\033[0m")

def main():
    CITY = 'Kozhikode'  # You can change this to your desired city name # TODO: Change
    
    get_weather(CITY)
    get_rain_forecast(CITY)

if __name__ == '__main__':
    main()
