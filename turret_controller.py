import time
import serial
from typing import Optional

class TurretController:
    def __init__(self, port: str = "COM3", baud_rate: int = 115200, simulated: bool = False):
        self.port = port
        self.baud_rate = baud_rate
        self.simulated = simulated
        self.ser: Optional[serial.Serial] = None
        self.current_pan = 140
        self.current_tilt = 60
        self.last_fire_time = 0.0
        self.fire_rate_limit = 0.5
        
        if not self.simulated:
            try:
                self.ser = serial.Serial(self.port, self.baud_rate, timeout=0.05)
                time.sleep(1.0)
            except Exception:
                self.simulated = True

    def _send_command(self, cmd: str) -> bool:
        if self.simulated or not self.ser:
            return True
        try:
            checksum = sum(cmd.encode("ascii")) & 0xFF
            packet = f"{cmd}*{checksum:02X}\n"
            self.ser.write(packet.encode("ascii"))
            resp = self.ser.readline().decode("ascii", errors="ignore").strip()
            return "ACK" in resp
        except Exception:
            return False

    def move_to(self, pan: int, tilt: int) -> bool:
        pan = max(80, min(220, int(pan)))
        tilt = max(50, min(90, int(tilt)))
        self.current_pan = pan
        self.current_tilt = tilt
        return self._send_command(f"MOVE,{pan},{tilt}")

    def fire(self) -> bool:
        now = time.time()
        if now - self.last_fire_time < self.fire_rate_limit:
            return False
        self.last_fire_time = now
        return self._send_command("FIRE,1")

    def stop_fire(self) -> bool:
        return self._send_command("FIRE,0")

    def home(self) -> bool:
        return self.move_to(140, 60)

    def close(self):
        if self.ser:
            try:
                self.stop_fire()
                self.home()
                self.ser.close()
            except Exception:
                pass
            self.ser = None
