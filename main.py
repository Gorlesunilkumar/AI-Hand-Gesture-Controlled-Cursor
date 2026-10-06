import cv2
import mediapipe as mp
import pyautogui
import math
import time
import tkinter as tk

from PIL import Image, ImageTk


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

APP_TITLE = "AI Hand Gesture Controlled Cursor"

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

CLICK_COOLDOWN = 0.5
STOP_HOLD_TIME = 1.0


# =========================================================
# COLORS
# =========================================================

BG = "#0B141C"
PANEL = "#172630"
CARD = "#203541"
CARD_DARK = "#15232C"

WHITE = "#FFFFFF"
TEXT = "#D9E2E8"
MUTED = "#91A1AC"

GREEN = "#00D084"
GREEN_DARK = "#009F68"

RED = "#F0443A"
RED_DARK = "#B92F28"

BLUE = "#3F6078"
BLUE_ACTIVE = "#547891"


# =========================================================
# MEDIAPIPE SETUP
# =========================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# =========================================================
# MAIN APPLICATION
# =========================================================

class HandGestureApp:

    def __init__(self, root):

        self.root = root

        # =================================================
        # WINDOW
        # =================================================

        self.root.title(APP_TITLE)
        self.root.geometry("1220x900")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # =================================================
        # SETTINGS
        # =================================================

        self.smoothing = 5
        self.pinch_threshold = 35
        self.drag_hold_time = 0.6
        self.scroll_sensitivity = 4

        # =================================================
        # CAMERA
        # =================================================

        self.running = False
        self.cap = None

        # =================================================
        # CURSOR
        # =================================================

        self.prev_x = None
        self.prev_y = None

        # =================================================
        # CLICK
        # =================================================

        self.last_click_time = 0
        self.last_right_click_time = 0

        # =================================================
        # PINCH / DRAG
        # =================================================

        self.pinch_started = False
        self.pinch_start_time = 0
        self.dragging = False

        # =================================================
        # SCROLL
        # =================================================

        self.previous_palm_y = None

        # =================================================
        # CLOSED FIST STOP
        # =================================================

        self.fist_started = False
        self.fist_start_time = 0

        # =================================================
        # FPS
        # =================================================

        self.frame_count = 0
        self.fps = 0
        self.fps_start_time = time.time()

        # =================================================
        # CAMERA IMAGE
        # =================================================

        self.frame_photo = None

        # =================================================
        # CREATE GUI
        # =================================================

        self.create_gui()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )


    # =====================================================
    # CREATE GUI
    # =====================================================

    def create_gui(self):

        # =================================================
        # HEADER
        # =================================================

        header = tk.Frame(
            self.root,
            bg=BG,
            height=150
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="AI HAND GESTURE CONTROLLED CURSOR",
            font=("Segoe UI", 26, "bold"),
            bg=BG,
            fg=WHITE
        ).pack(
            pady=(15, 0)
        )

        tk.Label(
            header,
            text="Computer Vision Based Human-Computer Interaction",
            font=("Segoe UI", 11),
            bg=BG,
            fg=MUTED
        ).pack(
            pady=(4, 0)
        )

        tk.Label(
            header,
            text="Developed by G SUNIL KUMAR",
            font=("Segoe UI", 12, "bold"),
            bg=BG,
            fg=GREEN
        ).pack(
            pady=(7, 0)
        )


        # =================================================
        # MAIN CONTENT
        # =================================================

        main_frame = tk.Frame(
            self.root,
            bg=BG
        )

        main_frame.pack(
            padx=14,
            pady=(0, 10)
        )


        # =================================================
        # CAMERA PANEL
        # =================================================

        camera_panel = tk.Frame(
            main_frame,
            bg=PANEL,
            width=720,
            height=620
        )

        camera_panel.pack(
            side="left",
            padx=(0, 12)
        )

        camera_panel.pack_propagate(False)


        # =================================================
        # CAMERA HEADER
        # =================================================

        camera_header = tk.Frame(
            camera_panel,
            bg=CARD,
            height=48
        )

        camera_header.pack(fill="x")
        camera_header.pack_propagate(False)

        tk.Label(
            camera_header,
            text="LIVE CAMERA MONITOR",
            font=("Segoe UI", 12, "bold"),
            bg=CARD,
            fg=WHITE
        ).pack(
            side="left",
            padx=16,
            pady=12
        )

        self.camera_state_label = tk.Label(
            camera_header,
            text="● OFFLINE",
            font=("Segoe UI", 9, "bold"),
            bg=CARD,
            fg=RED
        )

        self.camera_state_label.pack(
            side="right",
            padx=16
        )


        # =================================================
        # CAMERA DISPLAY
        # =================================================

        camera_display = tk.Frame(
            camera_panel,
            bg="#0F1A22"
        )

        camera_display.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.camera_label = tk.Label(
            camera_display,
            text="CAMERA IS STOPPED\n\nClick START to begin",
            font=("Segoe UI", 18),
            bg="#0F1A22",
            fg=TEXT,
            justify="center"
        )

        self.camera_label.pack(
            fill="both",
            expand=True
        )


        # =================================================
        # CAMERA FOOTER
        # =================================================

        camera_footer = tk.Frame(
            camera_panel,
            bg=CARD,
            height=38
        )

        camera_footer.pack(fill="x")
        camera_footer.pack_propagate(False)

        tk.Label(
            camera_footer,
            text="Resolution  640 × 480",
            font=("Segoe UI", 9),
            bg=CARD,
            fg=MUTED
        ).pack(
            side="left",
            padx=16,
            pady=9
        )

        tk.Label(
            camera_footer,
            text="MediaPipe Hand Tracking",
            font=("Segoe UI", 9),
            bg=CARD,
            fg=MUTED
        ).pack(
            side="right",
            padx=16,
            pady=9
        )


        # =================================================
        # CONTROL DASHBOARD
        # =================================================

        dashboard = tk.Frame(
            main_frame,
            bg=PANEL,
            width=450,
            height=620
        )

        dashboard.pack(
            side="right"
        )

        dashboard.pack_propagate(False)


        # =================================================
        # DASHBOARD TITLE
        # =================================================

        tk.Label(
            dashboard,
            text="CONTROL DASHBOARD",
            font=("Segoe UI", 15, "bold"),
            bg=PANEL,
            fg=WHITE
        ).place(
            x=0,
            y=7,
            width=450,
            height=30
        )


        # =================================================
        # SYSTEM STATUS CARD
        # =================================================

        status_card = tk.Frame(
            dashboard,
            bg=CARD
        )

        status_card.place(
            x=15,
            y=45,
            width=420,
            height=100
        )

        tk.Label(
            status_card,
            text="SYSTEM STATUS",
            font=("Segoe UI", 10, "bold"),
            bg=CARD,
            fg=MUTED
        ).place(
            x=0,
            y=8,
            width=420,
            height=20
        )

        self.status_label = tk.Label(
            status_card,
            text="● STOPPED",
            font=("Segoe UI", 13, "bold"),
            bg=CARD,
            fg=RED
        )

        self.status_label.place(
            x=0,
            y=32,
            width=420,
            height=22
        )

        self.gesture_label = tk.Label(
            status_card,
            text="System Ready",
            font=("Segoe UI", 12, "bold"),
            bg=CARD,
            fg=GREEN
        )

        self.gesture_label.place(
            x=0,
            y=56,
            width=420,
            height=22
        )

        self.hand_status = tk.Label(
            status_card,
            text="Hand: Not Detected",
            font=("Segoe UI", 9),
            bg=CARD,
            fg=TEXT
        )

        self.hand_status.place(
            x=0,
            y=79,
            width=420,
            height=18
        )


        # =================================================
        # SUPPORTED GESTURES CARD
        # =================================================

        gesture_card = tk.Frame(
            dashboard,
            bg=CARD
        )

        gesture_card.place(
            x=15,
            y=155,
            width=420,
            height=180
        )

        tk.Label(
            gesture_card,
            text="SUPPORTED GESTURES",
            font=("Segoe UI", 10, "bold"),
            bg=CARD,
            fg=MUTED
        ).pack(
            pady=(7, 4)
        )

        gesture_data = [
            ("01", "Index Finger", "Move Cursor"),
            ("02", "Quick Pinch", "Left Click"),
            ("03", "Hold Pinch", "Drag"),
            ("04", "Two Fingers", "Right Click"),
            ("05", "Open Palm", "Scroll"),
            ("06", "Closed Fist", "Stop")
        ]

        for number, gesture, action in gesture_data:

            row = tk.Frame(
                gesture_card,
                bg=CARD,
                height=22
            )

            row.pack(
                fill="x",
                padx=18,
                pady=0
            )

            row.pack_propagate(False)

            tk.Label(
                row,
                text=number,
                font=("Segoe UI", 8, "bold"),
                bg="#2C4857",
                fg=GREEN,
                width=3
            ).pack(
                side="left"
            )

            tk.Label(
                row,
                text=gesture,
                font=("Segoe UI", 9),
                bg=CARD,
                fg=WHITE,
                anchor="w"
            ).pack(
                side="left",
                padx=(8, 0)
            )

            tk.Label(
                row,
                text="→",
                font=("Segoe UI", 9, "bold"),
                bg=CARD,
                fg=GREEN
            ).pack(
                side="left",
                padx=8
            )

            tk.Label(
                row,
                text=action,
                font=("Segoe UI", 9),
                bg=CARD,
                fg=TEXT,
                anchor="w"
            ).pack(
                side="left"
            )


        # =================================================
        # DETECTION INFORMATION CARD
        # =================================================

        detection_card = tk.Frame(
            dashboard,
            bg=CARD
        )

        detection_card.place(
            x=15,
            y=345,
            width=420,
            height=85
        )

        tk.Label(
            detection_card,
            text="DETECTION INFORMATION",
            font=("Segoe UI", 10, "bold"),
            bg=CARD,
            fg=MUTED
        ).place(
            x=0,
            y=6,
            width=420,
            height=20
        )


        # FPS

        tk.Label(
            detection_card,
            text="FPS",
            font=("Segoe UI", 9),
            bg=CARD,
            fg=TEXT
        ).place(
            x=20,
            y=37
        )

        self.fps_value = tk.Label(
            detection_card,
            text="0",
            font=("Segoe UI", 9, "bold"),
            bg=CARD,
            fg=GREEN
        )

        self.fps_value.place(
            x=70,
            y=37
        )


        # Hand Confidence

        tk.Label(
            detection_card,
            text="Hand Confidence",
            font=("Segoe UI", 9),
            bg=CARD,
            fg=TEXT
        ).place(
            x=155,
            y=37
        )

        self.confidence_value = tk.Label(
            detection_card,
            text="0%",
            font=("Segoe UI", 9, "bold"),
            bg=CARD,
            fg=GREEN
        )

        self.confidence_value.place(
            x=285,
            y=37
        )


        # Camera

        tk.Label(
            detection_card,
            text="Camera",
            font=("Segoe UI", 9),
            bg=CARD,
            fg=TEXT
        ).place(
            x=20,
            y=62
        )

        tk.Label(
            detection_card,
            text="640 × 480",
            font=("Segoe UI", 9, "bold"),
            bg=CARD,
            fg=GREEN
        ).place(
            x=70,
            y=62
        )


        # =================================================
        # CONTROL SETTINGS CARD
        # =================================================

        settings_card = tk.Frame(
            dashboard,
            bg=CARD
        )

        settings_card.place(
            x=15,
            y=435,
            width=420,
            height=115
        )


        tk.Label(
            settings_card,
            text="CONTROL SETTINGS",
            font=("Segoe UI", 10, "bold"),
            bg=CARD,
            fg=MUTED
        ).place(
            x=0,
            y=5,
            width=420,
            height=20
        )


        # =================================================
        # CURSOR SMOOTHING
        # =================================================

        tk.Label(
            settings_card,
            text="Cursor Smoothing",
            font=("Segoe UI", 8),
            bg=CARD,
            fg=TEXT
        ).place(
            x=15,
            y=32
        )

        self.smoothing_scale = tk.Scale(
            settings_card,
            from_=1,
            to=15,
            orient="horizontal",
            showvalue=False,
            width=7,
            sliderlength=14,
            bg=CARD,
            fg=WHITE,
            highlightthickness=0,
            troughcolor="#425965",
            command=self.change_smoothing
        )

        self.smoothing_scale.set(5)

        self.smoothing_scale.place(
            x=135,
            y=25,
            width=185,
            height=30
        )

        self.smoothing_value = tk.Label(
            settings_card,
            text="5",
            font=("Segoe UI", 8, "bold"),
            bg=CARD,
            fg=GREEN
        )

        self.smoothing_value.place(
            x=350,
            y=32
        )


        # =================================================
        # PINCH SENSITIVITY
        # =================================================

        tk.Label(
            settings_card,
            text="Pinch Sensitivity",
            font=("Segoe UI", 8),
            bg=CARD,
            fg=TEXT
        ).place(
            x=15,
            y=62
        )

        self.pinch_scale = tk.Scale(
            settings_card,
            from_=20,
            to=60,
            orient="horizontal",
            showvalue=False,
            width=7,
            sliderlength=14,
            bg=CARD,
            fg=WHITE,
            highlightthickness=0,
            troughcolor="#425965",
            command=self.change_pinch
        )

        self.pinch_scale.set(35)

        self.pinch_scale.place(
            x=135,
            y=55,
            width=185,
            height=30
        )

        self.pinch_value = tk.Label(
            settings_card,
            text="35",
            font=("Segoe UI", 8, "bold"),
            bg=CARD,
            fg=GREEN
        )

        self.pinch_value.place(
            x=350,
            y=62
        )


        # =================================================
        # DRAG HOLD TIME
        # =================================================

        tk.Label(
            settings_card,
            text="Drag Hold Time",
            font=("Segoe UI", 8),
            bg=CARD,
            fg=TEXT
        ).place(
            x=15,
            y=92
        )

        self.drag_scale = tk.Scale(
            settings_card,
            from_=0.3,
            to=1.5,
            resolution=0.1,
            orient="horizontal",
            showvalue=False,
            width=7,
            sliderlength=14,
            bg=CARD,
            fg=WHITE,
            highlightthickness=0,
            troughcolor="#425965",
            command=self.change_drag
        )

        self.drag_scale.set(0.6)

        self.drag_scale.place(
            x=135,
            y=85,
            width=185,
            height=30
        )

        self.drag_value = tk.Label(
            settings_card,
            text="0.6s",
            font=("Segoe UI", 8, "bold"),
            bg=CARD,
            fg=GREEN
        )

        self.drag_value.place(
            x=350,
            y=92
        )


        # =================================================
        # BUTTON CARD
        # =================================================

        button_card = tk.Frame(
            dashboard,
            bg=CARD_DARK
        )

        button_card.place(
            x=15,
            y=555,
            width=420,
            height=65
        )


        # =================================================
        # START BUTTON
        # =================================================

        self.start_button = tk.Button(
            button_card,
            text="▶  START",
            command=self.start_camera,
            font=("Segoe UI", 10, "bold"),
            bg=GREEN_DARK,
            fg=WHITE,
            activebackground=GREEN,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        self.start_button.place(
            x=10,
            y=12,
            width=120,
            height=40
        )


        # =================================================
        # STOP BUTTON
        # =================================================

        self.stop_button = tk.Button(
            button_card,
            text="■  STOP",
            command=self.stop_camera,
            font=("Segoe UI", 10, "bold"),
            bg="#4B5A62",
            fg="#AAB4BA",
            activebackground=RED,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="",
            state="disabled"
        )

        self.stop_button.place(
            x=150,
            y=12,
            width=120,
            height=40
        )


        # =================================================
        # RESET BUTTON
        # =================================================

        self.reset_button = tk.Button(
            button_card,
            text="↻  RESET",
            command=self.reset_settings,
            font=("Segoe UI", 10, "bold"),
            bg=BLUE,
            fg=WHITE,
            activebackground=BLUE_ACTIVE,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        self.reset_button.place(
            x=290,
            y=12,
            width=120,
            height=40
        )


        # =================================================
        # FOOTER
        # =================================================

        footer = tk.Frame(
            self.root,
            bg=BG,
            height=38
        )

        footer.pack(fill="x")
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="B.Tech CSE Project  •  OpenCV  •  MediaPipe  •  PyAutoGUI",
            font=("Segoe UI", 9),
            bg=BG,
            fg="#71818C"
        ).pack(
            pady=9
        )


    # =====================================================
    # SETTINGS FUNCTIONS
    # =====================================================

    def change_smoothing(self, value):

        self.smoothing = int(float(value))

        self.smoothing_value.config(
            text=str(self.smoothing)
        )


    def change_pinch(self, value):

        self.pinch_threshold = int(float(value))

        self.pinch_value.config(
            text=str(self.pinch_threshold)
        )


    def change_drag(self, value):

        self.drag_hold_time = float(value)

        self.drag_value.config(
            text=f"{self.drag_hold_time:.1f}s"
        )


    # =====================================================
    # RESET
    # =====================================================

    def reset_settings(self):

        self.smoothing = 5
        self.pinch_threshold = 35
        self.drag_hold_time = 0.6

        self.smoothing_scale.set(5)
        self.pinch_scale.set(35)
        self.drag_scale.set(0.6)

        self.smoothing_value.config(
            text="5"
        )

        self.pinch_value.config(
            text="35"
        )

        self.drag_value.config(
            text="0.6s"
        )

        self.prev_x = None
        self.prev_y = None

        self.pinch_started = False
        self.dragging = False

        self.previous_palm_y = None

        self.fist_started = False
        self.fist_start_time = 0

        self.gesture_label.config(
            text="System Ready"
        )


    # =====================================================
    # START CAMERA
    # =====================================================

    def start_camera(self):

        if self.running:
            return

        self.cap = cv2.VideoCapture(0)

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            CAMERA_WIDTH
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            CAMERA_HEIGHT
        )

        if not self.cap.isOpened():

            self.gesture_label.config(
                text="Camera Error",
                fg=RED
            )

            self.hand_status.config(
                text="Hand: Camera unavailable"
            )

            self.camera_state_label.config(
                text="● ERROR",
                fg=RED
            )

            return

        self.running = True

        self.prev_x = None
        self.prev_y = None

        self.pinch_started = False
        self.dragging = False

        self.previous_palm_y = None

        self.fist_started = False
        self.fist_start_time = 0

        self.frame_count = 0
        self.fps = 0
        self.fps_start_time = time.time()

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status_label.config(
            text="● RUNNING",
            fg=GREEN
        )

        self.gesture_label.config(
            text="Detecting Hand...",
            fg=GREEN
        )

        self.hand_status.config(
            text="Hand: Searching..."
        )

        self.camera_state_label.config(
            text="● LIVE",
            fg=GREEN
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        self.start_button.config(
            state="disabled",
            bg="#4B5A62",
            fg="#AAB4BA",
            cursor=""
        )

        self.stop_button.config(
            state="normal",
            bg=RED_DARK,
            fg=WHITE,
            cursor="hand2"
        )

        self.camera_label.config(
            text=""
        )

        self.update_camera()


    # =====================================================
    # STOP CAMERA
    # =====================================================

    def stop_camera(self):

        if self.dragging:

            try:
                pyautogui.mouseUp()
            except:
                pass

            self.dragging = False

        if self.cap is not None:

            self.cap.release()
            self.cap = None

        self.running = False

        self.prev_x = None
        self.prev_y = None

        self.pinch_started = False
        self.previous_palm_y = None

        self.fist_started = False
        self.fist_start_time = 0

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status_label.config(
            text="● STOPPED",
            fg=RED
        )

        self.gesture_label.config(
            text="System Ready",
            fg=GREEN
        )

        self.hand_status.config(
            text="Hand: Not Detected"
        )

        self.camera_state_label.config(
            text="● OFFLINE",
            fg=RED
        )

        self.fps_value.config(
            text="0"
        )

        self.confidence_value.config(
            text="0%"
        )

        # -------------------------------------------------
        # CAMERA
        # -------------------------------------------------

        self.camera_label.config(
            image="",
            text="CAMERA IS STOPPED\n\nClick START to begin",
            font=("Segoe UI", 18),
            bg="#0F1A22",
            fg=TEXT
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        self.start_button.config(
            state="normal",
            bg=GREEN_DARK,
            fg=WHITE,
            cursor="hand2"
        )

        self.stop_button.config(
            state="disabled",
            bg="#4B5A62",
            fg="#AAB4BA",
            cursor=""
        )


    # =====================================================
    # DISTANCE
    # =====================================================

    def distance(self, p1, p2):

        return math.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2
        )


    # =====================================================
    # FINGER STATES
    # =====================================================

    def get_finger_states(self, landmarks):

        index_up = (
            landmarks[8].y <
            landmarks[6].y
        )

        middle_up = (
            landmarks[12].y <
            landmarks[10].y
        )

        ring_up = (
            landmarks[16].y <
            landmarks[14].y
        )

        pinky_up = (
            landmarks[20].y <
            landmarks[18].y
        )

        return (
            index_up,
            middle_up,
            ring_up,
            pinky_up
        )


    # =====================================================
    # MOVE CURSOR
    # =====================================================

    def move_cursor(self, landmark):

        target_x = int(
            landmark.x * SCREEN_WIDTH
        )

        target_y = int(
            landmark.y * SCREEN_HEIGHT
        )

        target_x = max(
            0,
            min(
                SCREEN_WIDTH - 1,
                target_x
            )
        )

        target_y = max(
            0,
            min(
                SCREEN_HEIGHT - 1,
                target_y
            )
        )

        if self.prev_x is None:

            self.prev_x = target_x
            self.prev_y = target_y

            return

        smooth_factor = max(
            1,
            self.smoothing
        )

        current_x = (
            self.prev_x +
            (target_x - self.prev_x) /
            smooth_factor
        )

        current_y = (
            self.prev_y +
            (target_y - self.prev_y) /
            smooth_factor
        )

        try:

            pyautogui.moveTo(
                int(current_x),
                int(current_y),
                duration=0
            )

        except:
            pass

        self.prev_x = current_x
        self.prev_y = current_y


    # =====================================================
    # CAMERA UPDATE
    # =====================================================

    def update_camera(self):

        if not self.running:
            return

        if self.cap is None:
            return

        ret, frame = self.cap.read()

        if not ret:

            self.stop_camera()
            return

        # -------------------------------------------------
        # MIRROR CAMERA
        # -------------------------------------------------

        frame = cv2.flip(
            frame,
            1
        )


        # =================================================
        # FPS
        # =================================================

        self.frame_count += 1

        elapsed = (
            time.time() -
            self.fps_start_time
        )

        if elapsed >= 1:

            self.fps = int(
                self.frame_count /
                elapsed
            )

            self.frame_count = 0

            self.fps_start_time = time.time()

        self.fps_value.config(
            text=str(self.fps)
        )


        # =================================================
        # MEDIAPIPE
        # =================================================

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = hands.process(
            rgb_frame
        )

        gesture = "No Hand Detected"


        # =================================================
        # HAND DETECTED
        # =================================================

        if results.multi_hand_landmarks:

            hand_landmarks = (
                results.multi_hand_landmarks[0]
            )

            # Visual confidence indicator
            confidence = 95

            self.confidence_value.config(
                text=f"{confidence}%"
            )

            self.hand_status.config(
                text="Hand: Detected"
            )

            # Draw landmarks

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            landmarks = (
                hand_landmarks.landmark
            )


            # =================================================
            # FINGER STATES
            # =================================================

            (
                index_up,
                middle_up,
                ring_up,
                pinky_up
            ) = self.get_finger_states(
                landmarks
            )


            # =================================================
            # PINCH DISTANCE
            # =================================================

            pinch_distance = (
                self.distance(
                    landmarks[8],
                    landmarks[4]
                ) * 1000
            )


            # =================================================
            # CLOSED FIST -> STOP
            # =================================================

            closed_fist = (
                not index_up
                and not middle_up
                and not ring_up
                and not pinky_up
            )

            if closed_fist:

                if not self.fist_started:

                    self.fist_started = True

                    self.fist_start_time = time.time()

                fist_duration = (
                    time.time() -
                    self.fist_start_time
                )

                remaining = (
                    STOP_HOLD_TIME -
                    fist_duration
                )

                if remaining > 0:

                    gesture = (
                        f"CLOSED FIST | "
                        f"STOP IN {remaining:.1f}s"
                    )

                else:

                    self.stop_camera()
                    return


            else:

                self.fist_started = False


                # =================================================
                # OPEN PALM -> SCROLL
                # =================================================

                open_palm = (
                    index_up
                    and middle_up
                    and ring_up
                    and pinky_up
                )

                if open_palm:

                    gesture = "Open Palm | Scroll"

                    palm_y = landmarks[9].y

                    if (
                        self.previous_palm_y
                        is not None
                    ):

                        movement = (
                            palm_y -
                            self.previous_palm_y
                        )

                        if abs(movement) > 0.015:

                            scroll_amount = int(
                                -movement *
                                120 *
                                self.scroll_sensitivity
                            )

                            if scroll_amount != 0:

                                try:

                                    pyautogui.scroll(
                                        scroll_amount
                                    )

                                except:
                                    pass

                    self.previous_palm_y = palm_y

                    self.prev_x = None
                    self.prev_y = None


                else:

                    self.previous_palm_y = None


                    # =================================================
                    # TWO FINGERS -> RIGHT CLICK
                    # =================================================

                    two_fingers = (
                        index_up
                        and middle_up
                        and not ring_up
                        and not pinky_up
                        and pinch_distance >
                        self.pinch_threshold
                    )

                    if two_fingers:

                        gesture = (
                            "Two Fingers | Right Click"
                        )

                        current_time = time.time()

                        if (
                            current_time -
                            self.last_right_click_time
                            > CLICK_COOLDOWN
                        ):

                            try:

                                pyautogui.rightClick()

                            except:
                                pass

                            self.last_right_click_time = (
                                current_time
                            )

                        self.prev_x = None
                        self.prev_y = None


                    # =================================================
                    # PINCH
                    # =================================================

                    elif (
                        pinch_distance <
                        self.pinch_threshold
                    ):

                        if not self.pinch_started:

                            self.pinch_started = True

                            self.pinch_start_time = (
                                time.time()
                            )

                        pinch_duration = (
                            time.time() -
                            self.pinch_start_time
                        )


                        # ---------------------------------------------
                        # HOLD PINCH -> DRAG
                        # ---------------------------------------------

                        if (
                            pinch_duration >=
                            self.drag_hold_time
                        ):

                            gesture = (
                                "Hold Pinch | Drag"
                            )

                            if not self.dragging:

                                try:

                                    pyautogui.mouseDown()

                                except:
                                    pass

                                self.dragging = True

                            self.move_cursor(
                                landmarks[8]
                            )

                        else:

                            gesture = (
                                "Quick Pinch | Left Click"
                            )


                    # =================================================
                    # PINCH RELEASE
                    # =================================================

                    else:

                        if self.pinch_started:

                            pinch_duration = (
                                time.time() -
                                self.pinch_start_time
                            )

                            if self.dragging:

                                try:

                                    pyautogui.mouseUp()

                                except:
                                    pass

                                self.dragging = False

                            elif (
                                pinch_duration <
                                self.drag_hold_time
                            ):

                                current_time = time.time()

                                if (
                                    current_time -
                                    self.last_click_time
                                    > CLICK_COOLDOWN
                                ):

                                    try:

                                        pyautogui.click()

                                    except:
                                        pass

                                    self.last_click_time = (
                                        current_time
                                    )

                        self.pinch_started = False


                        # =================================================
                        # INDEX FINGER -> MOVE CURSOR
                        # =================================================

                        if (
                            index_up
                            and not middle_up
                            and not ring_up
                            and not pinky_up
                        ):

                            gesture = (
                                "Index Finger | Move Cursor"
                            )

                            self.move_cursor(
                                landmarks[8]
                            )

                        else:

                            self.prev_x = None
                            self.prev_y = None


            # =================================================
            # CAMERA OVERLAY
            # =================================================

            cv2.rectangle(
                frame,
                (0, 0),
                (640, 125),
                (11, 20, 27),
                -1
            )

            cv2.putText(
                frame,
                gesture,
                (15, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (0, 255, 120),
                2
            )

            cv2.putText(
                frame,
                f"FPS: {self.fps}",
                (15, 62),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Hand: DETECTED",
                (15, 88),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (0, 255, 120),
                2
            )

            cv2.putText(
                frame,
                f"Pinch Distance: {int(pinch_distance)}",
                (15, 114),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2
            )


        # =================================================
        # NO HAND
        # =================================================

        else:

            self.confidence_value.config(
                text="0%"
            )

            self.hand_status.config(
                text="Hand: Not Detected"
            )

            self.prev_x = None
            self.prev_y = None

            self.previous_palm_y = None

            self.fist_started = False

            cv2.rectangle(
                frame,
                (0, 0),
                (640, 70),
                (11, 20, 27),
                -1
            )

            cv2.putText(
                frame,
                "NO HAND DETECTED",
                (15, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 180, 80),
                2
            )

            cv2.putText(
                frame,
                f"FPS: {self.fps}",
                (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (255, 255, 255),
                2
            )


        # =================================================
        # UPDATE CURRENT GESTURE
        # =================================================

        self.gesture_label.config(
            text=gesture
        )


        # =================================================
        # DISPLAY CAMERA
        # =================================================

        rgb_display = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(
            rgb_display
        )

        image = image.resize(
            (680, 510),
            Image.Resampling.LANCZOS
        )

        self.frame_photo = ImageTk.PhotoImage(
            image=image
        )

        self.camera_label.config(
            image=self.frame_photo,
            text=""
        )


        # =================================================
        # KEYBOARD STOP
        # =================================================

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            self.stop_camera()
            return


        # =================================================
        # NEXT FRAME
        # =================================================

        self.root.after(
            10,
            self.update_camera
        )


    # =====================================================
    # CLOSE APPLICATION
    # =====================================================

    def close_application(self):

        if self.dragging:

            try:
                pyautogui.mouseUp()
            except:
                pass

        if self.cap is not None:

            self.cap.release()
            self.cap = None

        self.running = False

        try:
            hands.close()
        except:
            pass

        self.root.destroy()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = HandGestureApp(root)

    root.mainloop()