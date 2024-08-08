import os
import re
from threading import Thread
from playsound import playsound


UNIFORM_SOUND_SELECTION = 0
MIDDLE_SOUND_SELECTION = 1

class PianoPlayer:
    def __init__(self, sounds_dir_path: str):
        self._sound_filenames = [] # List of ordered file paths
        self._dir = sounds_dir_path
        
        self._group = []
        self.grouping = True
        
        # Reads filenames
        self._sound_filenames = os.listdir(sounds_dir_path)
        # Sorts files by first number appearing in name
        self._sound_filenames.sort(key=lambda name: int(re.match(r'\d+', name).group()))
        
        
    def play_keys(self, number_of_keys: int, play_indexes: list[int], selection_method: int = 0):
        # Select sounds to be picked from
        if number_of_keys == 0 or not play_indexes:
            return
        
        # Pick which files are used to create keyboard
        selected_sounds = []
        if selection_method == 0:
            selected_sounds = self._select_sounds_uniform(number_of_keys)
        else:
            selected_sounds = self._select_sounds_middle(number_of_keys)
        
        # Plays given keys
        for index in play_indexes:
            filename = selected_sounds[index]
            # Creates and starts a new sound thread
            Thread(target=playsound, args=(f"{self._dir}/{filename}",), daemon=True).start()
            
    def _select_sounds_uniform(self, number_of_keys: int) -> list[str]:
        # Selects given number of keys by selecting every n-th key
        lenght = len(self._sound_filenames)
        
        # If number of keys is 1 returns middle element
        if number_of_keys == 1:
            return [self._sound_filenames[lenght//2]]
        
        # Calcualte distance between each file
        step = (lenght - 1) / (number_of_keys - 1)
        
        result = []
        for i in range(number_of_keys):
            result.append(self._sound_filenames[round(step * i)])
            
        return result
    
    def _select_sounds_middle(self, number_of_keys: int) -> list[str]:
        # Selects given number of keys from the middle of filelist
        # If number of keys is 1 returns middle element
        if number_of_keys == 1:
            return [self._sound_filenames[lenght//2]]

        lenght = len(self._sound_filenames)
        start_index = (lenght - number_of_keys) // 2
        return self._sound_filenames[start_index:start_index + number_of_keys]