import cv2
import detection
import validation
import control_panel
from playsound import playsound
import threading
import numpy as np


def main():
    # Creates video capture 
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Creates control panel
    ctrls = control_panel.ControlPanel()
    
    # Creates detectors and validator
    piano_det = detection.PianoDetection()
    hand_det = detection.HandDetection()
    validator = validation.TouchValidator()

    while True:
        # Update controls
        ctrls.update()
        
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        # Preapre frame for processing
        frame = cv2.flip(frame, 1)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # RGB for mediapipe
        
        # Detect piano points
        if not ctrls.freeze_points.get():
            piano_det.process(frame, ctrls.blur.get()*2+1, ctrls.canny_ths1.get(), ctrls.canny_ths2.get())
        
        # Detect finger points
        hand_det.process(frameRGB, ctrls.tracked_fingers)
        
        # Check which points should play sound
        indexes = validator.process(piano_det.piano_points, hand_det.fingertips, 
                                    ctrls.touch_distance.get(), ctrls.untouch_distance.get())
    
        # Play sounds
        for i in indexes:
            # Starts a thread with sound to not block the loop execution
            thread = threading.Thread(target=playsound, args=(f"../sounds/{i}.mp3",), daemon=True)
            thread.start()
            
        # Draws points and landmarks on original frame
        piano_det.draw_contour(frame)
        piano_det.draw_points(frame)
        hand_det.draw_landmarks(frame)
            
        # Converts biary from greyscale to rgb to stack them with color image
        main_bin_rgb = cv2.cvtColor(piano_det.frame_bin ,cv2.COLOR_GRAY2BGR)
        warped_bin_rgb = cv2.cvtColor(piano_det.paper_warp_bin ,cv2.COLOR_GRAY2BGR)
        
        # Stacks images
        display_main = np.hstack((frame, main_bin_rgb))
        display_warped = np.hstack((piano_det.paper_warp, warped_bin_rgb))
        
        # Displays images
        cv2.imshow("Main", display_main)
        cv2.imshow("Warped", display_warped)
        
        # Quit when q pressed
        if cv2.waitKey(1) == ord('q'):
            ctrls.quit()
            break        

if __name__ == "__main__":
    main()