print("Starting the main program. . .")
input("READY! Press Enter to continue")

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

print("IMPORT MODULES. . .")
import cv2
import mediapipe as mp
import pyautogui
import math
import time
print("MODULES IMPORTED!")

pyautogui.FAILSAFE = False

print("MAIN START")

# ================== CAMERA SETUP (ปรับให้ลื่นขึ้น) ==================
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("❌ เปิดกล้องไม่ได้")
    input("ENTER TO EXIT")
    exit()

screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,  # ปรับให้เร็วขึ้น
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

print("✅ SYSTEM READY (press q to quit)")

# ================== VARIABLES ==================
last_click_time = 0
click_delay = 0.6

prev_x, prev_y = 0, 0
smoothening = 7  # เพิ่มความลื่น

prev_scroll_y = 0
prev_time = 0

# ================== LOOP ==================
while True:
    ret, img = cap.read()
    if not ret:
        print("❌ อ่านภาพจากกล้องไม่ได้")
        break

    img = cv2.flip(img, 1)

    # ลด noise ทำให้ landmark นิ่งขึ้น
    img = cv2.GaussianBlur(img, (5, 5), 0)

    h, w, _ = img.shape

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            lm = hand.landmark

            # ================== ตรวจ "กำมือ" ==================
            fingers_folded = 0
            finger_tips = [8, 12, 16, 20]
            finger_pips = [6, 10, 14, 18]

            for tip, pip in zip(finger_tips, finger_pips):
                if lm[tip].y > lm[pip].y:
                    fingers_folded += 1

            fist = fingers_folded == 4

            if fist:
                cv2.putText(img, "PAUSE", (40, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 2)

            if not fist:

                ix = int(lm[8].x * w)
                iy = int(lm[8].y * h)

                mx = int(lm[12].x * w)
                my = int(lm[12].y * h)

                rx = int(lm[16].x * w)
                ry = int(lm[16].y * h)

                tx = int(lm[4].x * w)
                ty = int(lm[4].y * h)

                # ===== Smooth Mouse Movement =====
                screen_x = screen_w * lm[8].x
                screen_y = screen_h * lm[8].y

                curr_x = prev_x + (screen_x - prev_x) / smoothening
                curr_y = prev_y + (screen_y - prev_y) / smoothening

                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y

                cv2.circle(img, (ix, iy), 10, (255, 0, 255), -1)

                now = time.time()

                # ===== LEFT CLICK =====
                distance_click = math.hypot(ix - tx, iy - ty)
                if distance_click < 30 and now - last_click_time > click_delay:
                    pyautogui.click()
                    last_click_time = now
                    cv2.putText(img, "LEFT CLICK", (40, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 2)

                # ===== RIGHT CLICK =====
                distance_right = math.hypot(rx - tx, ry - ty)
                if distance_right < 30 and now - last_click_time > click_delay:
                    pyautogui.rightClick()
                    last_click_time = now
                    cv2.putText(img, "RIGHT CLICK", (40, 140),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 2)

                # ===== SCROLL MODE =====
                if lm[8].y < lm[6].y and lm[12].y < lm[10].y:
                    cv2.putText(img, "SCROLL MODE", (40, 180),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 255, 0), 2)

                    if prev_scroll_y != 0:
                        diff = iy - prev_scroll_y
                        pyautogui.scroll(-diff * 3)

                    prev_scroll_y = iy
                else:
                    prev_scroll_y = 0

            mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

    # ===== FPS COUNTER =====
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
    prev_time = curr_time

    cv2.putText(img, f"FPS: {int(fps)}", (500, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0, 255, 0), 2)

    cv2.imshow("AI Virtual Mouse PRO", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
