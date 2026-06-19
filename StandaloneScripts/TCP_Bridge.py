import socket
import json
import threading
import numpy as np

from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
import omni.kit.app



latest_joints_deg = None
lock = threading.Lock()
running = False
robot = None
thread = None


#Isacc sim updates
smoothed_joints_rad = None
alpha = 0.18

def start_tcp_bridge():
    global running, robot, thread
    robot = SingleArticulation(
        prim_path="/World/abb_irb1200_5_90/root_joint",
        name="abb"
    )
    robot.initialize()
    running = True
    thread = threading.Thread(target=tcp_server, daemon=True)
    thread.start()

    print("[INFO] TCP bridge started")
    

def tcp_server():
    global latest_joints_deg, running

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 5000))
    server.listen(1)

    print("[UINFO] Waiting for RobotStudio bridge...")
    conn, addr = server.accept()
    # Apply specifically for TCP, TCP_NODELAY = 1 -> send directly, dont wait
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,1)
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
                print("[ERROR] JSON error:", e)

    conn.close()
    server.close()



def update_tcp_bridge():
    global latest_joints_deg, smoothed_joints_rad

    with lock:
        joints = None if latest_joints_deg is None else latest_joints_deg.copy()

    if joints is None:
        return
    
    target_rad = np.deg2rad(joints)
    if smoothed_joints_rad is None:
        smoothed_joints_rad = target_rad.copy()
    else: 
        smoothed_joints_rad = (smoothed_joints_rad + alpha * (target_rad - smoothed_joints_rad))

    if joints is not None:
        robot.apply_action(
            ArticulationAction(
                joint_positions=smoothed_joints_rad
            )
        )

def stop_tcp_bridge():
    global running
    running = False
    print("[UINFO] TCP bridge stopped")
