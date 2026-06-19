from pathlib import Path

from isaacsim import SimulationApp


simulation_app = SimulationApp({"headless": False})


import omni.timeline
import omni.usd

from camera_capture_window import CameraCaptureWindow


REPO_ROOT = Path(__file__).resolve().parents[1]
USD_PATH = REPO_ROOT / "USD" / "K2-CV-STEP-003.usd"
CAMERA_PATH = "/World/Inspector83x/rgb_camera"


def main():
    print("[INFO] Loading USD stage...")
    omni.usd.get_context().open_stage(str(USD_PATH))

    for _ in range(10):
        simulation_app.update()

    print("[INFO] Starting physics...")
    omni.timeline.get_timeline_interface().play()
    simulation_app.update()

    camera_view = CameraCaptureWindow(
        camera_path=CAMERA_PATH,
        resolution=(640, 480),
        frequency=30,
        window_title="Dummy Camera Capture",
    )
    camera_view.start()

    try:
        while simulation_app.is_running():
            simulation_app.update()

            # Replace this with PyTorch detections later.
            demo_boxes = [
                [100, 80, 260, 220, "demo"],
            ]

            frame = camera_view.update(boxes=demo_boxes)

            # frame is RGB uint8 with shape H x W x 3.
            # PyTorch hook:
            # tensor = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
            # tensor = tensor.unsqueeze(0).to(device)
    finally:
        camera_view.stop()
        simulation_app.close()


if __name__ == "__main__":
    main()
