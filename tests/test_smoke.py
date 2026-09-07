import json
import inspect
import math
from pathlib import Path

from data_io import load_data


def _data():
    return load_data(Path(__file__).resolve().parents[1] / "data")


def test_sample_loading():
    streams = _data()
    assert len(streams) == 3
    assert all(streams)


def test_pipeline_runs(align):
    rows = align(*_data())
    assert isinstance(rows, list)
    assert type(rows) is list
    assert rows
    for row in rows:
        assert set(row) == {"timestamp", "frame_id", "state", "action"}
        assert len(row["state"]) == 7
        assert row["action"] is None or len(row["action"]) == 7
        assert type(row) is dict
        assert type(row["timestamp"]) in (int, float) and math.isfinite(row["timestamp"])
        assert type(row["frame_id"]) is int
        assert type(row["state"]) is list
        assert row["action"] is None or type(row["action"]) is list
        values = row["state"] + ([] if row["action"] is None else row["action"])
        assert all(type(value) in (int, float) and math.isfinite(value) for value in values)
    json.dumps(rows, allow_nan=False)


def test_single_record(align):
    signature = inspect.signature(align)
    parameters = list(signature.parameters.values())
    assert [p.name for p in parameters] == ["camera", "state", "action", "target_hz", "camera_tolerance"]
    assert all(p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD for p in parameters)
    assert all(p.default is inspect.Parameter.empty for p in parameters[:3])
    assert parameters[3].default == 30 and parameters[4].default == 0.025
    camera = [{"timestamp": 0.0, "frame_id": 10}]
    state = [{"timestamp": 0.0, "x": 1, "y": 2, "z": 3, "qx": 0, "qy": 0, "qz": 0, "qw": 1}]
    action = [{"timestamp": 0.0, "dx": 1, "dy": 2, "dz": 3, "drx": 4, "dry": 5, "drz": 6, "gripper": 7}]
    assert align(camera, state, action) == [{"timestamp": 0.0, "frame_id": 10,
                                            "state": [1, 2, 3, 0, 0, 0, 1],
                                            "action": [1, 2, 3, 4, 5, 6, 7]}]


def test_repeatability(align):
    assert align(*_data()) == align(*_data())


def test_no_records(align):
    assert align([], [], []) == []
