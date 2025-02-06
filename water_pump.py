# water_pump.py
"""
    Code that controls the water pump using L298N Motor driver
    
    Turns on the water pump
    Waits for a certain amount of time
    Turns off the water pump
"""

import RPi.GPIO as GPIO
import time
import json

# MARK: Load pins
"""Load already selected pins from config.json."""
with open("config.json", "r") as f:
    config = json.load(f)
    f.close()

# Define GPIO pins for L298N Motor Driver
IN1 = config["WATER_PUMP"]["IN1"]
IN2 = config["WATER_PUMP"]["IN2"]
ENA = config["WATER_PUMP"]["ENA"]

# Setup GPIO mode
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Initialize PWM on ENA pin
pwm = GPIO.PWM(ENA, 1000)

# MARK: Functions
def turn_on_pump(PWM : int):
    pwm.start(PWM)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    print("Water pump is ON")

def turn_off_pump():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(ENA, 0)
    print("Water pump is OFF")

def water(seconds : int, PWM : int = 100):
    turn_on_pump(100) # TODO: change this
    time.sleep(0.25)  # TODO: change this
    turn_off_pump()
    
    start_time = time.time()
    while time.time() - start_time < seconds:
        turn_on_pump(PWM)
        time.sleep(0.005)
        turn_off_pump()

if __name__ == "__main__":
    try:
        water(10, 20) # TODO: change this
    except KeyboardInterrupt:
        print("\033[32mKeyboard Interrupt\033[0m")
    except Exception as e:
        print(f"\033[31mError: {e}\033[0m")
    finally:
        turn_off_pump()
        pwm.stop()
        GPIO.cleanup()
        print("Everything done")
