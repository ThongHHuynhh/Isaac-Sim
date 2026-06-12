from pxr import UsdPhysics, PhysxSchema, Gf
import omni.usd

stage = omni.usd.get_context().get_stage()

belt_path = "/World/A_900023_INT_00_16_JUL_25_1/tn__A900023INT0016JUL251_lT8CFIMq0/Conveyor/Plane"
belt_prim = stage.GetPrimAtPath(belt_path)

if not belt_prim.IsValid():
    raise Exception(f"Prim not found: {belt_path}")

UsdPhysics.CollisionAPI.Apply(belt_prim)

mesh_collision = UsdPhysics.MeshCollisionAPI.Apply(belt_prim)
mesh_collision.CreateApproximationAttr("convexHull")

rigid_body = UsdPhysics.RigidBodyAPI.Apply(belt_prim)
rigid_body.CreateKinematicEnabledAttr(True)

surface_velocity = PhysxSchema.PhysxSurfaceVelocityAPI.Apply(belt_prim)
surface_velocity.CreateSurfaceVelocityAttr(Gf.Vec3f(0.2, 0.0, 0.0))  # +X, 0.5 m/s

print("Applied surface velocity to:", belt_path)