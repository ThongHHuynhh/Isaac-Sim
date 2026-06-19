import asyncio
from pxr import UsdGeom, Gf, Sdf
import omni.usd
import omni.timeline

PRODUCTS = [
    f"/World/Products/Bagg_0{i}"
    for i in range(1, 9)
]

SPAWN_POS = Gf.Vec3d(-3, 0, 0.95)
DELAY_SECONDS = 3.0

original_positions = {}

def get_stage():
    return omni.usd.get_context().get_stage()


def get_prim(stage, path):
    return stage.GetPrimAtPath(Sdf.Path(path))


def get_translate_op(xform):
    for op in xform.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            return op
    return xform.AddTranslateOp()


def save_original_positions():
    stage = get_stage()

    for path in PRODUCTS:
        prim = get_prim(stage, path)
        if prim.IsValid():
            xform = UsdGeom.Xformable(prim)
            op = get_translate_op(xform)
            original_positions[path] = op.Get()
            UsdGeom.Imageable(prim).MakeVisible()
        else:
            print("Missing:", path)


def reset_products():
    stage = get_stage()

    for path, pos in original_positions.items():
        prim = get_prim(stage, path)
        if prim.IsValid():
            xform = UsdGeom.Xformable(prim)
            op = get_translate_op(xform)
            op.Set(pos)
            UsdGeom.Imageable(prim).MakeVisible()
    print("Product reset to original pos")


async def release_products():
    stage = get_stage()
    timeline = omni.timeline.get_timeline_interface()

    save_original_positions()

    for path in PRODUCTS:
        if not timeline.is_playing():
            break

        prim = get_prim(stage, path)
        if not prim.IsValid():
            continue

        xform = UsdGeom.Xformable(prim)
        op = get_translate_op(xform)
        op.Set(SPAWN_POS)
        UsdGeom.Imageable(prim).MakeVisible()

        print("Released:", path)
        await asyncio.sleep(DELAY_SECONDS)

    while timeline.is_playing():
        await asyncio.sleep(0.2)

    reset_products()

def start_product_spawning():
    asyncio.ensure_future(release_products())
    print("[INFO] Product Spawning Started")
