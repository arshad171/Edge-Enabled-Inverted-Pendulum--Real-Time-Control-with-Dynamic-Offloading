import cv2
import numpy as np

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise ValueError("Could not open webcam")

# Define the dictionary and parameters
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters()

# Create the ArUco detector
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

print("Press 'q' to quit")

while True:
    # Capture frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect ArUco markers
    corners, ids, rejected = detector.detectMarkers(gray)


    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        print("Detected markers:", ids.flatten())

        detections = {}

        n_detections = ids.shape[0]

        for ix in range(n_detections):
            m_id = ids[ix][0]
            m_corners = corners[ix][0]

            m_corners_arr = np.array(m_corners)
            m_x = m_corners_arr[:, 0]
            m_y = m_corners_arr[:, 1]

            x_min, x_max = min(m_x), max(m_x)
            y_min, y_max = min(m_y), max(m_y)

            detections[m_id] = (float((x_min + x_max) /2), float((y_min + y_max) / 2))

        print(detections)
        
    # Show the frame
    cv2.imshow("Webcam ArUco Detection", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
