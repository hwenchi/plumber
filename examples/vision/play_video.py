import cv2

from plumber.decorator import valve

FONT = cv2.FONT_HERSHEY_SIMPLEX


@valve(inlet="detected", poll_interval=0.02)
def play_video(d):
    image = cv2.imread(d["path"])
    detections = d["detections"]

    cv2.putText(image, f"frame {d['frame_id']}  detections {len(detections)}", (10, 20), FONT, 0.5, (255, 255, 0), 1)
    for i, det in enumerate(detections):
        text = f"{i}: x={det['x']:.0f} y={det['y']:.0f} r={det['radius']:.0f}"
        cv2.putText(image, text, (10, 40 + i * 18), FONT, 0.45, (255, 255, 255), 1)

    cv2.imshow("plumber vision demo", image)
    cv2.waitKey(1)
