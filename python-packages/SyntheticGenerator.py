import omni.replicator.core as rep
import omni.usd
from pxr import UsdGeom, Usd

CAMERA_PATH = "/World/Inspector83x/rgb_camera"
OUTPUT_DIR = "/home/zadmin/dough_dataset"
NUM_FRAMES = 1000

DOUGH_PATHS = [
    "/World/Products/Bagg_01/Sphere",
    "/World/Products/Bagg_01/Sphere_01",
    "/World/Products/Bagg_01/Sphere_02",
]

stage = omni.usd.get_context().get_stage()

def get_local_translation(path):
    prim = stage.GetPrimAtPath(path)
    xform = UsdGeom.Xformable(prim)

    for op in xform.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            v = op.Get(Usd.TimeCode.Default())
            return (float(v[0]), float(v[1]), float(v[2]))

    return (0.0, 0.0, 0.0)

original_local_pos = {
    path: get_local_translation(path)
    for path in DOUGH_PATHS
}

render_product = rep.create.render_product(
    CAMERA_PATH,
    resolution=(1200, 800)
)

writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir=OUTPUT_DIR,
    rgb=True,
    semantic_segmentation=True,
    bounding_box_2d_tight=True,
    distance_to_camera=True
)
writer.attach([render_product])

dough_material = rep.create.material_omnipbr(
    diffuse=rep.distribution.uniform(
        (0.55, 0.38, 0.18),
        (0.95, 0.78, 0.45)
    ),
    roughness=0.95
)

with rep.trigger.on_frame(num_frames=NUM_FRAMES):
    for path in DOUGH_PATHS:
        x, y, z = original_local_pos[path]
        dough = rep.get.prims(path_pattern=f"^{path}$")

        with dough:
            rep.modify.pose(
                position=rep.distribution.uniform(
                    (x - 0.02, y - 0.015, z),
                    (x + 0.02, y + 0.015, z)
                ),
                rotation=rep.distribution.uniform(
                    (0, 0,-5),
                    (0, 0,5)
                ),
                scale=rep.distribution.uniform(
                    (0.32,0.1,0.1),
                    (0.72, 0.1, 0.1)
                )
            )
            rep.randomizer.materials([dough_material])

rep.orchestrator.run()