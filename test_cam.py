import cv2
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
else:
    ret, frame = cap.read()
    if ret:
        print(f"Success! Captured frame of size: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
