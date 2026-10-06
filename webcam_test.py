import cv2

# Open the default webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Could not open the webcam.")
    exit()

print("✅ Webcam started!")
print("Press Q to quit.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("❌ Failed to read frame.")
        break

    # Mirror the camera
    frame = cv2.flip(frame, 1)

    # Display the webcam
    cv2.imshow("Hand Gesture Cursor - Webcam Test", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()