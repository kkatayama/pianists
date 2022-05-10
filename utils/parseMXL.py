#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import argparse
import muspy


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("mxl", help="the musicmxl file to parse")
    ap.add_argument("base_path", help="the base folder to export the csv and json file")
    args = ap.parse_args()

    # -- GLOBALS -- #
    MXL_FILE = Path(args.mxl)
    BASE_PATH = Path.cwd()
    if args.base_path:
        BASE_PATH = Path(args.base_path)

    music = muspy.read_musicxml(str(MXL_FILE))
    data = music.to_ordered_dict()

    df = pd.DataFrame([dict(i) for i in data["tracks"][0]["notes"]])
    df.to_csv(f'{BASE_PATH.joinpath(MXL_FILE.stem)}.csv', index=False)

    with open(f'{BASE_PATH.joinpath(MXL_FILE.stem)}.json', 'w') as f:
        music.save_json(f)

    print(df)
