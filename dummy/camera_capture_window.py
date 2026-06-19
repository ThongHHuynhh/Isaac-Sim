import cv2
import numpy as np
import omni.ui as ui
from isaacsim.sensors.camera import Camera
from omni.kit.viewport.utility import get_active_viewport


class CameraCaptureWindow:
    def __init__(
        self,
        camera_path="/World/Inspector83x/rgb_camera",
        resolution=(640, 480),
        frequency=30,
        window_title="Live Isaac Camera",
    ):
        self.camera_path = camera_path
        self.resolution = resolution
        self.frequency = frequency
        self.window_title = window_title

        self.camera = None
        self.window = None
        self.provider = None
        self.latest_rgb = None

    def start(self):
        self.camera = Camera(
            prim_path=self.camera_path,
            resolution=self.resolution,
            frequency=self.frequency,
        )
        self.camera.initialize()

        viewport = get_active_viewport()
        if viewport is not None:
            viewport.camera_path = self.camera_path
            print(f"[INFO] Viewport camera set to: {self.camera_path}")

        width, height = self.resolution
        self.provider = ui.ByteImageProvider()
        self.window = ui.Window(self.window_title, width=width, height=height + 40)

        with self.window.frame:
            with ui.VStack():
                ui.Label(self.camera_path)
                ui.ImageWithProvider(
                    self.provider,
                    width=width,
                    height=height,
                )

        print(f"[INFO] Camera window started: {self.camera_path}")

    def update(self, boxes=None):
        if self.camera is None:
            return None

        rgba = self.camera.get_rgba()
        if rgba is None or rgba.size == 0:
            return None

        rgb = rgba[:, :, :3]
        if rgb.max() <= 1:
            rgb = rgb * 255

        rgb = rgb.astype(np.uint8)
        self.latest_rgb = rgb

        display_rgb = rgb.copy()
        if boxes:
            self._draw_boxes(display_rgb, boxes)

        self._show_rgb(display_rgb)
        return rgb

    def stop(self):
        print("[INFO] Camera window stopped")

    def _draw_boxes(self, rgb, boxes):
        for box in boxes:
            x1, y1, x2, y2 = box[:4]
            label = box[4] if len(box) > 4 else None

            cv2.rectangle(
                rgb,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                (0, 255, 0),
                2,
            )

            if label:
                cv2.putText(
                    rgb,
                    str(label),
                    (int(x1), max(0, int(y1) - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )

    def _show_rgb(self, rgb):
        if self.provider is None:
            return

        height, width, _ = rgb.shape

        rgba = np.empty((height, width, 4), dtype=np.uint8)
        rgba[:, :, :3] = rgb
        rgba[:, :, 3] = 255

        self.provider.set_bytes_data(
            rgba.ravel().tolist(),
            [width, height],
        )
