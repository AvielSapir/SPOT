import tkinter as tk
from PIL import Image, ImageTk
import customtkinter as ctk
import datetime
import cv2  # חובה לייבא את זה בשביל המרות צבע
import numpy as np

# --- הגדרות עיצוב ל-CTK ---
ctk.set_appearance_mode("dark")

# --- צבעי המערכת ---
COLOR_BG = "#21252b"
COLOR_PANEL = "#282c34"
COLOR_ACCENT = "#00e5ff"
COLOR_TEXT_MAIN = "white"
COLOR_TEXT_SEC = "#abb2bf"
COLOR_ALERT = "#ff5555"
COLOR_SUCCESS = "#00ff00"


class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("S.P.O.T. - System Interface")

        # --- הגדרות חלון ---
        self.root.attributes('-fullscreen', True)
        self.root.resizable(False, False)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.configure(bg=COLOR_BG)

        # משתנים פנימיים לתמונה
        self.last_pil_image = None
        self.current_tk_image = None
        self.original_w = 1  # למניעת חלוקה ב-0
        self.original_h = 1

        # משתנה לשמירת הפקודה האחרונה שנלחצה
        self.current_command = None

        # ========================================================
        #              בניית הממשק (Layout)
        # ========================================================

        # 1. רקע בסיס
        self.base_canvas = tk.Canvas(self.root, bg=COLOR_BG, highlightthickness=0)
        self.base_canvas.pack(fill="both", expand=True)
        self.root.bind("<Configure>", self.draw_interface_graphics)

        # 2. חלוקה לאזורים
        self.camera_area = tk.Frame(self.root, bg="black")
        self.camera_area.place(relx=0.02, rely=0.08, relwidth=0.66, relheight=0.65)

        self.controls_area = tk.Frame(self.root, bg=COLOR_BG)
        self.controls_area.place(relx=0.70, rely=0.08, relwidth=0.28, relheight=0.65)

        self.data_area = tk.Frame(self.root, bg=COLOR_BG)
        self.data_area.place(relx=0.05, rely=0.78, relwidth=0.90, relheight=0.18)

        # 3. הגדרת מסך התצוגה (Canvas)
        self.cam_canvas = tk.Canvas(self.camera_area, bg="black", highlightthickness=0)
        self.cam_canvas.pack(fill="both", expand=True)
        self.cam_canvas.bind("<Configure>", self._on_resize_camera)

        # שכבת התמונה ושכבת האנימציה (הריבוע הכחול)
        self.image_item = self.cam_canvas.create_image(0, 0, anchor=tk.NW)
        self.rect_frame = self.cam_canvas.create_rectangle(0, 0, 0, 0,
                                                           outline="#0000FF", width=3,
                                                           fill="#00FFFF", stipple="gray25")

        # 4. כותרות ולוגו
        tk.Label(self.root, text=" ⌖ S.P.O.T.", font=("Impact", 24), fg="white", bg=COLOR_BG).place(x=20, y=10)
        tk.Label(self.root, text='בס"ד', font=("Arial", 14), fg="white", bg=COLOR_BG).place(relx=0.95, y=15,
                                                                                            anchor="ne")

        # 5. כפתורי שליטה (צד ימין)
        self._setup_controls()

        # 6. לוג ונתונים (למטה)
        self._setup_data_panel()

    def _setup_controls(self):
        """ בניית אזור הכפתורים """
        ctk.CTkLabel(self.controls_area, text="MANUAL LASER CONTROL", font=("Orbitron", 20, "bold"),
                     text_color=COLOR_ACCENT).place(relx=0.5, rely=0.15, anchor="center")

        buttons_frame = ctk.CTkFrame(self.controls_area, fg_color="transparent")
        buttons_frame.place(relx=0.5, rely=0.55, anchor="center")

        btn_cfg = {"width": 60, "height": 40, "corner_radius": 10, "font": ("Arial", 32),
                   "fg_color": "#0047AB", "border_color": "#00BFFF", "border_width": 2, "hover_color": "#1E90FF"}

        ctk.CTkButton(buttons_frame, text="▲", command=lambda: self._register_click("MOVE_UP"), **btn_cfg).grid(row=0,
                                                                                                                column=1,
                                                                                                                pady=15)
        ctk.CTkButton(buttons_frame, text="▼", command=lambda: self._register_click("MOVE_DOWN"), **btn_cfg).grid(row=3,
                                                                                                                  column=1,
                                                                                                                  pady=15)
        ctk.CTkButton(buttons_frame, text="◀", command=lambda: self._register_click("MOVE_LEFT"), **btn_cfg).grid(row=2,
                                                                                                                  column=0,
                                                                                                                  padx=15)
        ctk.CTkButton(buttons_frame, text="▶", command=lambda: self._register_click("MOVE_RIGHT"), **btn_cfg).grid(
            row=2, column=2, padx=15)

        ctk.CTkButton(buttons_frame, text="🔥 FIRE 🔥", width=140, height=60, corner_radius=20,
                      fg_color="#CC0000", hover_color="#FF4500", text_color="#FFD700", font=("Rubik Storm", 18, "bold"),
                      command=lambda: self._register_click("FIRE_LASER")).grid(row=2, column=1, padx=15, pady=15)

    def _setup_data_panel(self):
        """ בניית אזור הנתונים התחתון """
        self.log_panel = ctk.CTkFrame(self.data_area, fg_color="transparent")
        self.log_panel.place(relx=0, rely=0, relwidth=0.4, relheight=1)

        ctk.CTkLabel(self.log_panel, text="SYSTEM COMMAND LOG >", font=("Consolas", 14, "bold"),
                     text_color=COLOR_TEXT_SEC).pack(anchor="w", padx=10, pady=(10, 0))
        self.log_box = ctk.CTkTextbox(self.log_panel, fg_color="transparent", text_color=COLOR_ALERT,
                                      font=("Consolas", 16))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)

        self.telemetry_panel = ctk.CTkFrame(self.data_area, fg_color="transparent")
        self.telemetry_panel.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

        self.lbl_status = ctk.CTkLabel(self.telemetry_panel, text="[ SEARCHING FOR TARGET... ]",
                                       font=("Consolas", 18, "bold"), text_color=COLOR_ALERT)
        self.lbl_status.pack(pady=(15, 5))

        grid_frame = ctk.CTkFrame(self.telemetry_panel, fg_color="transparent")
        grid_frame.pack(expand=True, fill="both", padx=20, pady=5)

        self.lbl_x = ctk.CTkLabel(grid_frame, text="X-AXIS: 000", font=("Consolas", 20), text_color=COLOR_ACCENT)
        self.lbl_x.grid(row=0, column=0, padx=20, pady=5, sticky="w")

        self.lbl_y = ctk.CTkLabel(grid_frame, text="Y-AXIS: 000", font=("Consolas", 20), text_color=COLOR_ACCENT)
        self.lbl_y.grid(row=0, column=1, padx=20, pady=5, sticky="e")

        self.lbl_motor_a = ctk.CTkLabel(grid_frame, text="MOTOR A: 0.0°", font=("Consolas", 16),
                                        text_color=COLOR_TEXT_SEC)
        self.lbl_motor_a.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        self.lbl_motor_b = ctk.CTkLabel(grid_frame, text="MOTOR B: 0.0°", font=("Consolas", 16),
                                        text_color=COLOR_TEXT_SEC)
        self.lbl_motor_b.grid(row=1, column=1, padx=20, pady=5, sticky="e")

        self.update_log("System Initialized.")

    # ========================================================
    #          פונקציות הליבה (מתוקנות לחיבור OpenCV)
    # ========================================================

    def get_command(self):
        """ מחזיר את הפקודה שנלחצה ומאפס """
        cmd = self.current_command
        self.current_command = None  # איפוס
        return cmd

    def update_frame(self, frame):
        """
        מקבל פריים (מערך Numpy מ-OpenCV),
        ממיר לצבעים נכונים ולפורמט תמונה ומציג
        """
        try:
            if frame is None:
                return

            # שמירת הרזולוציה המקורית לטובת חישובי מיקום
            self.original_h, self.original_w = frame.shape[:2]

            # המרה מ-BGR (של OpenCV) ל-RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # יצירת תמונת PIL
            pil_image = Image.fromarray(rgb_frame)

            self.last_pil_image = pil_image
            self._display_image_fit_to_screen()

        except Exception as e:
            print(f"Frame Error: {e}")  # הדפסה לקונסול במקום ללוג כדי לא להציף

    def update_target(self, is_target, x, y):
        """ מקבל האם קיים אובייקט, ומעדכן מסך עם יחס המרה """

        # עדכון טקסט
        self.lbl_x.configure(text=f"X-AXIS: {int(x)}")
        self.lbl_y.configure(text=f"Y-AXIS: {int(y)}")

        if is_target:
            self.lbl_status.configure(text="⚠ TARGET DETECTED ⚠", text_color=COLOR_SUCCESS)

            # --- חישוב המיקום החדש לפי גודל המסך ---
            # אנחנו צריכים לדעת מה הגודל של הקנבס כרגע
            canvas_w = self.cam_canvas.winfo_width()
            canvas_h = self.cam_canvas.winfo_height()

            # חישוב יחס מתיחה
            scale_x = canvas_w / self.original_w
            scale_y = canvas_h / self.original_h

            # המיקום האמיתי על המסך
            screen_x = x * scale_x
            screen_y = y * scale_y

            # ציור הריבוע במיקום המתוקן
            box_size = 100  # גודל הריבוע על המסך
            half = box_size / 2
            self.cam_canvas.coords(self.rect_frame, screen_x - half, screen_y - half, screen_x + half, screen_y + half)
        else:
            self.lbl_status.configure(text="[ SEARCHING FOR TARGET... ]", text_color=COLOR_ALERT)
            # העלמת הריבוע
            self.cam_canvas.coords(self.rect_frame, 0, 0, 0, 0)

    def refresh(self):
        """ פונקציה שה-Main Loop יקרא לה כדי לרענן את המסך """
        self.root.update_idletasks()
        self.root.update()

    def update_log(self, *args):
        msg = " ".join(str(arg) for arg in args)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] >> {msg}\n")
        self.log_box.see("end")

    # ========================================================
    #          פונקציות עזר פנימיות
    # ========================================================

    def _register_click(self, cmd_name):
        self.current_command = cmd_name
        # אפקט ויזואלי ללחיצה
        self.update_log(f"CMD: {cmd_name}")

    def _on_resize_camera(self, event):
        if self.last_pil_image: self._display_image_fit_to_screen()

    def _display_image_fit_to_screen(self):
        if not self.last_pil_image: return
        w = self.cam_canvas.winfo_width()
        h = self.cam_canvas.winfo_height()
        if w < 10 or h < 10: return

        # מתיחת התמונה לגודל הקנבס
        resized = self.last_pil_image.resize((w, h))
        self.current_tk_image = ImageTk.PhotoImage(resized)
        self.cam_canvas.itemconfig(self.image_item, image=self.current_tk_image)

    def draw_interface_graphics(self, event=None):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.base_canvas.delete("all")

        # קו מפריד
        split_x = w * 0.69
        self.base_canvas.create_line(split_x, 50, split_x, h * 0.75, fill=COLOR_ACCENT, width=2)

        # מסגרת תחתונה בסגנון Cyberpunk
        pad_x = w * 0.03
        panel_y = h * 0.76
        cut = 20
        pts = [pad_x + cut, panel_y, w - pad_x - cut, panel_y, w - pad_x, panel_y + cut,
               w - pad_x, h - 20 - cut, w - pad_x - cut, h - 20, pad_x + cut, h - 20,
               pad_x, h - 20 - cut, pad_x, panel_y + cut]

        self.base_canvas.create_polygon(pts, outline=COLOR_ACCENT, fill="", width=2)

