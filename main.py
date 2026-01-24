import tkinter as tk

import vision
from turret_controller import TurretController
from ui import UserInterface
from angle_calculator import AngleCalculator
import time


turret = TurretController()
angle_calculator = AngleCalculator()

root = tk.Tk()
ui = UserInterface(root)


count = 0
is_running = True
mode = "SAFE MODE"

turret.move_to(140, 60)
while is_running:
    try:
        ui.refresh()
    except tk.TclError:
        is_running = False
        break
    #mode = ui.get_command()
    #print(mode)

    # vision
    frame = vision.get_frame()
    if frame is None:
        break
    print("+screen")
    t_x, t_y, t_found = 0, 0, False
    l_x, l_y, l_found = 0, 0, False

    # move
    if mode == "SAFE MODE":
        l_x, l_y, t_x, t_y, l_found, t_found = vision.find_target(frame)
        if t_found and l_found:
            pan, tilt = angle_calculator.calculate_angles(t_x, t_y, l_x, l_y)
            turret.move_to(pan, tilt)
            print("$$$")
        else:
            count += 1
            if count >= 20:
                count = 0
                turret.move_to(140, 60)

    # ui
    ui.update_frame(frame)
    ui.update_target(t_found, t_x, t_y)
    #time.sleep(0.1)


print("done")


