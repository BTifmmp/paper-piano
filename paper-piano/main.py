import cv2
import detection
import validation
from playsound import playsound
import threading
import numpy as np

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    piano_det = detection.PianoDetection()
    controls = detection.PianoDetectionControls(piano_det)
    controls.show_trackbars("Trackbars")

    # Create a trackbar with binary values
    cv2.createTrackbar('Binary Value', 'Trackbars', 1, 1, lambda x: None)

    hand_det = detection.HandDetection()
    validator = validation.TouchValidator()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        frame = cv2.flip(frame, 1)
        frameRGB = cv2.cvtColor(frame ,cv2.COLOR_BGR2RGB)
        
        binary_value = cv2.getTrackbarPos('Binary Value', 'Trackbars')
        if binary_value:
            piano_det.process(frame)
        
        hand_det.process(frameRGB, [8, 12, 16]) #Starting from thumb 4, 6, 12, 16, 20
        
        indexes = validator.process(piano_det.points_og, hand_det.fingertips, 10, 10)
        
        piano_det.draw_contour(frame)
        piano_det.draw_points_og(frame)
        hand_det.draw_landmarks(frame)
        

        # Sounds
        for i in indexes:
            print(indexes)
            thread = threading.Thread(target=playsound, args=(f"../sounds/{i}.mp3",), daemon=True)
            thread.start()
            
        # Display
        main_bin_rgb = cv2.cvtColor(piano_det.frame_bin ,cv2.COLOR_GRAY2BGR)
        warped_bin_rgb = cv2.cvtColor(piano_det.paper_warp_bin ,cv2.COLOR_GRAY2BGR)
        
        display_main = np.hstack((frame, main_bin_rgb))
        display_warped = np.hstack((piano_det.paper_warp, warped_bin_rgb))
                
        cv2.imshow("Main", display_main)
        cv2.imshow("Warped", display_warped)
        
        if cv2.waitKey(1) == ord('q'):
            break
        

if __name__ == "__main__":
    main()