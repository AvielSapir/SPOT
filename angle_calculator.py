import time

class PIDController:
    def __init__(self, kp: float = 0.04, ki: float = 0.005, kd: float = 0.015, output_limits=(-15.0, 15.0), integral_limits=(-50.0, 50.0)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits
        self.integral_limits = integral_limits
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = None

    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = None

    def compute(self, error: float, current_time: float = None) -> float:
        if current_time is None:
            current_time = time.time()
        
        if self.last_time is None:
            dt = 0.033
        else:
            dt = max(0.001, current_time - self.last_time)
        
        self.integral += error * dt
        min_i, max_i = self.integral_limits
        self.integral = max(min_i, min(max_i, self.integral))
        
        derivative = (error - self.last_error) / dt
        
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        min_out, max_out = self.output_limits
        output = max(min_out, min(max_out, output))
        
        self.last_error = error
        self.last_time = current_time
        return output

class TargetTrackerPredictor:
    def __init__(self):
        self.last_pos = None
        self.last_time = None
        self.velocity = (0.0, 0.0)

    def update(self, target_x: float, target_y: float, current_time: float = None):
        if current_time is None:
            current_time = time.time()
        
        if self.last_time is not None and self.last_pos is not None:
            dt = max(0.001, current_time - self.last_time)
            vx = (target_x - self.last_pos[0]) / dt
            vy = (target_y - self.last_pos[1]) / dt
            self.velocity = (0.7 * self.velocity[0] + 0.3 * vx, 0.7 * self.velocity[1] + 0.3 * vy)
        
        self.last_pos = (target_x, target_y)
        self.last_time = current_time

    def predict_lead(self, lead_time_seconds: float = 0.1) -> tuple:
        if self.last_pos is None:
            return 0, 0
        pred_x = self.last_pos[0] + self.velocity[0] * lead_time_seconds
        pred_y = self.last_pos[1] + self.velocity[1] * lead_time_seconds
        return int(pred_x), int(pred_y)

class AngleCalculator:
    def __init__(self):
        self.current_pan = 140.0
        self.current_tilt = 60.0
        self.PAN_MIN = 80.0
        self.PAN_MAX = 220.0
        self.TILT_MIN = 50.0
        self.TILT_MAX = 90.0
        self.Y_OFFSET = 40.0
        self.dead_zone = 8.0
        
        self.pid_pan = PIDController(kp=0.035, ki=0.004, kd=0.012)
        self.pid_tilt = PIDController(kp=0.035, ki=0.004, kd=0.012)
        self.predictor = TargetTrackerPredictor()

    def reset_control(self):
        self.pid_pan.reset()
        self.pid_tilt.reset()

    def calculate_angles(self, target_x: float, target_y: float, laser_x: float, laser_y: float, current_time: float = None) -> tuple:
        self.predictor.update(target_x, target_y, current_time)
        pred_tx, pred_ty = self.predictor.predict_lead(lead_time_seconds=0.08)
        
        corrected_y = pred_ty + self.Y_OFFSET
        error_x = pred_tx - laser_x
        error_y = corrected_y - laser_y
        
        if abs(error_x) < self.dead_zone and abs(error_y) < self.dead_zone:
            self.pid_pan.reset()
            self.pid_tilt.reset()
            return int(self.current_pan), int(self.current_tilt)
        
        adj_pan = self.pid_pan.compute(error_x, current_time)
        adj_tilt = self.pid_tilt.compute(error_y, current_time)
        
        self.current_pan -= adj_pan
        self.current_tilt -= adj_tilt
        
        self.current_pan = max(self.PAN_MIN, min(self.PAN_MAX, self.current_pan))
        self.current_tilt = max(self.TILT_MIN, min(self.TILT_MAX, self.current_tilt))
        
        return int(self.current_pan), int(self.current_tilt)
