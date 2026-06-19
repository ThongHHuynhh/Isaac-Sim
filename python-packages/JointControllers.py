from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
import numpy as np



robot = SingleArticulation(
    prim_path="/World/abb_irb1200_5_90/root_joint",
    name="abb"
)

robot.initialize()

print("DOF names:", robot.dof_names)
print("Joint positions:",np.rad2deg( robot.get_joint_positions()))


robot.apply_action(
    ArticulationAction(
        joint_positions=np.deg2rad([0, 0, 0, 0, 0, 0])
    )
)
