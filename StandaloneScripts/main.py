from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})


import omni
import omni.timeline
import carb
from isaacsim.core.utils.stage import open_stage
from isaacsim.core.api import World

#import python moduls
from TCP_Bridge import start_tcp_bridge, update_tcp_bridge, stop_tcp_bridge
from ProductSpawning import start_product_spawning
from ImageCapture2D import start_image_capture, update_image_capture, stop_image_capture

USD_PATH = "/home/zadmin/sandbox-isaac/USD/K2-CV-STEP-003.usd"
CAMERA_PATH = "/World/Inspector83x/rgb_camera"

#Open stage with isaac API, can be replace with Omniverse, check out StandaloneABB
# open_stage(USD_PATH)
print("[UINFO] Loading USD Stage...")
omni.usd.get_context().open_stage("/home/zadmin/sandbox-isaac/USD/K2-CV-STEP-003.usd")

for _ in range(10):
    simulation_app.update()

# STARTING PHYSICS (PRESS PLAY)
print("[UINFO] Starting physics (Press Play)")
omni.timeline.get_timeline_interface().play()
simulation_app.update()
print("[UINFO] Stage loaded.")

#starting TCP Bridge
start_tcp_bridge()
start_product_spawning()
start_image_capture(CAMERA_PATH)

while simulation_app.is_running():
    simulation_app.update()
    update_tcp_bridge()
    update_image_capture()

stop_image_capture()
stop_tcp_bridge()
simulation_app.close()
