import os

from examples.vision.detect_circles import detect_circles
from examples.vision.draw_frame import draw_frame
from examples.vision.generate_positions import generate_positions
from examples.vision.play_video import play_video

from plumber.pipeline import Pipeline

DATA_DIR = os.path.join(os.path.dirname(__file__), "vision_data")


if __name__ == "__main__":
    Pipeline([generate_positions, draw_frame, detect_circles, play_video], DATA_DIR).run()