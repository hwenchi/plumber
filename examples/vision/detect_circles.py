import random

import cv2

from plumber.decorator import valve

CRASH_PROBABILITY = 0.002


@valve(inlet="frames", outlet="detected", poll_interval=0.02)
def detect_circles(d):
    if random.random() < CRASH_PROBABILITY:
        raise RuntimeError("simulated crash in detect_circles")

    image = cv2.imread(d["path"])
    gray = cv2.medianBlur(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 5)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=50,
        param2=18,
        minRadius=5,
        maxRadius=60,
    )

    detections = []
    if circles is not None:
        for x, y, r in circles[0]:
            detections.append({"x": float(x), "y": float(y), "radius": float(r)})
            cv2.circle(image, (int(x), int(y)), int(r), (255, 255, 255), 2)
            cv2.circle(image, (int(x), int(y)), 2, (0, 0, 255), 3)

    annotated_path = d["path"].replace("frame_", "detected_")
    cv2.imwrite(annotated_path, image)

    return [{"path": annotated_path, "frame_id": d["frame_id"], "detections": detections}]