import cv2
from cv2.typing import MatLike
import numpy as np
import mediapipe as mp

_mp_drawing = mp.solutions.drawing_utils
_mp_hands = mp.solutions.hands

class Keypoint:
    def __init__(self, hand: str, number: int, position: tuple[float, float]):
        self.hand = hand
        self.number = number
        self.position = position

class PianoDetection:
    def __init__(self, blur: int = 15, canny_th1: int = 10, canny_th2: int = 30):
        self.frame_gray = None
        self.frame_blur = None
        self.frame_bin = None

        self.paper_bbox = None
        self.paper_approx = None

        self.warped_size = (300, 300)
        self.transform_matrix = None
        self.paper_warp = np.zeros((*self.warped_size, 3), dtype=np.uint8)
        self.paper_warp_bin = np.zeros((*self.warped_size, 1), dtype=np.uint8)
        
        self.points_warped = []
        self.points_og = []
        
        self.blur = blur
        self.canny_th1 = canny_th1
        self.canny_th2 = canny_th2

    def process(self, frame: MatLike):
        """
        Detects paper in a frame, and sets steps of proccessing to a attributes.
        Returns true if paper was found, otherwise false.
        """
        self.frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.frame_blur = cv2.GaussianBlur(self.frame_gray, (self.blur, self.blur), 0)
        self.frame_bin = cv2.Canny(self.frame_blur, self.canny_th1, self.canny_th2, L2gradient=True)
        kernel = np.ones((4,4),np.uint8)
        self.frame_bin = cv2.morphologyEx(self.frame_bin, cv2.MORPH_DILATE, kernel)

        contours, _ = cv2.findContours(self.frame_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # No contour was found
        if not contours:
            self.paper_bbox = None
            self.paper_approx = None
            return

        # Finds largest rectangle
        self.paper_approx = _find_largest_rectangle(contours, 0.01)
        print(self.paper_approx)

        # No rectangle was found
        if self.paper_approx is None:
            return

        # Source points for 4 point transform
        src_points = self.paper_approx.copy().reshape((4, 2))
        src_points = _order_points(src_points)
        
        # Calculates dimensions for warped image
        width = int(cv2.norm(src_points[0], src_points[1]))
        height = int(cv2.norm(src_points[0], src_points[3]))
        self.warped_size = (width, height)
        
        # Destination points
        dst_points = np.array(
            [[0, 0], # Top left
             [self.warped_size[0], 0], # Top right
             [self.warped_size[0], self.warped_size[1]], # Bottom right
             [0, self.warped_size[1]]], # Bottom left
            dtype="float32"
        )

        # Computes the perspective transformation matrix
        self.transform_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # Creates warped image
        self.paper_warp = cv2.warpPerspective(frame, self.transform_matrix, self.warped_size)
        
        # Preperes warped image for extracting points
        extraction = cv2.cvtColor(self.paper_warp, cv2.COLOR_BGR2GRAY)
        extraction = cv2.GaussianBlur(extraction, (11, 11), 2)
        extraction = cv2.adaptiveThreshold(extraction,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY_INV,11,2)
        kernel = np.ones((4,4),np.uint8)
        extraction = cv2.morphologyEx(extraction, cv2.MORPH_OPEN, kernel)
        
        # Removes unwanted edges
        extraction = _add_inside_border(extraction, 15)
        
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
        
        # Assign points sorted along x axis
        self.points_warped = sorted(points, key=lambda pt: pt[0])
        
        # Reshapes points for transform
        points = np.array(points, np.float32).reshape(-1, 1, 2)

        # Computes inverse matrix
        inverse_matrix = np.linalg.inv(self.transform_matrix)

        # Applies the inverse perspective transformation to map points back to the original image
        original_points = cv2.perspectiveTransform(points, inverse_matrix)
        original_points = original_points.reshape(-1, 2)
        
        # Assign sorted points by x axis
        original_points = [tuple(row) for row in original_points.astype(object)]
        self.points_og = sorted(original_points, key=lambda pt: pt[0])

    def draw_bbox(self, img: MatLike):
        """Draws bounding box of detected paper, if exists"""
        if self.paper_bbox is None:
            return

        # Draws green rectangle
        cv2.rectangle(img, self.paper_bbox[:2], np.add(self.paper_bbox[:2], self.paper_bbox[2:]), (0, 255, 0), 2)

    def draw_contour(self, img: MatLike):
        """Draws contour and vertices of detected paper, if exists"""
        if self.paper_approx is None:
            return

        # Draws green contour
        cv2.drawContours(img, [self.paper_approx], -1, (0, 255, 0), 2)
        # Draws red vetices
        for point in self.paper_approx:
            cv2.circle(img, tuple(point[0]), 5, (0, 0, 255), -1)

    def draw_points_warped(self, img: MatLike):
        """Draws warped points, if exists"""
        if self.points_warped is None:
            return
        
        for point in self.points_warped:
            cv2.circle(img, point, 5, (255, 0, 0), -1)
    
    def draw_points_og(self, img: MatLike):
        """Draws original points, if exists"""
        if self.points_og is None:
            return
        
        # Define the text and properties
        text = ""
        position = None # Bottom-left corner of the text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        color = (255, 0, 0)  # White color in BGR
        thickness = 2
        i = 0  
        for point in self.points_og:
            text = str(i)
            position = (int(point[0]-10), int(point[1]-10))
            cv2.circle(img, (int(point[0]), int(point[1])), 5, (255, 0, 0), -1)
            cv2.putText(img, text, position, font, font_scale, color, thickness)
            i+=1


class PianoDetectionControls:
    def __init__(self, piano_detection: PianoDetection):
        self.piano_detection = piano_detection

    def show_trackbars(self, window_name: str):
        "Creates a windows with trackbars for configurable values of PianoDetection"
        cv2.namedWindow(window_name)
        cv2.createTrackbar("Blur Strenght", window_name, self.piano_detection.blur, 30, self._blur_change)
        cv2.createTrackbar(
            "Canny threschold1", window_name, self.piano_detection.canny_th1, 200, self._canny_th1_change
        )
        cv2.createTrackbar(
            "Canny threschold2", window_name, self.piano_detection.canny_th2, 200, self._canny_th2_change
        )

    def _blur_change(self, val):
        if val % 2 == 1:  # Only odd values are valid
            self.piano_detection.blur = val

    def _canny_th1_change(self, val):
        self.piano_detection.canny_th1 = val

    def _canny_th2_change(self, val):
        self.piano_detection.canny_th2 = val


class HandDetection:
    def __init__(self):
        self.fingertips = []
        self.hands = _mp_hands.Hands(
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
            )
        self.results = None
        
    def process(self, frame: MatLike, fingertips: list[int] = [8]):
        """Extracts fingertips data from the frame"""
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        self.results = self.hands.process(frame)
        
        # Reset fingertips
        self.fingertips = []
        
        # Procces detected hands
        if self.results.multi_hand_landmarks:
            for landmarks, handedness in zip(self.results.multi_hand_landmarks, self.results.multi_handedness):
                hand_type = handedness.classification[0].label
                for tip in fingertips:
                    landmark = landmarks.landmark[tip]
                    
                    # Find positon on frame
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    
                    # Create new keypoint
                    new_tip = Keypoint(hand_type, tip, (x,y))
                    self.fingertips.append(new_tip)
            
    def draw_landmarks(self, img):
        """
        Draws default hands landmarks
        """
        if not self.results.multi_hand_landmarks:
            return
        
        for landmarks in self.results.multi_hand_landmarks:
            _mp_drawing.draw_landmarks(img, landmarks, _mp_hands.HAND_CONNECTIONS)
    
    
def _order_points(pts: MatLike) -> MatLike:
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

def _find_largest_rectangle(contours: MatLike, epsilon_mult: float) -> MatLike:
    """Finds largest contour by bounding box"""
    max_area = 0
    largest_rect = None
    for contour in contours:
        approx = _approximate_contour(contour, epsilon_mult)
        area = cv2.contourArea(approx)

        if area > max_area and cv2.isContourConvex(approx) and len(approx) == 4:
            max_area = area
            largest_rect = approx

    return largest_rect

def _approximate_contour(contour: MatLike, epsilon_mult: float) -> MatLike:
    """Approximates the contour to reduce the number of points"""
    epsilon = epsilon_mult * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    return approx

def _add_inside_border(img: MatLike, width: int) -> MatLike:
    """Adds inside black border of specified width"""
    img_cpy = img.copy()
    img_cpy[:width, :] = 0
    img_cpy[-width:, :] = 0
    img_cpy[:, :width] = 0
    img_cpy[:, -width:] = 0
    
    return img_cpy