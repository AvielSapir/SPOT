from vision import VisionSystem
from turret_controller import TurretController
from ui import UserInterface
from angle_calculator import AngleCalculator
import time


vision = VisionSystem()
turret = TurretController()
angle_calculator = AngleCalculator()
ui = UserInterface()

is_running = True
mode = "SAFE MODE"

while is_running:
    mode = ui.get_command()
    print(mode)

    # vision
    frame = vision.get_frame()
    if frame is None:
        break
    t_x, t_y, t_found = 0, 0, False
    l_x, l_y, l_found = 0, 0, False

    # move
    if mode == "RED":
        t_x, t_y, l_x, l_y, t_found, l_found = vision.find_target(frame, mode)
        if t_found and l_found:
            pan, tilt = angle_calculator.calculate_angles(t_x, t_y, l_x, l_y)
            turret.move_to(pan, tilt)

    # ui
    ui.update_frame(frame)
    ui.update_target(t_found, t_x, t_y)





