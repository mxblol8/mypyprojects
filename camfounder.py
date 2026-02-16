import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    print(i, cap.isOpened())
    cap.release()
print("กล้องที่ใช้งานได้คือ")