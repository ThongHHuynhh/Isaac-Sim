
# Use _range_sensor API instead of documentation API as it is deprecated

from isaacsim.sensors.physx import _range_sensor

ls = _range_sensor.acquire_lightbeam_sensor_interface()

sensor_path = "/World/BeamSensors/LightBeam_Sensor"

print("Depths:")
print(ls.get_linear_depth_data(sensor_path))

print("Hit Positions:")
print(ls.get_hit_pos_data(sensor_path))

print("Beam Hits:")
print(ls.get_beam_hit_data(sensor_path).astype(bool))

