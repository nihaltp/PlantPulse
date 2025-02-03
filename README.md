# Plant Pulse

This is a project where instead of using n number of sensors to detect the health of a plant, we use a single sensor to detect the moisture level of the plant. We will use a camera to detect the health and species of the plant as well. After processing the data, we will upload the data to blynk. Using the data we will calculate the water required for the plant and provide water accordingly.

## Table of Contents

- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Circuit Diagrams](#circuit-diagram)
- [Troubleshooting](#troubleshooting)

## Features

- Preprogrammed Path (using a csv file)
- Blynk integration
- Camera integration
- => Plant health monitoring
- => Plant species detection
- Moisture sensor integration
- Watering system integration

## Hardware Requirements

- Raspberry Pi
- Moisture sensor
- ADC (ADS1115)
- Camera
- Motors for the robot
- Motor for sensor movement
- Motor drivers
- Water pump
- Power supply
- Breadboard
- Jumper wires

## Software Requirements

- Python 3.x and required libraries

## Setup

1. Clone the repository: `git clone https://github.com/your-username/PlantPulse.git`
2. Install the required libraries: `pip install -r requirements.txt`
3. Configure the path - movements.csv
4. Configure the Blynk
5. Configure the Openwheathermap API
6. Configure the camera
7. Connect the components as per the circuit diagram
8. Connect the motors and motor driver
9. Connect the ADC and moisture sensor
10. Connect the water pump and power supply
11. Connect the camera and power supply
12. Configure motor and motor drivers
13. Run the script: `python PlantPulse.py`

## Configuration

Before running the code:

1. Update the `movements.csv` file with the desired movement commands.
2. Update the `.env` file with your Blynk token and OpenWeatherMap API key.
3. Update the pin numbers for the motors and motor driver.
4. Update the pin numbers for the ADC and moisture sensor.
5. Update the pin numbers for the water pump and power supply.
6. Update the port number for the camera.

## Usage

1. Run the code: `python PlantPulse.py`
2. The code will start the robot and the sensor.
3. The robot will move according to the commands in the `movements.csv` file.
4. The robot will stop when the robot reaches the destination.
5. The sensor will measure the moisture level and send the data to the Blynk app.
6. The camera will detect the species and health of the plant and send the data to the Blynk app.
7. The water pump will water the plant according to the moisture level.

## Circuit Diagram

![Motor Driver Circuit](circuit/motor_driver.png)
![Sensor Circuit](circuit/sensor.png)
![Water Pump Circuit](circuit/water_pump.png)

## Troubleshooting

If the code doesn't work, check the following:

- Make sure the motors and motor driver are connected correctly.
- Make sure the ADC and moisture sensor are connected correctly.
- Make sure the water pump and power supply are connected correctly.
- Make sure the camera and power supply are connected correctly (update the camera port).
- Make sure the Blynk token and OpenWeatherMap API key are correct.
- Make sure the `movements.csv` file is correct.
- Verify motor direction if the robot moves in the wrong direction.
