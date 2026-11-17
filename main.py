import time
import argparse
import numpy as np
from vision import VisionEngine
from angle_calculator import AngleCalculator
from turret_controller import TurretController
from overlay import CrosshairOverlay

class SpotSystem:
    def __init__(self, camera_source=0, weights_path: str = "yolov8n.pt", port: str = "COM3", simulated: bool = True):
        self.vision = VisionEngine(source=camera_source, weights_path=weights_path)
        self.calculator = AngleCalculator()
        self.turret = TurretController(port=port, simulated=simulated)
        self.lock_threshold = 12.0
        self.lock_hold_frames = 0
        self.required_lock_frames = 5
        self.running = False

    def step(self, frame: np.ndarray = None):
        if frame is None:
            frame = self.vision.get_frame()
        if frame is None:
            return None, False, (self.turret.current_pan, self.turret.current_tilt)
        
        lx, ly, tx, ty, l_found, t_found, t_name = self.vision.find_target(frame)
        
        lock_acquired = False
        if t_found and l_found:
            pan, tilt = self.calculator.calculate_angles(tx, ty, lx, ly)
            self.turret.move_to(pan, tilt)
            
            error_dist = ((tx - lx) ** 2 + ((ty + self.calculator.Y_OFFSET) - ly) ** 2) ** 0.5
            if error_dist <= self.lock_threshold:
                self.lock_hold_frames += 1
                if self.lock_hold_frames >= self.required_lock_frames:
                    lock_acquired = True
                    self.turret.fire()
            else:
                self.lock_hold_frames = 0
                self.turret.stop_fire()
        else:
            self.lock_hold_frames = 0
            self.turret.stop_fire()
            self.calculator.reset_control()

        annotated = CrosshairOverlay.draw(frame, (lx, ly), (tx, ty), lock_acquired, t_name)
        return annotated, lock_acquired, (self.turret.current_pan, self.turret.current_tilt)

    def shutdown(self):
        self.running = False
        self.turret.close()
        self.vision.release()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=0)
    parser.add_argument("--weights", default="yolov8n.pt")
    parser.add_argument("--port", default="COM3")
    parser.add_argument("--simulated", action="store_true", default=True)
    args = parser.parse_args()

    system = SpotSystem(
        camera_source=args.source,
        weights_path=args.weights,
        port=args.port,
        simulated=args.simulated
    )
    
    try:
        while True:
            annotated, locked, angles = system.step()
            if annotated is None:
                break
            time.sleep(0.033)
    except KeyboardInterrupt:
        pass
    finally:
        system.shutdown()

if __name__ == "__main__":
    main()
