import tkinter as tk

class ControlPanel(tk.Tk):
    def __init__(self, 
                 freeze_points: bool = False, 
                 blur: int = 10, 
                 canny_ths1: int = 40,
                 canny_ths2: int = 40,
                 match_threshold: int = 60):
        """Creates a new tk window with controls for piano detection validation"""
        super().__init__()
        
        # Controlable variables
        self.freeze_points = tk.BooleanVar(value=freeze_points)
        self.blur = tk.IntVar(value=blur)
        self.canny_ths1 = tk.IntVar(value=canny_ths1)
        self.canny_ths2 = tk.IntVar(value=canny_ths2)
        self.match_threshold = tk.IntVar(value=match_threshold)
        self.is_closed = False
        
        self.bind("<Destroy>", self._window_closed)
        self.bind('q', self._window_closed)
        
        # Set title
        self.title("Control Panel")
        
        # Set window min size
        self.minsize(width=250, height=250)
        
        # Make the window height fit controls
        self.grid_rowconfigure(0, weight=1)
        
        # Search points label
        label = tk.Label(self, text="Points Search", anchor="w")
        label.grid(row=0, column=0, columnspan=1, padx=10, sticky='ew')

        # Freeze points button
        self._toggle_button = tk.Checkbutton(
            self, variable=self.freeze_points, indicatoron=False,
            width=40, height=2, command=self._freeze_toggle, onvalue=False, offvalue=True)
        self._toggle_button.grid(row=1, column=0, columnspan=1, padx=10, sticky='ew')
        self._freeze_toggle() # Update text

        # Paper detection sliders
        slider = tk.Scale(self, variable=self.blur, from_=0, to=30, 
                          orient=tk.HORIZONTAL, label="Blur Strength")
        slider.grid(row=2, column=0, columnspan=1, padx=10, sticky='ew')
        slider = tk.Scale(self, variable=self.canny_ths1, from_=0, to=200, 
                          orient=tk.HORIZONTAL, label="Canny Threshold 1")
        slider.grid(row=3, column=0, columnspan=1, padx=10, sticky='ew')
        slider = tk.Scale(self, variable=self.canny_ths2, from_=0, to=200, 
                          orient=tk.HORIZONTAL, label="Canny Threshold 2")
        slider.grid(row=4, column=0, columnspan=1, padx=10, sticky='ew')
        
        # Validation - match threshold
        slider = tk.Scale(self, variable=self.match_threshold, from_=40, to=90, 
                          orient=tk.HORIZONTAL, label="Match threshold")
        slider.grid(row=5, column=0, columnspan=1, padx=10, pady=10, sticky='ew')
    
    def _freeze_toggle(self):
        # Changes text of freeze button
        self._toggle_button.config(text="Unfreeze Points" if self.freeze_points.get() else "Freeze Points")
        
    def _finger_toggle(self):
        # Computes tracked fingers from checkbottons
        self.tracked_fingers = []
        keypoint = 4 # Thumb
        for fb in self._fingers_buttons:
            if fb.get():
                self.tracked_fingers.append(keypoint)
            
            keypoint += 4 # Next fingertip +4 from the previous
            
    def _window_closed(self, ev):
        self.is_closed = True
        
    