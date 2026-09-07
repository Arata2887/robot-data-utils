"""Run the candidate implementation on the bundled synthetic CSV data."""

import argparse
import json
from pathlib import Path

from alignment import align_trajectory
from data_io import load_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument("--output", type=Path, default=Path("trajectory.json"))
    args = parser.parse_args()
    rows = align_trajectory(*load_data(args.data_dir))
    args.output.write_text(json.dumps(rows, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Wrote {} aligned rows to {}".format(len(rows), args.output))


if __name__ == "__main__":
    main()
