import cv2
import numpy as np
from typing import Tuple

class CrosshairOverlay:
    @staticmethod
    def draw(frame: np.ndarray, laser_pos: Tuple[int, int], target_pos: Tuple[int, int], lock_acquired: bool, target_label: str = None) -> np.ndarray:
        display = frame.copy()
        h, w = display.shape[:2]
        
        cv2.line(display, (w // 2 - 20, h // 2), (w // 2 + 20, h // 2), (200, 200, 200), 1)
        cv2.line(display, (w // 2, h // 2 - 20), (w // 2, h // 2 + 20), (200, 200, 200), 1)
        
        lx, ly = laser_pos
        if lx != -1 and ly != -1:
            cv2.circle(display, (lx, ly), 6, (0, 255, 0), -1)
            cv2.circle(display, (lx, ly), 12, (0, 255, 0), 1)
            cv2.putText(display, "LASER", (lx + 15, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
        tx, ty = target_pos
        if tx != -1 and ty != -1:
            box_color = (0, 0, 255) if not lock_acquired else (0, 255, 255)
            cv2.rectangle(display, (tx - 25, ty - 25), (tx + 25, ty + 25), box_color, 2)
            lbl = f"TARGET: {target_label or 'UNKNOWN'}"
            cv2.putText(display, lbl, (tx - 35, ty - 32), cv2.FONT_HERSHEY_SIMPLEX, 0.4, box_color, 1)
            if lx != -1 and ly != -1:
                cv2.line(display, (lx, ly), (tx, ty), (255, 0, 255), 1)
                
        status_text = "STATUS: LOCKED" if lock_acquired else "STATUS: TRACKING"
        status_color = (0, 255, 0) if lock_acquired else (0, 165, 255)
        cv2.putText(display, status_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        return display
