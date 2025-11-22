"""
FPS Counter for MetaMindIQTrain application.
Provides a way to track frames per second for performance monitoring.
"""

class FPSCounter:
    """Tracks frame rate for performance monitoring."""
    
    def __init__(self, update_interval: float = 1.0):
        """Initialize the FPS counter.
        
        Args:
            update_interval: Interval in seconds to update the FPS value
        """
        self.frame_count = 0
        self.fps = 0.0
        self.accumulated_time = 0.0
        self.update_interval = update_interval
        
    def update(self, delta_time: float) -> None:
        """Update the FPS counter.
        
        Args:
            delta_time: Time elapsed since the last frame in seconds
        """
        self.frame_count += 1
        self.accumulated_time += delta_time
        
        # Update FPS value at the specified interval
        if self.accumulated_time >= self.update_interval:
            self.fps = self.frame_count / self.accumulated_time
            self.frame_count = 0
            self.accumulated_time = 0.0
            
    def get_fps(self) -> float:
        """Get the current FPS value.
        
        Returns:
            Current frames per second
        """
        return self.fps
        
    def reset(self) -> None:
        """Reset the FPS counter."""
        self.frame_count = 0
        self.fps = 0.0
        self.accumulated_time = 0.0 