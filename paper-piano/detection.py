import cv2
import mediapipe as mp
import numpy as np
from cv2.typing import MatLike

_mp_drawing = mp.solutions.drawing_utils
_mp_hands = mp.solutions.hands

class Keypoint:
    def __init__(self, hand: str, number: int, position: tuple[float, float]):
        self.hand = hand
        self.number = number
        self.position = position

class PianoDetection:
    def __init__(self):
        # Frame procces steps
        self.frame_gray = None
        self.frame_blur = None
        self.frame_bin = None

        self.paper_approx = None

        # 200x200 is a starting size of warped image
        self.paper_warp = np.zeros((*(200, 200), 3), dtype=np.uint8)
        self.paper_warp_bin = np.zeros((*(200, 200), 1), dtype=np.uint8)
        
        # Detected piano points
        self.piano_points = []

    def process(self, frame: MatLike, blur: int, canny_th1: int, canny_th2: int):
        """
        Detects paper in a frame, and sets steps of proccessing to a attributes.
        Returns true if paper was found, otherwise false.
        """
        self.frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.frame_blur = cv2.GaussianBlur(self.frame_gray, (blur, blur), 0)
        self.frame_bin = cv2.Canny(self.frame_blur, canny_th1, canny_th2, L2gradient=True)
        kernel = np.ones((4,4),np.uint8)
        self.frame_bin = cv2.morphologyEx(self.frame_bin, cv2.MORPH_DILATE, kernel)

        contours, _ = cv2.findContours(self.frame_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # No contour was found
        if not contours:
            self.paper_approx = None
            return

        # Finds largest rectangle
        self.paper_approx = find_largest_rectangle(contours, 0.01)

        # No rectangle was found
        if self.paper_approx is None:
            return

        # Source points for 4 point transform
        src_points = self.paper_approx.copy().reshape((4, 2))
        src_points = order_points(src_points)
        
        # Calculates dimensions for warped image
        width = int(cv2.norm(src_points[0], src_points[1]))
        height = int(cv2.norm(src_points[0], src_points[3]))
        
        # Destination points
        dst_points = np.array(
            [[0, 0], # Top left
             [width, 0], # Top right
             [width, height], # Bottom right
             [0, height]], # Bottom left
            dtype="float32"
        )

        # Computes the perspective transformation matrix
        transform_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # Creates warped image
        self.paper_warp = cv2.warpPerspective(frame, transform_matrix, (width, height))
        
        # Preperes warped image for extracting points
        extraction = cv2.cvtColor(self.paper_warp, cv2.COLOR_BGR2GRAY)
        extraction = cv2.GaussianBlur(extraction, (11, 11), 2)
        extraction = cv2.adaptiveThreshold(extraction,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY_INV,11,2)
        kernel = np.ones((5,5),np.uint8)
        extraction = cv2.morphologyEx(extraction, cv2.MORPH_OPEN, kernel)
        
        # Removes unwanted edges
        extraction = add_inside_border(extraction, 10)
        
        # Thicken cirles to make them easier to detect
        kernel = np.ones((3,3),np.uint8)
        extraction = cv2.morphologyEx(extraction, cv2.MORPH_DILATE, kernel)
        
        # Assign final binary form 
        self.paper_warp_bin = extraction
        
        contours, _ = cv2.findContours(self.paper_warp_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # No contour was found
        if not contours:
            return
        
        # Finds centers of points
        points = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filters small leftovers 
            if w > 6 and h > 6:
                points.append((x+w/2, y+h/2))
        
        # No points detected
        if not points:
            return
        
        # Reshapes points for transform
        points = np.array(points, np.float32).reshape(-1, 1, 2)

        # Computes inverse matrix
        inverse_matrix = np.linalg.inv(transform_matrix)

        # Applies the inverse perspective transformation to map points back to the original image
        original_points = cv2.perspectiveTransform(points, inverse_matrix)
        original_points = original_points.reshape(-1, 2)
        
        # Assign sorted points by x axis
        original_points = [tuple(row) for row in original_points.astype(object)]
        self.piano_points = sorted(original_points, key=lambda pt: pt[0])

    def draw_contour(self, img: MatLike):
        """Draws contour and vertices of detected paper, if exists"""
        if self.paper_approx is None:
            return

        # Draws green contour
        cv2.drawContours(img, [self.paper_approx], -1, (0, 255, 0), 2)
        # Draws red vetices
        for point in self.paper_approx:
            cv2.circle(img, tuple(point[0]), 5, (0, 0, 255), -1)
    
    def draw_points(self, img: MatLike, labeled: bool = True):
        """Draws original points, if exists"""
        if self.piano_points is None:
            return
        
        # Draws circles
        for point in self.piano_points:
            cv2.circle(img, (int(point[0]), int(point[1])), 5, (255, 0, 0), -1)
            
        if labeled:
            # Define the text and properties
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            color = (255, 0, 0)
            thickness = 2
            
            i = 0
            # Draws text
            for point in self.piano_points:
                text = str(i)
                position = (int(point[0]-10), int(point[1]-10))
                cv2.putText(img, text, position, font, font_scale, color, thickness)
                i+=1
   
    
def order_points(pts: MatLike) -> MatLike:
    """Orders 4 points to be in clockwise order starting from top left"""
    ordered_points = np.zeros((4, 2), dtype="float32")

    # sort points along x axis
    x_sort = sorted(pts, key=lambda pt: pt[0])

    # Two points with lowest x values will be the ones on the left edge
    ordered_points[0] = min(x_sort[0], x_sort[1], key=lambda pt: pt[1])  # Top left has hihger y
    ordered_points[3] = max(x_sort[0], x_sort[1], key=lambda pt: pt[1])  # Bottom left has lower y

    # Two points with highest x values will be the ones on the right edge
    ordered_points[1] = min(x_sort[2], x_sort[3], key=lambda pt: pt[1])  # Top right has hihger y
    ordered_points[2] = max(x_sort[2], x_sort[3], key=lambda pt: pt[1])  # Bottom right has lower y

    # return the ordered coordinates
    return ordered_points

def find_largest_rectangle(contours: MatLike, epsilon_mult: float) -> MatLike:
    """Finds largest contour by bounding box"""
    max_area = 0
    largest_rect = None
    for contour in contours:
        approx = approximate_contour(contour, epsilon_mult)
        area = cv2.contourArea(approx)

        if area > max_area and cv2.isContourConvex(approx) and len(approx) == 4:
            max_area = area
            largest_rect = approx

    return largest_rect

def approximate_contour(contour: MatLike, epsilon_mult: float) -> MatLike:
    """Approximates the contour to reduce the number of points"""
    epsilon = epsilon_mult * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    return approx

def add_inside_border(img: MatLike, width: int) -> MatLike:
    """Adds inside black border of specified width"""
    img_cpy = img.copy()
    img_cpy[:width, :] = 0
    img_cpy[-width:, :] = 0
    img_cpy[:, :width] = 0
    img_cpy[:, -width:] = 0
    
    return img_cpy