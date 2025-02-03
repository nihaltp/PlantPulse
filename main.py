# rover.py
"""
    Code that controls the Rover
    
    Moves the Rover using rover_L298N.py
    -> Uses defined distances to move the Rover
    eg: execute_line(1)
    
    Gets Moisture from moisture.py
    -> lowers the moisture sensor to get moisture value
    -> gets the moisture value
    -> raises the moisture sensor
    eg: moisture_value = get_moisture()
    
    Gets Weather from weather.py
    -> Gets Temperature using get_weather function
        -> Gets Temperature
        -> Gets Humidity
        -> Gets Wind Speed
    eg: temperature, humidity, wind_speed, weather = get_weather("City")
    
    Gets Rain from weather.py
    -> Gets Rain using get_rain_forecast function
        -> Gets Rain 3h
        -> Gets Rain 6h
        -> Gets Rain 9h
        -> Gets Rain 12h
    eg: rain_3h, rain_6h, rain_9h, rain_12h = get_rain_forecast("City")
    
    finds water content needed using camera.py
    -> finds species of leaves
    -> finds water needed for the plant according to species
    
    finds water content of leaves using camera.py
    -> finds water content of leaves
    
    calculates water needed for the plant
    -> uses temperature, humidity, wind_speed, rain_3h, rain_6h, rain_9h, rain_12h
    -> uses water content of leaves
    -> uses water needed for the plant according to species
    
    Waters the plant using water.py
    
    shows data using blynk.py
    -> shows the moisture value
    -> shows the species of plant
    -> shows the water content of plant
    -> shows the water needed for the plant
    
    # TODO: Manual Control of the Rover using ESP or transmitter and receiver
"""

from rover_L298N import read_csv, execute_line
from moisture_sensor import get_moisture
from sensor_movement import move_up, move_down, stop_motor
from weather_data import get_weather, get_rain_forecast
from plant_camera import camera
from water_pump import water
from blynk_api import send_data_to_blynk

import cv2
import json
from time import sleep
import RPi.GPIO as GPIO
import concurrent.futures

def camera_work():
    # Capture a frame from the camera
    frame = camera.camera.capture_array()
    
    # Process the frame to detect species and water content
    processed_frame = camera.process_frame(frame)
    
    # Display processed results if desired
    print(f"Detected Species: {camera.species}")
    print(f"Detection Score: {camera.score}")
    print(f"Water Content: {camera.water_content:.2f}%")
    print(f"Water Needed: {camera.water_content_needed:.2f}%")
    
    # Optionally display the frame with annotations
    cv2.imshow("Processed Frame", processed_frame)
    cv2.waitKey(0)  # Wait for a key press to close the window
    
    return camera.species, camera.water_content, camera.water_content_needed

def load_species_water_content(self):
    # Load species water content from JSON file
    with open("config/water_needed.json", "r") as file:
        species_water_content = json.load(file)
        file.close()
    return species_water_content

# Calculate weight factors based on temperature and humidity
def calculate_weight(temp: int, humid: int, time_decay: float, rain: int):
    return max(0, 1 - (temp * time_decay / (humid + 1))) * rain

# MARK: water needed
def get_water_needed(species: str, moisture_value, temperature, humidity, rain_3h, rain_6h, rain_9h, rain_12h, water_content, water_content_needed, species_water_content):
    # Calculate water needed for the plant
    S = species_water_content[species]
    
    # Time decay factors for rainfall
    t_3h, t_6h, t_9h, t_12h = 0.25, 0.5, 0.75, 1.0  # TODO: Change
    
    # Weight factors
    w_3h = calculate_weight(temperature, humidity, t_3h, rain_3h)
    w_6h = calculate_weight(temperature, humidity, t_6h, rain_6h)
    w_9h = calculate_weight(temperature, humidity, t_9h, rain_9h)
    w_12h = calculate_weight(temperature, humidity, t_12h, rain_12h)
    
    # Calculate effective rainfall contribution (R)
    R = w_3h + w_6h + w_9h + w_12h  # Total rainfall
    
    # Soil moisture adjustment (M)
    moisture_factor = 0.5  # Adjust this value based on soil type # TODO: Change
    M = moisture_value * moisture_factor
    
    # Evapotranspiration adjustment (E)
    temp_factor = 1.0  # Temperature contribution factor  # TODO: Change
    humidity_factor = 0.5  # Humidity contribution factor # TODO: Change
    
    E = (temperature * temp_factor) - (humidity * humidity_factor)
    
    # Calculate total water needed
    water_needed = S - (R + M) + E
    
    # Ensure water needed is non-negative
    water_needed_calculated = max(0, water_needed)
    water_needed_calculated = round(water_needed_calculated, 2)
    
    print(f"Water Needed: {water_needed_calculated}%")
    
    return water_needed_calculated

# MARK: main
def main():
    file_content = read_csv()
    
    # Using weather API
    temperature, humidity, wind_speed, weather = get_weather()
    rain_3h, rain_6h, rain_9h, rain_12h = get_rain_forecast()
    
    species_water_content = load_species_water_content()
    
    # print(species_water_content)
    
    # for _ in range(5):
    #     movements()
        
    #     move_up()
    #     species, water_content, water_content_needed = camera_work()
    #     print("camera work done")
    #     moisture_value = read_sensor()
    #     move_down()

    for i in range(1, len(file_content)):
        execute_line(i)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result1 = executor.submit(get_moisture)
            result2 = executor.submit(camera_work)
            
            moisture_value = result1.result()
            species, water_content, water_content_needed = result2.result()
        
        water_needed_calculated = get_water_needed(species, moisture_value, temperature, humidity, rain_3h, rain_6h, rain_9h, rain_12h, water_content, water_content_needed, species_water_content)
        
        # Using water pump
        water(water_needed_calculated)
        
        # Using Blynk
        send_data_to_blynk(moisture_value, species, water_content, water_needed_calculated)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("User Interupted in main file")
    except Exception as e:
        print(f"Error in main file: {e}")
    finally:
        GPIO.cleanup()
        print("Program ended")
