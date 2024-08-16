import cv2
from cv2.typing import MatLike
import numpy as np

class TouchValidator():
    def __init__(self, probbing_area: int = 6):
        self._probbing_area = probbing_area
        self._templates = []
        self._piano_points = []
        self._is_pressed = []
        
        self.test = []
    
    def initialize_points_images(self, frame: MatLike, piano_points: list[tuple[float, float]]):
        """Creates image for for every point to be used later as a template"""
        self._templates = []
        self._piano_points = piano_points
        
        height, width = frame.shape[:2]
    
        for pp in piano_points:
            # Initialize each point as not pressed
            self._is_pressed.append(False)
            
            # Points of cropping rectangle
            # Probbing is reduced to focus on the point
            x = int(max(0, pp[0] - self._probbing_area))
            y = int(max(3, pp[1] - self._probbing_area + 1))
            w = int(min(x + self._probbing_area * 2, width))
            h = int(min(y + (self._probbing_area - 1) * 2, height))
            
            # Crop frame
            cropped = np.copy(frame[y:h, x:w])
            self._templates.append(cropped)
        
    def process(self, frame: MatLike, match_threshold: float = 0.7) -> set[int]:
        """Detects piano points hidden behind finger, return indexes of those points """
        result = set() # Set of indicies
        height, width = frame.shape[:2] 
        for indx, pp in enumerate(self._piano_points):
            # Points of cropping rectangle
            x = int(max(0, pp[0] - self._probbing_area))
            y = int(max(0, pp[1] - self._probbing_area + 1))
            w = int(min(x + self._probbing_area * 2, width))
            h = int(min(y + (self._probbing_area - 1) * 2, height))
            
            # Crop frame
            cropped = np.copy(frame[y:h, x:w])
            
            # Tries to match a point to corresponding cropped frame
            # If point is not detected it means there in no finger over it
            is_point_detected, image = self._is_template_in_image(cropped, self._templates[indx], match_threshold)
            
            if is_point_detected:
                if not self._is_pressed[indx]:
                    # Point was not detected and wasnt previously pressed
                    result.add(indx)
                    self._is_pressed[indx] = True
            else:
                # Point was detected
                self._is_pressed[indx] = False            
        
        return result    
    
    def _is_template_in_image(self, image, template, threshold=0.7):
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        
        # Get the maximum match value
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        # If the maximum match value is above the threshold, the object is present
        if max_val >= threshold:
            return False, result  # Point is present
    
        return True, result  # No Point detected