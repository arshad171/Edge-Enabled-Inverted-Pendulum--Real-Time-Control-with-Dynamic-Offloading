import cv2
import numpy as np
import time

batch_size = 1

frame_width = 1920
frame_height = 1080

def get_data(batch_size):
    return np.random.randint(0, 256, (frame_height, frame_width, 3), dtype=np.uint8)


class Model:
    def __init__(self):
        # weights = th.load("module/weights.pth")
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters()

        self.detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    def predict(self, batch_size=batch_size):

        frame = get_data(batch_size)

        lower_line = 150
        detections = {}

        for _ in range(1):
            # if len(detections) == 2:
            #     break
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect ArUco markers
            corners, ids, rejected = self.detector.detectMarkers(gray)

            if ids is not None:

                n_detections = ids.shape[0]

                if n_detections != 2:
                    continue

                for ix in range(n_detections):
                    m_id = ids[ix][0]
                    m_corners = corners[ix][0]

                    m_corners_arr = np.array(m_corners)
                    m_x = m_corners_arr[:, 0]
                    m_y = m_corners_arr[:, 1]

                    x_min, x_max = min(m_x), max(m_x)
                    y_min, y_max = min(m_y), max(m_y)

                    detections[int(m_id)] = (int((x_min + x_max) /2), int((y_min + y_max) / 2))

        if 2 in detections:
            # Store coordinates of detected objects in the upper half (tip point)
            tip_point = {'x': detections[2][0], 'y': detections[2][1]}
        else:
            tip_point = {'x': 100, 'y': 200}

        if 10 in detections:
            # Store coordinates of detected objects in the lower half (fixed point)
            fixed_point = {"x": detections[10][0], "y": detections[10][1]}
        else:
            fixed_point = {"x": 100, "y": 100}

        return {
            "tip_point": tip_point,
            "fixed_point": fixed_point,
        }

m = Model()
m.predict()
