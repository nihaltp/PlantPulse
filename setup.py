import sys
import json

class Setup:
    # MARK: __init__
    def __init__(self) -> None:
        self.welcome()
        
        self.config_file = "config.json"
        self.default_file = "default_pins.json"
        
        # List of GPIO pins
        self.GPIO_PINS : list[int] = [3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 35, 36, 37, 38, 40]
        # TODO: Take the default pins from another file
        self.PINS_DEFAULT : dict[str, dict[str, int]] = self.load_pins(self.default_file)
        
        # List of available GPIO pins
        self.avalilable_pins : list[int] = self.GPIO_PINS
        self.PINS_USING : list[int] = []
        self.pins : dict[str, dict[str, int]] = self.load_pins(self.config_file)
        self.compare_pins()
        self.check_pins()
    
    # MARK: Welcome
    def welcome(self) -> None:
        print("\033[1;32m🚀 Welcome to the GPIO PIN setup!")
        print("This script will help you select the GPIO pins")
        print("\033[0m")
    
    # MARK: Load pins
    def load_pins(self, file) -> dict[str, dict[str, int]]:
        """Load already selected pins from config.json."""
        try:
            with open(file, "r") as f:
                config = json.load(f)
                f.close()
            return config
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
        
    # MARK: Compare pins
    def compare_pins(self) -> None:
        """Compare default pins with loaded pins and add missing pins to config.json."""
        save = False
        for category, pins in self.PINS_DEFAULT.items():
            if category not in self.pins:
                self.pins[category] = pins
                print(f"\033[32m✅ {category} pins added to {self.config_file}\033[0m")
                save = True
            else:
                for pin_name, pin_number in pins.items():
                    if pin_name not in self.pins[category]:
                        self.pins[category][pin_name] = pin_number
                        print(f"\033[32m✅ {pin_name} (GPIO {pin_number}) added to {category}\033[0m")
                        save = True
        
        if save:
            self.save_pins()
        
    # MARK: Check pins
    def check_pins(self)  -> None :
        error : bool = False
        
        for category, pins in self.pins.items():
            for pin, pin_number in pins.items():
                if pin_number not in self.GPIO_PINS:
                    print(f"❌ Invalid pin: {pin_number} for {category} : {pin}. Choose from {self.GPIO_PINS}")
                    error = True
                    break
                else:
                    if pin_number not in self.PINS_USING:
                        self.PINS_USING.append(pin_number)
                    else:
                        print(f"❌ Pin {pin_number} is already in use!")
                        error = True
                        break
        
        if not error:
            print("\033[32m✅ All pins are valid!\033[0m")
            check = input("Would you like to change the pins? ").lower().strip()
            if check == "yes" or check == "y":
                error = True
        
        if error:
            self.all_pins()
            self.save_pins()
        
        self.exit()
    
    # MARK: Save pins
    def save_pins(self) -> None:
        """Save selected pins to config.json."""
        config = self.pins
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)
        print("\033[32m✅ Pins saved successfully!\033[0m")
    
    # MARK: All pins
    def all_pins(self) -> None:
        self.avalilable_pins = self.GPIO_PINS
        
        for category, pins in self.PINS_DEFAULT.items():
            for pin_name, _ in pins.items():
                print(f"\n\033[32m✅ Available GPIO pins: {self.avalilable_pins}\033[0m")
                while True:
                    try:
                        pin = int(input(f"\033[33mSelect a pin for {category} - {pin_name} :\033[0m "))
                        if pin not in self.avalilable_pins:
                            print(f"\033[31m❌ Invalid pin: {pin}.\n Choose from {self.avalilable_pins}\033[0m")
                        else:
                            self.pins[category][pin_name] = pin
                            self.avalilable_pins.remove(pin)
                            break
                    except ValueError:
                        print("\033[31m❌ Invalid input. Please enter a valid integer.\033[0m")
                    except Exception as e:
                        print(f"\033[31m❌ {e}")
    
    # MARK: Exit
    def exit(self) -> None:
        print("\n\033[1;32m🚀You can change the pins later by running this script again.")
        print("Thanks for using the GPIO PIN setup!\033[0m")
        sys.exit()


if __name__ == "__main__":
    Setup()
