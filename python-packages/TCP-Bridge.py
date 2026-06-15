import socket
import json
import threading
import numpy as np

from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
import omni.kit.app

robot = SingleArticulation(
    prim_path="/World/abb_irb1200_5_90/root_joint",
    name="abb"
)
robot.initialize()

latest_joints_deg = None
lock = threading.Lock()
running = True

def tcp_server():
    global latest_joints_deg, running

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 5000))
    server.listen(1)

    print("Waiting for RobotStudio bridge...")
    conn, addr = server.accept()
    print("Connected:", addr)

    buffer = ""

    while running:
        data = conn.recv(1024)
        if not data:
            break

        buffer += data.decode()

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)

            try:
                msg = json.loads(line)
                joints = np.array(msg["joints"], dtype=float)

                with lock:
                    latest_joints_deg = joints

            except Exception as e:
                print("JSON error:", e)

    conn.close()
    server.close()

def on_update(e):
    global latest_joints_deg

    with lock:
        joints = None if latest_joints_deg is None else latest_joints_deg.copy()

    if joints is not None:
        robot.apply_action(
            ArticulationAction(
                joint_positions=np.deg2rad(joints)
            )
        )

thread = threading.Thread(target=tcp_server, daemon=True)
thread.start()

sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
    on_update,
    name="robotstudio_to_isaac_joint_stream"
)

print("Isaac TCP listener running.")