import numpy as np
from isaacsim.sensors.camera import Camera
from omni.kit.viewport.utility import get_active_viewport


camera = None
latest_rgb = None


def start_image_capture(
    camera_path="/World/Inspector83x/rgb_camera",
    resolution=(640, 480),
    frequency=30,
):
    global camera

    camera = Camera(
        prim_path=camera_path,
        resolution=resolution,
        frequency=frequency,
    )
    camera.initialize()

    viewport = get_active_viewport()
    if viewport is not None:
        viewport.camera_path = camera_path
        print(f"[INFO] Viewport camera set to: {camera_path}")

    print(f"[INFO] Camera initialized: {camera_path}")


def update_image_capture():
    global latest_rgb

    if camera is None:
        return

    rgba = camera.get_rgba()

    if rgba is None or rgba.size == 0:
        return

    rgb = rgba[:, :, :3]

    if rgb.max() <= 1:
        rgb = rgb * 255

    rgb = rgb.astype(np.uint8)
    latest_rgb = rgb


def stop_image_capture():
    print("[INFO] Camera capture stopped")
