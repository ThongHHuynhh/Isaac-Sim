import asyncio
import numpy as np
import omni.kit.app
import omni.ui as ui
from isaacsim.sensors.physx import _range_sensor

# ======================
# CONFIG
# ======================
SENSOR_PATH = "/World/BeamSensors/LightBeam_Sensor"

NUM_BEAMS = 1200
IMAGE_HEIGHT = 300

MIN_DEPTH = 0.0
MAX_DEPTH = 2.0

UI_UPDATE_EVERY = 1   # bigger = less lagS
DOWNSAMPLE_X = 2
DOWNSAMPLE_Y = 2

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 300

# ======================
# GLOBALS
# ======================
running = True
frame_id = 0

ls = _range_sensor.acquire_lightbeam_sensor_interface()
app = omni.kit.app.get_app()

depth_image = np.zeros((IMAGE_HEIGHT, NUM_BEAMS), dtype=np.float32)

provider = ui.ByteImageProvider()

window = ui.Window("Live LightBeam Stitched Image", width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT + 50)

with window.frame:
    with ui.VStack():
        ui.Label("1200-beam stitched depth stream")
        ui.ImageWithProvider(
            provider,
            width=DISPLAY_WIDTH,
            height=DISPLAY_HEIGHT,
        )


def depth_to_rgba(depth_img):
    img = np.nan_to_num(
        depth_img,
        nan=MAX_DEPTH,
        posinf=MAX_DEPTH,
        neginf=MIN_DEPTH,
    )

    img = (img - MIN_DEPTH) / (MAX_DEPTH - MIN_DEPTH)
    img = np.clip(img, 0.0, 1.0)

    gray = (img * 255).astype(np.uint8)

    rgba = np.empty((gray.shape[0], gray.shape[1], 4), dtype=np.uint8)
    rgba[:, :, 0] = gray
    rgba[:, :, 1] = gray
    rgba[:, :, 2] = gray
    rgba[:, :, 3] = 255

    return rgba


async def stream_lightbeam_to_ui():
    global depth_image, running, frame_id

    print("Streaming started.")
    print("Run this to stop:")
    print("running = False")

    while running:
        depth = ls.get_linear_depth_data(SENSOR_PATH)
        depth = np.asarray(depth, dtype=np.float32)

        if depth.shape[0] == NUM_BEAMS:
            depth_image[:-1, :] = depth_image[1:, :]
            depth_image[-1, :] = depth

        frame_id += 1

        if frame_id % UI_UPDATE_EVERY == 0:
            small = depth_image[::DOWNSAMPLE_Y, ::DOWNSAMPLE_X]
            rgba = depth_to_rgba(small)

            provider.set_bytes_data(
                rgba.ravel().tolist(),
                [small.shape[1], small.shape[0]],
            )

        await app.next_update_async()

    print("Streaming stopped.")


asyncio.ensure_future(stream_lightbeam_to_ui())