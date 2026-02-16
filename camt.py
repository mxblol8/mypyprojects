import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("camera opened:", cap.isOpened())

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()