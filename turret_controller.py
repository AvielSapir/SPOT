import serial
import time


class TurretController:
    def __init__(self):
        # --- הגדרות חיבור (שנה כאן אם צריך) ---
        self.serial_port = 'COM3'  # לבדוק ב-Device Manager!
        self.baud_rate = 9600  # חייב להתאים לקוד בארדואינו
        # -------------------------------------

        self.ser = None
        try:
            print(f"Connecting to Arduino on {self.serial_port}...")
            # timeout=0.1 חשוב כדי לא לתקוע את המצלמה אם יש בעיה
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=0.1)
            time.sleep(2)  # חובה לחכות לאתחול הארדואינו
            print("Arduino Connected Successfully!")
        except Exception as e:
            print(f"ERROR: Could not connect to Arduino: {e}")
            print("Running in simulation mode (No motors moving).")

    def move_to(self, pan, tilt):
        """
        מקבלת זוויות ושולחת לארדואינו.
        הפונקציה הזו נקראת ע"י main.py
        """
        if self.ser is None:
            return  # אין חיבור, לא עושים כלום

        # 1. הגנה על הגבולות (0-180)
        pan = max(40, min(80, pan))
        tilt = max(40, min(80, tilt))

        # 2. שליחה בפורמט שהחבר שלך הגדיר
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