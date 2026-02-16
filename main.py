print("Starting the main program. . .")
input("READY! Press Enter to continue")

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # ลด warning เงียบ ๆ ของ mediapipe

print("IMPORT MODULES. . ." )
import cv2
import mediapipe as mp
import pyautogui
import math
import time
print("MODULES IMPORTED!")

pyautogui.FAILSAFE = False

print("MAIN START")

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("❌ เปิดกล้องไม่ได้")
    input("ENTER TO EXIT")
    exit()

screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

print("✅ SYSTEM READY (press q to quit)")

# ================== LOOP ==================
last_click_time = 0
click_delay = 0.6

while True:
    ret, img = cap.read()
    if not ret:
        print("❌ อ่านภาพจากกล้องไม่ได้")
        break

    img = cv2.flip(img, 1)
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
                cv2.putText(
                    img, "PAUSE",
                    (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

            # ================== ถ้าไม่กำมือ → เมาส์ทำงาน ==================
            if not fist:
                # นิ้วชี้
                ix = int(lm[8].x * w)
                iy = int(lm[8].y * h)

                # นิ้วโป้ง
                tx = int(lm[4].x * w)
                ty = int(lm[4].y * h)

                # ขยับเมาส์
                screen_x = int(screen_w * lm[8].x)
                screen_y = int(screen_h * lm[8].y)
                pyautogui.moveTo(screen_x, screen_y)

                cv2.circle(img, (ix, iy), 10, (255, 0, 255), -1)

                distance = math.hypot(ix - tx, iy - ty)

                now = time.time()
                if distance < 30 and now - last_click_time > click_delay:
                    pyautogui.click()
                    last_click_time = now
                    cv2.putText(
                        img, "CLICK",
                        (40, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

            mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("AI Virtual Mouse", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
