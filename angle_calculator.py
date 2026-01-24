class AngleCalculator:

    def __init__(self):
        self.current_pan = 140
        self.current_tilt = 60
        self.PAN_MIN = 80
        self.PAN_MAX = 220
        self.TILT_MIN = 50
        self.TILT_MAX = 90
        self.Y_OFFSET = 40

    def calculate_angles(self, target_x, target_y, laser_x, laser_y):
        k = 0.01
        dead_zone = 55

        target_y_corrected = target_y + self.Y_OFFSET

        error_x = target_x - laser_x
        error_y = target_y_corrected - laser_y

        if abs(error_x) < dead_zone and abs(error_y) < dead_zone:
            return int(self.current_pan), int(self.current_tilt)
        delta_pan = error_x * k
        delta_tilt = error_y * k

        self.current_pan -= delta_pan
        self.current_tilt -= delta_tilt

        self.current_pan = max(self.PAN_MIN, min(self.PAN_MAX, self.current_pan))
        self.current_tilt = max(self.TILT_MIN, min(self.TILT_MAX, self.current_tilt))

        return int(self.current_pan), int(self.current_tilt)