import cv2
import sys
import time
import numpy as np

OUTPUT_FILE = "camera_feed.png"
CAPTURE_INTERVAL = 0.1 

lower_brown = np.array([10, 100, 20])  
upper_brown = np.array([30, 255, 200])

def detect_brown_bag(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
    mask = cv2.inRange(hsv, lower_brown, upper_brown)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected = False
    for contour in contours:
        if cv2.contourArea(contour) > 1000: 
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) 
            cv2.putText(frame, "Brown Bag", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            detected = True
    
    return frame, detected

def main():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        sys.exit(1)
        
    print("Camera initialized successfully")
    print(f"Capturing frames every {CAPTURE_INTERVAL} seconds")
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Could not grab frame from camera")
                break

            processed_frame, detected = detect_brown_bag(frame)

            if detected:
                print("Brown bag detected!")

            cv2.imwrite(OUTPUT_FILE, processed_frame)

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(CAPTURE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStopping camera capture")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Camera released")

if __name__ == "__main__":
    main()
