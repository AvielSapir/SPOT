# SPOT (Smart Precision Optical Turret)

An autonomous computer-vision target tracking and optical turret control system in Python. It combines **YOLOv8** object detection, **HSV laser-spot tracking**, **PID closed-loop control**, and **lead-target prediction** to lock onto moving targets and drive a hardware turret over serial.

## How it works

1. **Vision (`vision.py`)** – Runs YOLOv8 object detection to locate targets and uses HSV color masking + contour moments to pinpoint the laser dot in real time.
2. **Control & prediction (`angle_calculator.py`)** – Estimates target velocity with an exponential moving average (lead prediction), applies a dead zone to avoid motor jitter, and runs separate Pan/Tilt PID controllers with anti-windup.
3. **Hardware interface (`turret_controller.py`)** – Sends checksummed `MOVE,Pan,Tilt*Checksum` commands over UART/Serial (with a built-in simulation mode for testing without hardware) and enforces rate-limited firing only after consecutive lock-on frames.
4. **HUD overlay (`overlay.py`)** – Draws crosshairs, tracking boxes, error vectors, and lock status (`LOCKED` / `TRACKING`) onto each frame.

### PID control loop

Pan and tilt corrections are computed continuously from the spatial error $e(t)$ between the laser dot and the target:

$$
u(t) = K_p \cdot e(t) + K_i \int_0^t e(\tau) \, d\tau + K_d \frac{de(t)}{dt}
$$

- **Proportional ($K_p$)** reacts to the current pixel offset.
- **Integral ($K_i$)** eliminates steady-state error from mechanical friction or gravity.
- **Derivative ($K_d$)** dampens overshoot when the turret approaches the target.

## Quick start

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the unit tests:
```bash
python test_spot.py
```

Run in simulation mode:
```bash
python main.py --source 0 --weights yolov8n.pt --simulated
```

## Project structure

- `main.py` – Main control loop (`SpotSystem`) and CLI entry point
- `vision.py` – YOLOv8 target detection and HSV laser-spot tracking
- `angle_calculator.py` – `PIDController`, `TargetTrackerPredictor`, and `AngleCalculator`
- `turret_controller.py` – Checksummed serial protocol and simulated turret driver
- `overlay.py` – Real-time HUD rendering
- `test_spot.py` – Unit tests for control, vision, and protocol logic
