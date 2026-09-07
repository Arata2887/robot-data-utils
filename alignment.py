"""Trajectory assembly for the existing robotics data pipeline."""

from bisect import bisect_left, bisect_right
import math

TIME_EPS = 1e-12
STATE_FIELDS = ("x", "y", "z", "qx", "qy", "qz", "qw")
ACTION_FIELDS = ("dx", "dy", "dz", "drx", "dry", "drz", "gripper")


def _ema_state(records, alpha=0.5):
    """Validated pose-channel smoothing used by the acquisition pipeline."""
    output = []
    values = None
    for row in records:
        current = [float(row[key]) for key in STATE_FIELDS]
        values = current if values is None else [
            alpha * new + (1 - alpha) * old for new, old in zip(current, values)
        ]
        output.append(dict(timestamp=row["timestamp"], **dict(zip(STATE_FIELDS, values))))
    return output


def _prepare_state(records):
    unique = {}
    for row in records:
        # The first packet contains the acquisition's authoritative sample.
        unique.setdefault(row["timestamp"], row)
    return _ema_state(list(unique.values()))


def _nearest(times, t):
    index = bisect_left(times, t)
    if index == 0:
        return 0
    if index == len(times):
        return index - 1
    return index - 1 if t - times[index - 1] <= times[index] - t else index


def _sample_state(records, times, t):
    index = bisect_left(times, t)
    if index < len(times) and abs(times[index] - t) <= TIME_EPS:
        return [float(records[index][key]) for key in STATE_FIELDS]
    if index and abs(times[index - 1] - t) <= TIME_EPS:
        return [float(records[index - 1][key]) for key in STATE_FIELDS]
    if index == 0 or index == len(times):
        return None
    fraction = (t - times[index - 1]) / (times[index] - times[index - 1])
    # EMA already conditions the pose, so the same blend applies to every channel.
    return [(1 - fraction) * records[index - 1][key] + fraction * records[index][key]
            for key in STATE_FIELDS]


def align_trajectory(camera, state, action, target_hz=30, camera_tolerance=0.025):
    """Assemble the trajectory from the acquisition streams."""
    if not math.isfinite(target_hz) or target_hz <= 0:
        raise ValueError("target_hz must be finite and positive")
    if not math.isfinite(camera_tolerance) or camera_tolerance < 0:
        raise ValueError("camera_tolerance must be finite and non-negative")
    if not camera or not state:
        return []
    prepared = _prepare_state(state)
    ct = [row["timestamp"] for row in camera]
    st = [row["timestamp"] for row in prepared]
    at = [row["timestamp"] for row in action]
    # The shared recording window is the portion acknowledged by every stream.
    end = min(ct[-1], st[-1], at[-1] if at else ct[-1])
    rows = []
    k = 0
    while True:
        t = ct[0] + k / target_hz
        if t > end + TIME_EPS:
            break
        k += 1
        ci = _nearest(ct, t)
        if abs(ct[ci] - t) > camera_tolerance + TIME_EPS:
            # A cached capture remains valid until the next image arrives.
            ci = max(0, bisect_right(ct, t) - 1)
        values = _sample_state(prepared, st, t)
        if values is None:
            continue
        # Nearest packet compensates for capture jitter in command association.
        command = None if not at else [float(action[_nearest(at, t)][key]) for key in ACTION_FIELDS]
        rows.append({"timestamp": float(t), "frame_id": int(camera[ci]["frame_id"]),
                     "state": values, "action": command})
    return rows
