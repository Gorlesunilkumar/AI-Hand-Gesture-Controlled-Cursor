import cv2
import mediapipe as mp
import pyautogui
import math
import time


# =========================================================
# SETTINGS
# =========================================================

screen_width, screen_height = pyautogui.size()

frame_width = 640
frame_height = 480

# Cursor movement settings
margin = 100
smoothening = 5

# Pinch settings
pinch_threshold = 35

# Click settings
click_cooldown = 0.5

# Drag settings
drag_hold_time = 0.6

# Scroll settings
scroll_sensitivity = 4


# =========================================================
# VARIABLES
# =========================================================

prev_x = 0
prev_y = 0

# Click
last_click_time = 0
last_right_click_time = 0

# Pinch / Drag
pinch_started = False
pinch_start_time = 0
dragging = False

# Scroll
previous_palm_y = None


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
# WEBCAM SETUP
# =========================================================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)


if not cap.isOpened():

    print("❌ Could not open webcam.")

    exit()


# =========================================================
# START MESSAGE
# =========================================================

print()
print("==============================================")
print("     AI HAND GESTURE CURSOR CONTROLLER")
print("==============================================")
print()
print("☝️  Index Finger       → Move Cursor")
print("🤏 Quick Pinch        → Left Click")
print("🤏 Hold Pinch         → Drag")
print("✋ Release Pinch      → Drop")
print("✌️  Two Fingers       → Right Click")
print("🖐️  Open Palm         → Scroll")
print("❌ Press Q            → Quit")
print()
print("==============================================")
print()


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    # -----------------------------------------------------
    # READ CAMERA
    # -----------------------------------------------------

    success, frame = cap.read()

    if not success:

        print("❌ Failed to read webcam.")

        break


    # Mirror camera
    frame = cv2.flip(frame, 1)


    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # Process hand
    results = hands.process(rgb_frame)


    # Default gesture
    gesture_text = "No Hand"


    # =====================================================
    # HAND DETECTED
    # =====================================================

    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            # -------------------------------------------------
            # DRAW LANDMARKS
            # -------------------------------------------------

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )


            # -------------------------------------------------
            # GET LANDMARKS
            # -------------------------------------------------

            thumb = hand_landmarks.landmark[4]

            index = hand_landmarks.landmark[8]

            middle = hand_landmarks.landmark[12]

            ring = hand_landmarks.landmark[16]

            pinky = hand_landmarks.landmark[20]

            wrist = hand_landmarks.landmark[0]


            # -------------------------------------------------
            # CONVERT LANDMARKS TO PIXELS
            # -------------------------------------------------

            thumb_x = int(
                thumb.x * frame_width
            )

            thumb_y = int(
                thumb.y * frame_height
            )


            index_x = int(
                index.x * frame_width
            )

            index_y = int(
                index.y * frame_height
            )


            wrist_y = int(
                wrist.y * frame_height
            )


            # =================================================
            # PINCH DISTANCE
            # =================================================

            pinch_distance = math.sqrt(

                (index_x - thumb_x) ** 2

                +

                (index_y - thumb_y) ** 2
            )


            # =================================================
            # FINGER DETECTION
            # =================================================

            index_up = (
                index.y
                <
                hand_landmarks.landmark[6].y
            )


            middle_up = (
                middle.y
                <
                hand_landmarks.landmark[10].y
            )


            ring_up = (
                ring.y
                <
                hand_landmarks.landmark[14].y
            )


            pinky_up = (
                pinky.y
                <
                hand_landmarks.landmark[18].y
            )


            # =================================================
            # CURSOR POSITION
            # =================================================

            x = index_x

            y = index_y


            # Keep cursor inside camera control area
            x = max(
                margin,
                min(
                    x,
                    frame_width - margin
                )
            )


            y = max(
                margin,
                min(
                    y,
                    frame_height - margin
                )
            )


            # Convert camera coordinates
            # to screen coordinates

            screen_x = int(

                (x - margin)
                *
                screen_width
                /
                (frame_width - 2 * margin)
            )


            screen_y = int(

                (y - margin)
                *
                screen_height
                /
                (frame_height - 2 * margin)
            )


            # Keep screen coordinates valid

            screen_x = max(
                0,
                min(
                    screen_x,
                    screen_width - 1
                )
            )


            screen_y = max(
                0,
                min(
                    screen_y,
                    screen_height - 1
                )
            )


            # =================================================
            # SMOOTH CURSOR MOVEMENT
            # =================================================

            current_x = (
                prev_x
                +
                (
                    screen_x - prev_x
                )
                /
                smoothening
            )


            current_y = (
                prev_y
                +
                (
                    screen_y - prev_y
                )
                /
                smoothening
            )


            # =================================================
            # OPEN PALM
            # =================================================

            open_palm = (

                index_up

                and middle_up

                and ring_up

                and pinky_up

                and pinch_distance > pinch_threshold
            )


            if open_palm:

                gesture_text = "OPEN PALM - SCROLL"


                # Detect palm movement

                if previous_palm_y is not None:

                    movement = (
                        previous_palm_y
                        -
                        wrist_y
                    )


                    if abs(movement) > 5:

                        scroll_amount = int(

                            movement
                            /
                            scroll_sensitivity
                        )


                        if scroll_amount != 0:

                            pyautogui.scroll(
                                scroll_amount
                            )


                previous_palm_y = wrist_y


            else:

                previous_palm_y = None


            # =================================================
            # RIGHT CLICK
            # =================================================

            two_finger_gesture = (

                index_up

                and middle_up

                and not ring_up

                and not pinky_up

                and pinch_distance > pinch_threshold
            )


            if two_finger_gesture:

                gesture_text = "RIGHT CLICK"


                current_time = time.time()


                if (

                    current_time
                    -
                    last_right_click_time
                    >
                    click_cooldown

                ):

                    pyautogui.rightClick()


                    last_right_click_time = (
                        current_time
                    )


            # =================================================
            # PINCH
            # =================================================

            pinch = (
                pinch_distance
                <
                pinch_threshold
            )


            current_time = time.time()


            if pinch:

                gesture_text = "PINCH"


                # ---------------------------------------------
                # PINCH STARTED
                # ---------------------------------------------

                if not pinch_started:

                    pinch_started = True

                    pinch_start_time = (
                        current_time
                    )


                # How long pinch is held

                pinch_duration = (

                    current_time
                    -
                    pinch_start_time
                )


                # ---------------------------------------------
                # START DRAG
                # ---------------------------------------------

                if (

                    pinch_duration
                    >=
                    drag_hold_time

                    and

                    not dragging

                ):

                    pyautogui.mouseDown()

                    dragging = True

                    gesture_text = "DRAGGING"


                elif dragging:

                    gesture_text = "DRAGGING"


            else:

                # ---------------------------------------------
                # PINCH RELEASED
                # ---------------------------------------------

                if pinch_started:

                    pinch_duration = (

                        current_time
                        -
                        pinch_start_time
                    )


                    # -----------------------------------------
                    # END DRAG
                    # -----------------------------------------

                    if dragging:

                        pyautogui.mouseUp()

                        dragging = False

                        gesture_text = "DROP"


                    # -----------------------------------------
                    # NORMAL LEFT CLICK
                    # -----------------------------------------

                    elif (

                        pinch_duration
                        <
                        drag_hold_time

                    ):

                        if (

                            current_time
                            -
                            last_click_time
                            >
                            click_cooldown

                        ):

                            pyautogui.click()

                            last_click_time = (
                                current_time
                            )

                            gesture_text = "LEFT CLICK"


                    pinch_started = False


            # =================================================
            # MOVE CURSOR
            # =================================================

            if (

                not open_palm

                and

                not two_finger_gesture

            ):

                pyautogui.moveTo(

                    int(current_x),

                    int(current_y),

                    duration=0
                )


            # Save cursor position

            prev_x = current_x

            prev_y = current_y


            # =================================================
            # DISPLAY PINCH DISTANCE
            # =================================================

            cv2.putText(

                frame,

                f"Pinch: {int(pinch_distance)}",

                (10, 70),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255, 255, 255),

                2
            )


    # =========================================================
    # DISPLAY GESTURE
    # =========================================================

    cv2.putText(

        frame,

        f"Gesture: {gesture_text}",

        (10, 40),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        (0, 255, 0),

        2
    )


    # =========================================================
    # INSTRUCTIONS
    # =========================================================

    cv2.putText(

        frame,

        "Q = Quit",

        (10, frame_height - 20),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.6,

        (255, 255, 255),

        2
    )


    # =========================================================
    # SHOW CAMERA WINDOW
    # =========================================================

    cv2.imshow(

        "AI Hand Gesture Cursor",

        frame
    )


    # =========================================================
    # QUIT
    # =========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# =========================================================
# CLEANUP
# =========================================================

if dragging:

    pyautogui.mouseUp()


cap.release()

cv2.destroyAllWindows()

hands.close()


print()
print("✅ Program stopped successfully.")