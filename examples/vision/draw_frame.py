import os

import cv2
import numpy as np

from plumber.decorator import valve
from examples.vision.shared import FRAME_DIR, HEIGHT, WIDTH


@valve(inlet="positions", outlet="frames", poll_interval=0.02)
def draw_frame(d):
    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for ball in d["balls"]:
        center = (int(ball["x"]), int(ball["y"]))
        cv2.circle(canvas, center, ball["radius"], tuple(ball["color"]), -1)

    os.makedirs(FRAME_DIR, exist_ok=True)
    path = os.path.join(FRAME_DIR, f"frame_{d['frame_id']:05d}.png")
    cv2.imwrite(path, canvas)

    return [{"path": path, "frame_id": d["frame_id"]}]