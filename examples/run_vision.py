import os
import time

from examples.vision.detect_circles import detect_circles
from examples.vision.draw_frame import draw_frame
from examples.vision.generate_positions import generate_positions
from examples.vision.play_video import play_video

from plumber.pipeline import Pipeline

DATA_DIR = os.path.join(os.path.dirname(__file__), "vision_data")


def main():
    pipeline = Pipeline([generate_positions, draw_frame, detect_circles, play_video], DATA_DIR)
    pipeline.start()

    try:
        while True:
            time.sleep(1)
            for name, actuator in pipeline.actuators.items():
                if not actuator.is_running():
                    print(f"warning: {name} is not running (exit code {actuator.returncode})")
    except KeyboardInterrupt:
        pass
    finally:
        for actuator in pipeline.actuators.values():
            actuator.stop()


if __name__ == "__main__":
    main()