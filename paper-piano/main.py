from pathlib import Path
import cv2
import numpy as np
import detection
import control_panel
import piano_player
import validation


def main():
    # Creates video capture
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Creates control panel
    ctrls = control_panel.ControlPanel()
    
    # Creates detectors and validator
    piano_det = detection.PianoDetection()
    validator = validation.TouchValidator()
    
    # Sound player
    default_sounds_path = Path(__file__).parent.parent / "sounds"
    player = piano_player.PianoPlayer(default_sounds_path)
    
    wasFrozen = False
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
        
        if not ctrls.freeze_points.get():
            # Detect piano points
            piano_det.process(frame, ctrls.blur.get()*2+1, ctrls.canny_ths1.get(), ctrls.canny_ths2.get())
            wasFrozen = False
        else:
            if wasFrozen == False:
                wasFrozen = True
                validator.initialize_points_images(frame, piano_det.piano_points)
        # Check which points should play sound
        indexes = validator.process(frame, ctrls.match_threshold.get()/100)

        # Play sounds
        player.play_keys(len(piano_det.piano_points), indexes, piano_player.MIDDLE_SOUND_SELECTION)
            
        # Draws points and landmarks on original frame
        piano_det.draw_contour(frame)
        piano_det.draw_points(frame)
            
        # Converts biary from greyscale to rgb to stack them with color image
        main_bin_rgb = cv2.cvtColor(piano_det.frame_bin ,cv2.COLOR_GRAY2BGR)
        warped_bin_rgb = cv2.cvtColor(piano_det.paper_warp_bin ,cv2.COLOR_GRAY2BGR)
        
        # Stacks images
        display_main = np.hstack((frame, main_bin_rgb))
        display_warped = np.hstack((piano_det.paper_warp, warped_bin_rgb))
        
        # Displays images
        cv2.imshow("Main", display_main)
        cv2.imshow("Warped", display_warped)
        
        # Quit program if any control panel window is closed or q pressed     
        if cv2.waitKey(1) == ord('q') or ctrls.is_closed:
            ctrls.quit()
            break        

if __name__ == "__main__":
    main()