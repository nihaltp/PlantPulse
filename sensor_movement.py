# sensor_movement.py
"""
    Code that controls the movement of the sensor
    
    Moves the sensor up and down as well as stop it
    Controlled using L298N Motor driver
"""

import RPi.GPIO as GPIO
from time import sleep

# Define GPIO pins for L298N Motor Driver
IN1: int = 26 # TODO: Change pin
IN2: int = 24 # TODO: Change pin
ENA: int = 21 # TODO: Change pin

# Define movement parameters
sensor_movement: int = 2  # TODO: Change value
movement_speed: int = 100 # TODO: Change value

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Initialize PWM on ENA pin
pwm = GPIO.PWM(ENA, 100)
pwm.start(0)

# MARK: Movement
def move_up(duration: int = sensor_movement, speed: int = movement_speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)
    print(f"Sensor Moving up for {duration} seconds at speed {speed}")
    sleep(duration)
    stop_motor()

def move_down(duration: int = sensor_movement, speed: int = movement_speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(speed)
    print(f"Sensor Moving down for {duration} seconds at speed {speed}")
    sleep(duration)
    stop_motor()

def stop_motor(duration: int= 0):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)
    print("Sensor Movement stopped")
    sleep(duration)

if __name__ == "__main__":
    move_up()
    move_down()
    stop_motor()
    GPIO.cleanup()
