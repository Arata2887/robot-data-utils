"""Small CSV adapter, provided so the exercise focuses on alignment."""

import csv
from pathlib import Path


def load_data(data_dir):
    streams = []
    for name in ("camera", "state", "action"):
        with (Path(data_dir) / (name + ".csv")).open(newline="", encoding="utf-8") as f:
            streams.append([
                {key: int(value) if key == "frame_id" else float(value)
                 for key, value in row.items()}
                for row in csv.DictReader(f)
            ])
    return tuple(streams)
