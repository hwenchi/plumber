from plumber.decorator import valve
from examples.vision.shared import INITIAL_BALLS, step_ball


@valve(outlet="positions", throttle=0.03)
def generate_positions(_, reservoir):
    frame_id = reservoir.get("frame_id", 0)
    balls = [step_ball(b) for b in reservoir.get("balls", INITIAL_BALLS)]

    drop = {"frame_id": frame_id, "balls": balls}
    return [drop], {"frame_id": frame_id + 1, "balls": balls}
