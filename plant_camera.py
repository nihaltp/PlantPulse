# plant_camera.py
"""
    Code that controls the camera
    
    Uses camera to detect leaves of different species
    -> loads images from species folder
    -> detects leaves
    -> finds species
    -> finds water needed according to species
    
    Uses camera to estimate water content of leaves
    -> uses the color of leaves according to species to estimate water content
"""

import os
import cv2
import json
import numpy as np
from time import time
from picamera2 import Picamera2
from concurrent.futures import ThreadPoolExecutor

class PlantCam:
    # MARK: init
    def __init__(self) -> None:
        self.showVideo : bool = True # TODO: Change
        
        # Minimum area threshold to filter small contours
        # Adjust this value based on your use case 
        self.MIN_CONTOUR_AREA : int = 1000 # TODO: Change

        self.save_folder = 'captured_images'
        
        self.species_folder : str = "species"
        self.species : str = ""
        self.score : float = 0.0
        self.water_content : float = 0.0
        self.water_content_needed : float = 0.0
        
        # Initialize the camera using Picamera2
        self.camera = Picamera2()
        self.video_config = self.camera.create_video_configuration()
        self.camera.configure(self.video_config)
        self.camera.start()
        
        self.load_species_colors()
        self.load_species_water_content()
        self.load_species_images()
        
        os.makedirs(self.save_folder, exist_ok=True)
    
    # MARK: Load Species Colors
    def load_species_colors(self):
        # Load species colors from JSON file
        with open("config/hsv.json", "r") as file:
            species_colors = json.load(file)
            file.close()
        self.species_colors = {
            species: (np.array(color_range[0]), np.array(color_range[1])) for species, color_range in species_colors.items()
        }
        print(f"Species Colors: {self.species_colors}")
    
    # MARK: Load Water Content
    def load_species_water_content(self):
        # Load species water content from JSON file
        with open("config/species_values.json", "r") as file:
            species_water_content = json.load(file)
            file.close()
        self.species_water_content = species_water_content
    
    # MARK: Load Species Images
    def load_species_images(self):
        """
        Load species images from the specified folder.
        """
        print(f"species_folder: {self.species_folder}")
        
        species_templates = {}
        with ThreadPoolExecutor() as executor:
            futures = []
            for file_name in os.listdir(self.species_folder):
                file_name = file_name.lower()
                if file_name.endswith((".png", ".jpg", ".jpeg")):
                    futures.append(executor.submit(self.load_single_image, file_name))
            for future in futures:
                species_name, image = future.result()
                species_templates[species_name] = image
        self.species_templates = species_templates
    
    # MARK: Load Single Image
    def load_single_image(self, file_name):
        """
        Load a single image and return its species name and image.
        """
        species_folder = self.species_folder
        species_name = os.path.splitext(file_name)[0]
        image = cv2.imread(os.path.join(species_folder, file_name), cv2.IMREAD_COLOR)
        return species_name, image
    
    # MARK: Save image
    def save_image(self, frame):
        # Save the image
        filename = f"{self.save_folder}/captured_frame_{int(time.time())}.png"
        cv2.imwrite(filename, frame)
        print(f"Image saved as {filename}")
    
    # MARK: Water content
    def calculate_water_content(self, species, hue, saturation):
        """
        Calculate water content based on hue and saturation.
        Adjust the equation based on your experiment.
        """
        if species not in self.species_water_content:
            print(f"Unknown species: {species}")
            return None
        
        return self.species_water_content[species][0] * hue + self.species_water_content[species][1] * saturation + self.species_water_content[species][2]
    
    # MARK: Matching species
    def find_matching_species(self, leaf_crop):
        """
        Compare the given cropped leaf image with species templates and find the best match.
        """
        best_match = None
        best_score = float('inf')
        
        for species, template in self.species_templates.items():
            if template is None:
                continue
            
            # Resize template to match the leaf crop dimensions
            resized_template = cv2.resize(template, (leaf_crop.shape[1], leaf_crop.shape[0]))
            
            # Compute Mean Squared Error (MSE) between images
            mse = np.mean((leaf_crop.astype("float") - resized_template.astype("float")) ** 2)
            
            if mse < best_score:
                best_score = mse
                best_match = species
        
        if best_match is None:
            best_match =  "Unknown"
        self.species = best_match
        self.score = best_score
        print(f"Best Match: {best_match}, Best Score: {best_score}")
    
    # MARK: Process Species Mask
    def process_species_mask(self, args):
        """
        Process the mask for a single species.
        """
        hsv, species, color_range = args
        try:
            lower = np.array(color_range[0], dtype=np.uint8)
            upper = np.array(color_range[1], dtype=np.uint8)
            # lower, upper = color_range
            mask = cv2.inRange(hsv, lower, upper)
            found_contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            return species, found_contours
        except Exception as e:
            print(f"Error processing species '{species}': {e}")
            return species, []
    
    # MARK: Process Frame
    def process_frame(self, frame):
        """
        Process a single frame to detect leaves of different species and estimate water content.
        """
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        results = []
        
        for species, color_range in self.species_colors.items():
            species, contours = self.process_species_mask((hsv, species, color_range))
            print(f"Species: {species}, Contours: {len(contours)}")
            
            # Filter contours by size
            contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= self.MIN_CONTOUR_AREA]
            print(f"Species: {species}, Filtered Contours: {len(contours)}")
            
            results.append((species, contours))
        
        contours = []
        for species, species_contours in results:
            contours.extend(species_contours)
            mask = cv2.inRange(hsv, *self.species_colors[species])
        
        if self.showVideo:
            cv2.imshow("Green Mask", mask)
        
        if not contours:
            return frame
        
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        cropped_leaf = frame[y:y + h, x:x + w]
        cropped_hsv = hsv[y:y + h, x:x + w]
        
        # Find matching species from folder
        self.find_matching_species(cropped_leaf)
        print(f"Species: {self.species}, Score: {self.score}")
        
        if self.showVideo:
            # Display the cropped leaf for debugging
            cv2.imshow(f"{self.species} Cropped Leaf", cropped_leaf)
        
        mean_color = cv2.mean(cropped_hsv, mask=mask[y:y + h, x:x + w])
        hue, saturation, _ = mean_color[:3]
        hue, saturation = round(hue, 2), round(saturation, 2)
        
        # Estimate water content based on species
        self.water_content_needed = self.species_water_content.get(self.species, 0.0)
        print(f"Species {self.species} with {hue}, {saturation}")
        self.water_content = self.calculate_water_content(self.species, hue, saturation)
        
        if self.species == None:
            species = "Unknown"
        else:
            species = self.species
        
        if self.water_content == None:
            water_content = 0.0
        else:
            water_content = round(self.water_content, 2)
        
        print(f"Species: {species}, Water Content: {water_content}%")
        
        # Annotate the frame with the detected species and water content
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{species} : {water_content}%", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
    
    # MARK: Run
    def run(self):
        print("Press 'q' to exit the video feed.")
        try:
            while True:
                # Capture a frame from the camera
                frame = self.camera.capture_array()
                
                # Process the frame
                processed_frame = self.process_frame(frame)
                
                if self.showVideo:
                    # Display the frame with annotations
                    cv2.imshow("Leaf Water Content Estimation", processed_frame)
                
                # Save the image on 's' key
                if cv2.waitKey(1) & 0xFF == ord('s'):
                    self.save_image(frame)
                
                # Break loop on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Exiting video feed.")
                    break
            
        
        except KeyboardInterrupt:
            print("Video feed interrupted by user.")
        
        finally:
            # Cleanup
            cv2.destroyAllWindows()
            self.camera.stop()
            

if __name__ == "__main__":
    camera = PlantCam()
    camera.run()
