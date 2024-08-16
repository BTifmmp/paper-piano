# Drawn Piano with OpenCV

Demo video, play with sound on\
[![Project video demo](https://img.youtube.com/vi/t-hFxrR4HwU/0.jpg)](https://youtu.be/t-hFxrR4HwU)

## Overview

This project allows users to play a piano that is drawn on a piece of paper. Using the power of OpenCV, the application tracks if user's fingers are touching piano and plays the corresponding notes. Paper rectangle is detected using canny edge detection and contours. From rectangle the points are detected also using canny and contours. After finding points small snapshot (hardcoded 6x6) of each point is taken to be later used as a background for template matching.

The project also includes a **Control Panel** built with Tkinter that enables users to adjust various settings, such as:

- Adjusting OpenCV detection variables to improve piano detection accuracy.
- Modifying the template match threshold used in checking if point is covered by finger.

## Installation

To get started with this project, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/drawn-piano.git
    cd drawn-piano
    ```

2. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application:**
    ```bash
    python main.py
    ```

## Usage
1. Draw a piano keyboard as points on a rectangular piece of paper.
2. Run the application as described in the installation steps.
3. Position your camera to capture the drawn piano.
4. Use the control panel to adjust detection settings.
5. Once the desired points are detected press "Freeze Points" button at the top of control panel.
5. Start playing by pressing the keys on your drawn piano with your fingers.

## Acknowledgements
The piano sounds used in this project are sourced from the [University of Iowa Electronic Music Studios](http://theremin.music.uiowa.edu/) and later modified to fit the projects needs.