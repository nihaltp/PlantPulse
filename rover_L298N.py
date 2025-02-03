# rover_L298N.py
"""
    Code that controls the movement of the robot
    Uses 2 BTS motor drivers
    
    Opens movements.txt
    Uses predefined distances to move the robot
    Uses predefined angles to turn the robot
"""

import csv
import RPi.GPIO as GPIO
from time import sleep

# Motor driver pins
IN1: int = 36 # TODO: Change pin
IN2: int = 11 # TODO: Change pin
ENA: int = 12 # TODO: Change pin
IN3: int = 35 # TODO: Change pin
IN4: int = 38 # TODO: Change pin
ENB: int = 40 # TODO: Change pin

# Setup GPIO mode and pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Initialize PWM
pwm_ENA = GPIO.PWM(ENA, 1000)
pwm_ENB = GPIO.PWM(ENB, 1000)

# Predefined distances and angles
DISTANCE_TIME = 1  # Define your multiplier of distance # TODO: Change value
ANGLE_TIME = 1     # Define your multiplier of angle    # TODO: Change value
SPEED = 30                                              # TODO: Change value

# MARK: Movement
# Function to stop the robot
def stop(duration : int = 0):
    print(f"Stopping for {duration} seconds")
    pwm_ENA.start(0)
    pwm_ENB.start(0)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    sleep(duration)

# Function to move the robot forward
def move_forward(duration : int = 2):
    print(f"Moving forward for {duration} seconds")
    pwm_ENA.start(SPEED)
    pwm_ENB.start(SPEED)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    sleep(duration)
    stop()

# Function to move the robot backward
def move_backward(duration: int = 1):
    print(f"Moving backward for {duration} seconds")
    pwm_ENA.start(SPEED)
    pwm_ENB.start(SPEED)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    sleep(duration)
    stop()

# Function to turn the robot left
def move_left(duration: int = 1):
    print(f"Turning left for {duration} seconds")
    pwm_ENA.start(SPEED)
    pwm_ENB.start(SPEED)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    sleep(duration)
    stop()

# Function to turn the robot right
def move_right(duration : int = 2):
    print(f"Moving right for {duration} seconds")
    pwm_ENA.start(100)
    pwm_ENB.start(100)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    sleep(duration)

# MARK: File handling
# Function to read the entire CSV file
def read_csv(file_path: str = 'movements/movements.csv'):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        return data[1:]

# Function to return a specific line from the CSV file
def get_csv_line(file_content, line_number: int):
    if 0 <= line_number < len(file_content):
        return file_content[line_number]
    raise IndexError("\n\033[31mLine number out of range\033[0m")

# MARK: Execution
# Function to execute movements based on CSV line content
def execute_movements(line: list):
    try:
        line = line[1:]
        line = [item for item in line if item]
        for action in line:
            direction, duration = action.split(':')
            direction = direction.lower().strip()
            duration = int(duration)
            if direction == 'forward':
                move_forward(duration)
            elif direction == 'backward':
                move_backward(duration)
            elif direction == 'left':
                move_left(duration)
            elif direction == 'right':
                move_right(duration)
            elif direction == 'stop':
                stop(duration)
            else:
                print(f"\n\033[31mUnknown action: {direction}\033[0m")
    except ValueError:
        print("\n\033[31mError: Invalid duration value\033[0m")
    except Exception as e:
        print(f"\033[31mAn error occurred: {e}\033[0m")
    finally:
        stop()

def execute_line(line_number: int, file_content = None, file_name : str = 'movements/movements.csv'):
    line_number -= 1
    if file_content is None:
        file_content = read_csv(file_name)
    line = get_csv_line(file_content, line_number)
    if line is not None:
        execute_movements(line)
    else:
        print(f"\033[31mError: Invalid line number {line_number} in the CSV file.\033[0m")

def main(file_name: str = 'movements/movements.csv'):
    file_content = read_csv(file_name)
    for line_number in range(1, len(file_content)):
        yield execute_line(line_number, file_content)

if __name__ == "__main__":
    try:
        i = 0
        file_content = read_csv()
        while i < len(file_content):
            for _ in main():
                i += 1
    except KeyboardInterrupt:
        print("\033[32mExiting...\033[0m")
    except Exception as e:
        print(f"\033[31mError: {e}\033[0m")
    finally:
        stop()
        GPIO.cleanup()
