# 1. THIS MUST BE THE VERY FIRST THING IN YOUR SCRIPT
# It boots the Isaac Sim engine and opens the UI window.
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False}) # Set to True if you don't want a UI

# 2. Import standard libraries AFTER SimulationApp is initialized
import omni
import omni.timeline
import socket
import json
import threading
import numpy as np

# Import Isaac libraries
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction

# --- TCP SERVER SETUP (Unchanged) ---
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
        try:
            data = conn.recv(1024)
            if not data:
                break

            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                msg = json.loads(line)
                joints = np.array(msg["joints"], dtype=float)

                with lock:
                    latest_joints_deg = joints
        except Exception as e:
            print("TCP Error:", e)
            break

    conn.close()
    server.close()

# Start the background network thread
thread = threading.Thread(target=tcp_server, daemon=True)
thread.start()

# --- ISAAC SIM SETUP ---

# Note: In a real standalone app, you would load your USD stage here first
print("Loading USD Stage...")
omni.usd.get_context().open_stage("/home/zadmin/sandbox-isaac/USD/K2-CV-STEP-002.usd")

for _ in range(10):
    simulation_app.update()

# --- THE FIX: START PHYSICS (PRESS PLAY)
print("Starting physics timeline...")
omni.timeline.get_timeline_interface().play()
simulation_app.update()
print("Stage loaded. Initializing robot...")

robot = SingleArticulation(
    prim_path="/World/abb_irb1200_5_90/root_joint",
    name="abb"
)
robot.initialize()


print("Isaac Standalone running. Press Ctrl+C in terminal or close window to stop.")

# --- THE MAIN SIMULATION LOOP ---
# This replaces the omni.kit.app.get_update_event_stream() from the editor script.
while simulation_app.is_running():
    
    # 1. Step the simulation forward one frame
    simulation_app.update()

    # 2. Safely grab the latest network data
    with lock:
        joints = None if latest_joints_deg is None else latest_joints_deg.copy()

    # 3. Apply the movement to the virtual robot
    if joints is not None:
        robot.apply_action(
            ArticulationAction(
                joint_positions=np.deg2rad(joints)
            )
        )

# --- CLEANUP ---
# If the while loop breaks (e.g., you close the UI window), safely shut everything down.
running = False
simulation_app.close()