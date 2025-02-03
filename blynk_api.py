"""
    Code to send data from raspberry pi to blynk through api
    
    https://{server_address}/external/api/update?token={token}&{pin}={value}
    
    eg: https://blynk.cloud/external/api/update?token=ffujYGgbf805tgsf&v1=100
    
    https://{server_address}/external/api/batch/update?token={token}&{pin1}={value1}&{pin2}={value2}
    
    eg: https://blynk.cloud/external/api/batch/update?token=ffujYGgbf805tgsf&v1=100&v2=200
"""

import os
import requests
from time import sleep
from random import randint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Blynk authorization token
BLYNK_AUTH = os.getenv('BLYNK_AUTH_TOKEN')

# Virtual pins
MOISTURE = 0      # int
SPECIES = 1       # string
WATER_CONTENT = 2 # int
WATER_NEEDED = 3  # int

def get_sensor_data():
    return {
        "moisture": randint(0, 100),
        "species": "Rose",
        "water_content": randint(0, 100),
        "water_needed": randint(0, 100)
    }

def send_data_to_blynk(*data):
    for index, value in enumerate(data):
        url = f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH}&v{index}={value}"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"\n\033[31mError: Failed to send data to Blynk. Status code: {response.status_code}\033[0m")
            print(f"\033[31mData tried to send: {index} = {value}\n\033[0m")
            continue
    print("\033[32mAll data has been processed.\033[0m")

if __name__ == "__main__":
    try:
        while True:
            values = get_sensor_data().values()
            send_data_to_blynk(*values)
            sleep(1)
    except KeyboardInterrupt:
        print("\n\033[32mExiting...\033[0m")
    except Exception as e:
        print(f"\n\033[31mError: {e}\033[0m")
