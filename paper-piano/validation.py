import math
from detection import Keypoint


class TrackedPoint:
    def __init__(self, position, touching_fingertips=[]):
        self.position = position
        self.fingertips = []


class TouchValidator:
    def __init__(self):
        self.tracked_points = []

    def process(
        self, piano_points: list[tuple[float, float]], fingertips: list[Keypoint], 
        touch_distance: float, untouch_distance: float
        ) -> set[int]:
        """
        Checks if piano points are close enough to fingertip.
        Returns indexes of piano points that were not previously touched
        but are touched now.
        """
        # Number of given points is diffrent than tracked points
        if len(piano_points) != len(self.tracked_points):
            # Creates clean tracked points
            self._create_tracked_points(piano_points)

        indexes = set()
        i = 0 # Index of piano point
        # For each piano point checks if any given fingertip should start/stop being tracked.
        # Fingertip is removed from trackign only if its distance from piano point is higher
        # than max_distance, if the fingertip wasnt detected in given frame it stays tracked.
        for pp in piano_points:
            for ft in fingertips:
                is_touching = math.dist(pp, ft.position) < touch_distance
                
                ft_index =  self._get_fingertip_index(self.tracked_points[i].fingertips, ft)
                is_tracked = ft_index != -1
                
                if is_tracked:
                    # Fingertip is outside if its distance is geater than max_distance from previous position
                    is_outside = math.dist(self.tracked_points[i].fingertips[ft_index].position, ft.position) > untouch_distance
                    if is_outside:
                        # Fingertip is no longer touching the piano point
                        del self.tracked_points[i].fingertips[ft_index]
                else:
                    if is_touching:
                        # Fingertip is not tracked, but touching point
                        if len(self.tracked_points[i].fingertips) == 0:
                            # Piano point is not touched by any finger
                            indexes.add(i)
                        
                        self.tracked_points[i].fingertips.append(ft)
                        
                
            i += 1
                    
        return indexes
    
    def _get_fingertip_index(self, tracked_fingertips: list[Keypoint], fingertip: Keypoint) -> int:
        # Checks if fingertip is already tracked, returns index if true, otherwise -1 
        j = 0
        for tracked_ft in tracked_fingertips:
            if self._are_fingertips_equal(fingertip, tracked_ft):                        
                return j
            j += 1
        
        return -1
    
    def _are_fingertips_equal(self, ft1: Keypoint, ft2: Keypoint):
        # Fingertips are equal if hand and keypoint number are the same
        if ft1.hand == ft2.hand and ft1.number == ft2.number:
            return True

        return False

    def _create_tracked_points(self, piano_points: list[tuple[float, float]]):
        for pp in piano_points:
            new_tracked = TrackedPoint(pp)
            self.tracked_points.append(new_tracked)
