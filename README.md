# Drawn Piano with OpenCV and Mediapipe

Demo video, play with sound on\
[![Project video demo](https://img.youtube.com/vi/50WxalOTiOc/0.jpg)](https://youtu.be/50WxalOTiOc)

## Overview

This project allows users to play a piano that is drawn on a piece of paper. Using the power of OpenCV and Mediapipe, the application tracks the user's fingers and plays the corresponding notes as they interact with the drawn piano keys.

The project also includes a **Control Panel** built with Tkinter that enables users to adjust various settings, such as:

- Adjusting OpenCV detection variables to improve piano detection accuracy.
- Selecting which fingers to track for piano key interaction.
- Modifying the distance threshold between the finger and the piano key to trigger a note.

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