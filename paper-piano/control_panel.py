import tkinter as tk

class ControlPanel(tk.Tk):
    def __init__(self):
        """Creates a new tk window with controls for piano detection validation"""
        super().__init__()
        
        # Controlable variables
        self.freeze_points = tk.BooleanVar(value=False)
        self.blur = tk.IntVar(value=0)
        self.canny_ths1 = tk.IntVar(value=0)
        self.canny_ths2 = tk.IntVar(value=0)
        self.touch_distance = tk.IntVar(value=0)
        self.untouch_distance = tk.IntVar(value=0)
        self.tracked_fingers = []
        
        # Set title
        self.title("Control Panel")
        
        # Set window min size
        self.minsize(width=250, height=250)
        
        # Make the window height fit controls
        self.grid_rowconfigure(0, weight=1)
        
        # Search points label
        label = tk.Label(self, text="Points Search", anchor="w")
        label.grid(row=0, column=0, columnspan=5, padx=10, sticky='ew')

        # Freeze points button
        self._toggle_button = tk.Checkbutton(
            self, variable=self.freeze_points, indicatoron=False,
            width=10, height=2, command=self._freeze_toggle, onvalue=False, offvalue=True)
        self._toggle_button.grid(row=1, column=0, columnspan=5, padx=10, sticky='ew')
        self._freeze_toggle() # Update text

        # Paper detection sliders
        slider = tk.Scale(self, variable=self.blur, from_=0, to=30, 
                          orient=tk.HORIZONTAL, label="Blur Strength")
        slider.grid(row=2, column=0, columnspan=5, padx=10, sticky='ew')
        slider = tk.Scale(self, variable=self.canny_ths1, from_=0, to=200, 
                          orient=tk.HORIZONTAL, label="Canny Threshold 1")
        slider.grid(row=3, column=0, columnspan=5, padx=10, sticky='ew')
        slider = tk.Scale(self, variable=self.canny_ths2, from_=0, to=200, 
                          orient=tk.HORIZONTAL, label="Canny Threshold 2")
        slider.grid(row=4, column=0, columnspan=5, padx=10, sticky='ew')
        
        # Tracked Fingers label
        label = tk.Label(self, text="Tracked fingers", anchor="w")
        label.grid(row=5, column=0, columnspan=5, padx=10, sticky='ew')

        # Tracked fingers checkbuttons
        self._fingers_buttons = []
        fingers = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
        for i in range(5):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                self, text=f"{fingers[i]}", variable=var, indicatoron=False,
                width=10, height=2, command=self._finger_toggle)
            cb.grid(row=6, column=i, padx=10, pady=10, sticky='ew')
            self._fingers_buttons.append(var)

        # Touch validation sliders
        slider = tk.Scale(self, variable=self.touch_distance, from_=0, to=30, 
                          orient=tk.HORIZONTAL, label="Touch detection distance")
        slider.grid(row=7, column=0, columnspan=5, padx=10, pady=5, sticky='ew')
        slider = tk.Scale(self, variable=self.untouch_distance, from_=0, to=30, 
                          orient=tk.HORIZONTAL, label="Untouch detection distance")
        slider.grid(row=8, column=0, columnspan=5, padx=10, pady=5, sticky='ew')
    
    def _freeze_toggle(self):
        # Changes text of freeze button
        self._toggle_button.config(text="Unfreeze Points" if self.freeze_points.get() else "Freeze Points")
        
    def _finger_toggle(self):
        # Computes tracked fingers from checkboxes
        self.tracked_fingers = []
        keypoint = 4 # Thumb
        for fb in self._fingers_buttons:
            if fb.get():
                self.tracked_fingers.append(keypoint)
            
            keypoint += 4 # Next fingertip +4 from the previous
            
