# moisture_sensor.py
"""
    Uses sensor_movement.py to move moisture sensor
    -> lowers the moisture sensor to get moisture value
    -> gets the moisture value using ADS1115 ADC
    -> raises the moisture sensor
"""

# Functions to move sensor
from sensor_movement import move_up, move_down, stop_motor

import RPi.GPIO as GPIO
import Adafruit_ADS1x15
from time import sleep

# Initialize the ADS1115 ADC on bus 1
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

# MARK: Read Sensor
def read_sensor(channel: int = 0, GAIN: int = 1):
    """
    Reads the ADS1115 ADC
    :param channel: The channel to read from (0-3)
    :return: The moisture value in percentage
    
    Output is a 16-bit value
    It will be between 0 and 32767
    """
    
    value = adc.read_adc(channel, gain=GAIN)
    value = (value/32767) * 100
    value = round(value, 2)
    return value

# MARK: Get Moisture
def get_moisture(moisture_duration: int= 2, movement_duration: int= 2, speed: int= 100):
    try:
        # Lower the sensor
        print("Lowering the sensor...")
        move_down(movement_duration, speed)
        
        # Measure the moisture
        print(f"Waiting for {moisture_duration} seconds to settle moisture sensor...")
        sleep(moisture_duration)
        moisture_value = read_sensor()
        print(f"Moisture Value: {moisture_value}")
        
        # Raise the sensor
        print("Raising the sensor...")
        move_up(movement_duration, speed)
        
        return moisture_value
    
    except Exception as e:
        print(f"\n\033[31mAn error occurred: {e}\033[0m")
    
    finally:
        # Stop the motor and cleanup GPIO
        print("\033[32mStopping the motors...\033[0m")
        stop_motor()

if __name__ == "__main__":
    try:
        while True:
            get_moisture()
            sleep(1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Stopping the robot.")
    except Exception as e:
        print(f"\n\033[31mAn error occurred: {e}\033[0m")
    finally:
        GPIO.cleanup()
