import asyncio
import numpy as np
import matplotlib.pyplot as plt
import omni.kit.app
from isaacsim.sensors.camera import Camera

CAMERA_PATH = "/World/Inspector83x/rgb_camera"

camera = Camera(
    prim_path=CAMERA_PATH,
    resolution=(640, 480),
    frequency=30,
)

camera.initialize()

async def capture_one_frame():
    for _ in range(60):
        await omni.kit.app.get_app().next_update_async()

    rgba = camera.get_rgba()

    if rgba is None or rgba.size == 0:
        print("No frame captured")
        return

    rgb = rgba[:, :, :3]

    if rgb.max() <= 1:
        rgb = rgb * 255

    rgb = rgb.astype(np.uint8)

    save_path = "/home/zadmin/camera_frame.png"
    plt.imsave(save_path, rgb)

    print("Saved camera frame to:", save_path)

asyncio.ensure_future(capture_one_frame())