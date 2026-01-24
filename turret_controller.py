import serial
import time


class TurretController:
    def __init__(self):
        self.serial_port = 'COM3'
        self.baud_rate = 9600

        self.ser = None
        try:
            print(f"Connecting to Arduino on {self.serial_port}...")
            # timeout=0.1
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=0.1)
            time.sleep(2)
            print("Arduino Connected Successfully!")
        except Exception as e:
            print(f"ERROR: Could not connect to Arduino: {e}")
            print("Running in simulation mode (No motors moving).")

    def move_to(self, pan, tilt):
        if self.ser is None:
            return

        pan = max(80, min(220, pan))
        tilt = max(50, min(90, tilt))

        command = f"{pan},{tilt}\n"

        try:
            self.ser.write(command.encode())

            if self.ser.in_waiting > 0:
                self.ser.read(self.ser.in_waiting)

        except Exception as e:
            print(f"Serial Error: {e}")

    def close(self):
        if self.ser:
            self.ser.close()
            print("Serial Connection Closed.")