import socket
import struct
import threading
import time
import numpy as np

import omni.kit.app
from isaacsim.sensors.physx import _range_sensor

# ---------------- CONFIG ----------------

SENSOR_PATH = "/World/Photoeye/LightBeam_Sensor"

DEVICE_PORT = 56100        # fake TDS2000 listens here
SEND_RATE_HZ = 50          # match your scanner/composition trigger rate
SEND_ALL_RAYS = False      # False = only hit points, True = send all rays

# Convert Isaac units to TDS units
M_TO_MM = 1000.0

# If hit_pos is not reliable, use depth as Y
USE_HIT_POSITION = True

# ----------------------------------------

ls = _range_sensor.acquire_lightbeam_sensor_interface()

clients = set()
clients_lock = threading.Lock()

scan_count = 0
latest_packet = None
running = True


def build_realtime_header(scan_count):
    """
    TDS RealTimeHeader = 32 bytes.
    TimestampHigh, TimestampLow, EncoderCount, Stat1, Stat2,
    ExposureTime, XyDataType, SceneId, Reserved1, Reserved2
    """
    timestamp_ns = time.time_ns()
    ts_high = (timestamp_ns >> 32) & 0xFFFFFFFF
    ts_low = timestamp_ns & 0xFFFFFFFF

    encoder_count = scan_count
    stat1 = 0
    stat2 = 0
    exposure_time_us = 1000
    xy_data_type = 0x00   # XY little endian
    scene_id = 0
    reserved1 = 0
    reserved2 = 0

    return struct.pack(
        "<IIIIIHBBII",
        ts_high,
        ts_low,
        encoder_count,
        stat1,
        stat2,
        exposure_time_us,
        xy_data_type,
        scene_id,
        reserved1,
        reserved2,
    )


def build_xy_packet(depths, hit_pos, hits):
    """
    Rsp56100 Table 3:
    ScanTriggerCount 4
    Reserved 2
    PayloadType 2 = 0x0001
    RealTimeHeader 32
    Reserved 6
    NumPoints 2
    XY points: float32 X, float32 Y in mm
    """
    global scan_count

    scan_count += 1
    points = []

    depths = np.asarray(depths)
    hits = np.asarray(hits).astype(bool)

    if hit_pos is not None:
        hit_pos = np.asarray(hit_pos)

    for i in range(len(depths)):
        if not SEND_ALL_RAYS and not hits[i]:
            continue

        if USE_HIT_POSITION and hit_pos is not None and len(hit_pos) > i:
            # Isaac position is usually meters
            x_mm = float(hit_pos[i][0]) * M_TO_MM
            y_mm = float(hit_pos[i][2]) * M_TO_MM
        else:
            # fallback: use ray index as X, depth as Y
            x_mm = float(i)
            y_mm = float(depths[i]) * M_TO_MM

        points.append((x_mm, y_mm))

    num_points = len(points)

    header = struct.pack(
        "<IHH",
        scan_count,
        0,
        0x0001,
    )

    rth = build_realtime_header(scan_count)

    packet = header
    packet += rth
    packet += b"\x00" * 6
    packet += struct.pack("<H", num_points)

    for x_mm, y_mm in points:
        packet += struct.pack("<ff", x_mm, y_mm)

    return packet


def make_session_response(status, client_ip):
    """
    Rsp56100 session response = 26 bytes.
    Status, MaxSessions, Reserved, Session1_IP, Session2_IP, Reserved
    """
    max_sessions = 2
    session1_ip = socket.inet_aton(client_ip)
    session2_ip = b"\x00\x00\x00\x00"

    return (
        struct.pack("<BBH", status, max_sessions, 0)
        + session1_ip
        + session2_ip
        + b"\x00" * 14
    )


def udp_session_server():
    """
    Receives Req56100:
    byte 0 = FlowSwitch
      0 = disable
      1 = enable
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", DEVICE_PORT))
    sock.settimeout(0.2)

    print(f"Fake TDS2000 UDP56100 listening on port {DEVICE_PORT}")

    while running:
        try:
            data, addr = sock.recvfrom(2048)
        except socket.timeout:
            continue
        except Exception as e:
            print("UDP server error:", e)
            break

        if len(data) < 1:
            continue

        flow_switch = data[0]
        client_ip, client_port = addr

        if flow_switch == 1:
            with clients_lock:
                clients.add(addr)

            rsp = make_session_response(0x00, client_ip)
            sock.sendto(rsp, addr)
            print("Session enabled:", addr)

        elif flow_switch == 0:
            with clients_lock:
                clients.discard(addr)

            rsp = make_session_response(0x01, client_ip)
            sock.sendto(rsp, addr)
            print("Session disabled:", addr)

    sock.close()


def udp_stream_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    period = 1.0 / SEND_RATE_HZ
    last_send = 0

    while running:
        now = time.time()

        if now - last_send >= period:
            last_send = now

            with clients_lock:
                targets = list(clients)

            if latest_packet is not None:
                for addr in targets:
                    try:
                        sock.sendto(latest_packet, addr)
                    except Exception as e:
                        print("Send error:", e)

        time.sleep(0.001)

    sock.close()


def on_update(event):
    global latest_packet

    try:
        depths = ls.get_linear_depth_data(SENSOR_PATH)
        hit_pos = ls.get_hit_pos_data(SENSOR_PATH)
        hits = ls.get_beam_hit_data(SENSOR_PATH).astype(bool)

        latest_packet = build_xy_packet(depths, hit_pos, hits)

    except Exception as e:
        print("Lightbeam read error:", e)


# Stop old callback if re-running
try:
    lightbeam_tds_sub.unsubscribe()
except Exception:
    pass

# Start UDP threads once
try:
    running = False
    time.sleep(0.1)
except Exception:
    pass

running = True

threading.Thread(target=udp_session_server, daemon=True).start()
threading.Thread(target=udp_stream_sender, daemon=True).start()

lightbeam_tds_sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
    on_update,
    name="FakeTDS2000LightBeam"
)

print("Fake TDS2000 lightbeam started.")
print("Your system should send Req56100 FlowSwitch=1 to Isaac IP, port 56100.")
print("To stop, run: stop_fake_tds()")


def stop_fake_tds():
    global running
    running = False
    try:
        lightbeam_tds_sub.unsubscribe()
    except Exception:
        pass
    print("Fake TDS2000 stopped.")