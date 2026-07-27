import os

FRAME_DIR = os.path.join(os.path.dirname(__file__), "frames")
WIDTH, HEIGHT = 480, 360
INITIAL_BALLS = [
    {"x": 80.0, "y": 60.0, "vx": 4.0, "vy": 3.0, "radius": 25, "color": (60, 180, 255)},
    {"x": 300.0, "y": 200.0, "vx": -3.0, "vy": 5.0, "radius": 35, "color": (80, 220, 120)},
    {"x": 200.0, "y": 300.0, "vx": 5.0, "vy": -4.0, "radius": 18, "color": (200, 100, 220)},
]


def step_ball(ball):
    x = ball["x"] + ball["vx"]
    y = ball["y"] + ball["vy"]
    vx, vy = ball["vx"], ball["vy"]
    if x - ball["radius"] < 0 or x + ball["radius"] > WIDTH:
        vx = -vx
        x = min(max(x, ball["radius"]), WIDTH - ball["radius"])
    if y - ball["radius"] < 0 or y + ball["radius"] > HEIGHT:
        vy = -vy
        y = min(max(y, ball["radius"]), HEIGHT - ball["radius"])
    return {**ball, "x": x, "y": y, "vx": vx, "vy": vy}