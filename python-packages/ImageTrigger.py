import numpy as np
import cv2
import time
import os

# =========================
# CONFIG
# =========================

PHOTOEYE_PATH = "/World/Photoeye/LightBeam_Sensor"
TOP_SCANNER_PATH = "/World/BeamSensors/LightBeam_Sensor"

NUM_TOP_RAYS = 1200

CONVEYOR_SPEED_M_S = 0.10      # change to your conveyor speed
PHOTOEYE_TO_SCANNER_M = 0.20   # distance from photoeye to top scanner

BEAM_CLEAR_DISTANCE = 0.80     # distance when beam is not blocked
PHOTOEYE_THRESHOLD = 0.03      # trigger if depth changes by this much

START_CONFIRM_FRAMES = 3
STOP_CONFIRM_FRAMES = 5

SAVE_FOLDER = "/home/zadmin/sandbox-isaac/temp"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# =========================
# SENSOR READ FUNCTIONS
# =========================

def read_photoeye_depth():
    """
    Replace this with your real photoeye/light beam read.
    It should return one float depth value.
    Example return:
        0.8 = clear
        0.3 = blocked by product
    """
    depths = read_light_beam_depths(PHOTOEYE_PATH)

    if depths is None or len(depths) == 0:
        return BEAM_CLEAR_DISTANCE

    depths = np.array(depths, dtype=np.float32)
    valid = np.isfinite(depths)

    if not np.any(valid):
        return BEAM_CLEAR_DISTANCE

    return float(np.min(depths[valid]))


def read_top_scanner_depths():
    """
    Replace this with your real top line scanner read.
    Must return array shape: (1200,)
    """
    depths = read_light_beam_depths(TOP_SCANNER_PATH)

    if depths is None:
        return None

    depths = np.array(depths, dtype=np.float32)

    if depths.shape[0] != NUM_TOP_RAYS:
        print("Wrong top scanner ray count:", depths.shape)
        return None

    depths[~np.isfinite(depths)] = 0.0

    return depths


def read_light_beam_depths(sensor_path):
    """
    This is the only function you may need to adapt depending on
    how your Isaac light beam sensor exposes data.

    Put your working sensor read code here.
    It should return the depth array from that sensor.
    """

    # Example placeholder:
    # return my_sensor_dict[sensor_path].data.depths

    raise NotImplementedError(
        "Put your Isaac Sim light beam / raycast depth reading code here."
    )


# =========================
# MAIN SCANNER LOGIC
# =========================

class ProductDepthScanner:
    def __init__(self):
        self.capturing = False
        self.armed_start = False
        self.armed_stop = False

        self.depth_rows = []

        self.blocked_count = 0
        self.clear_count = 0

        self.start_time = None
        self.stop_time = None

        self.delay_time = PHOTOEYE_TO_SCANNER_M / CONVEYOR_SPEED_M_S

        self.product_index = 0

    def update(self):
        now = time.time()

        photoeye_depth = read_photoeye_depth()

        beam_blocked = abs(photoeye_depth - BEAM_CLEAR_DISTANCE) > PHOTOEYE_THRESHOLD

        if beam_blocked:
            self.blocked_count += 1
            self.clear_count = 0
        else:
            self.clear_count += 1
            self.blocked_count = 0

        # Leading edge detected
        if not self.capturing and not self.armed_start:
            if self.blocked_count >= START_CONFIRM_FRAMES:
                self.start_time = now + self.delay_time
                self.armed_start = True
                print("Photoeye triggered. Scanner will start after delay.")

        # Start scanner after travel delay
        if self.armed_start and now >= self.start_time:
            self.capturing = True
            self.armed_start = False
            self.depth_rows = []
            print("Started top scanner capture.")

        # Capture top scanner line
        if self.capturing:
            top_depths = read_top_scanner_depths()

            if top_depths is not None:
                self.depth_rows.append(top_depths)

        # Trailing edge detected
        if self.capturing and not self.armed_stop:
            if self.clear_count >= STOP_CONFIRM_FRAMES:
                self.stop_time = now + self.delay_time
                self.armed_stop = True
                print("Photoeye clear. Scanner will stop after delay.")
        # Stop scanner after trailing edge reaches scanner
        if self.armed_stop and now >= self.stop_time:
            self.capturing = False
            self.armed_stop = False

            print("Stopped capture.")
            self.save_depth_map()

    def save_depth_map(self):
        if len(self.depth_rows) == 0:
            print("No depth rows captured.")
            return

        depth_map = np.stack(self.depth_rows, axis=0)

        npy_path = os.path.join(
            SAVE_FOLDER,
            f"product_{self.product_index:03d}_depth.npy"
        )

        png_path = os.path.join(
            SAVE_FOLDER,
            f"product_{self.product_index:03d}_depth.png"
        )

        np.save(npy_path, depth_map)

        depth_vis = cv2.normalize(
            depth_map,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        cv2.imwrite(png_path, depth_vis)

        print("Saved raw depth:", npy_path)
        print("Saved image:", png_path)
        print("Depth map shape:", depth_map.shape)

        self.product_index += 1
        self.depth_rows = []


# =========================
# RUN LOOP
# =========================

scanner = ProductDepthScanner()

print("Depth scanner running.")
print("Move product through photoeye and scanner.")

while True:
    scanner.update()
    time.sleep(0.01)