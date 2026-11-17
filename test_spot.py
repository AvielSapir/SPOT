import time
import unittest
import numpy as np
from angle_calculator import PIDController, TargetTrackerPredictor, AngleCalculator
from turret_controller import TurretController
from overlay import CrosshairOverlay
from main import SpotSystem

class TestPIDController(unittest.TestCase):
    def test_convergence(self):
        pid = PIDController(kp=0.1, ki=0.01, kd=0.02)
        error = 100.0
        current_val = 0.0
        target_val = 100.0
        t = 0.0
        
        for _ in range(50):
            t += 0.033
            err = target_val - current_val
            adj = pid.compute(err, current_time=t)
            current_val += adj
            
        self.assertLess(abs(target_val - current_val), 10.0)

class TestPredictor(unittest.TestCase):
    def test_velocity_prediction(self):
        predictor = TargetTrackerPredictor()
        predictor.update(100.0, 100.0, current_time=0.0)
        predictor.update(110.0, 100.0, current_time=0.1)
        pred_x, pred_y = predictor.predict_lead(lead_time_seconds=0.1)
        self.assertGreater(pred_x, 110)

class TestAngleCalculator(unittest.TestCase):
    def test_limits_and_centering(self):
        calc = AngleCalculator()
        pan, tilt = calc.calculate_angles(320, 240, 320, 240 + calc.Y_OFFSET, current_time=1.0)
        self.assertEqual(pan, 140)
        self.assertEqual(tilt, 60)

class TestTurretController(unittest.TestCase):
    def test_simulated_motion(self):
        turret = TurretController(simulated=True)
        res = turret.move_to(150, 70)
        self.assertTrue(res)
        self.assertEqual(turret.current_pan, 150)
        self.assertEqual(turret.current_tilt, 70)

class TestIntegrationStep(unittest.TestCase):
    def test_spot_step_synthetic_frame(self):
        system = SpotSystem(simulated=True)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        annotated, locked, angles = system.step(frame)
        self.assertIsNotNone(annotated)
        self.assertFalse(locked)
        self.assertEqual(angles, (140, 60))
        system.shutdown()

if __name__ == "__main__":
    unittest.main()
