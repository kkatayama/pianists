#!/usr/bin/env python3
from pathlib import Path
# import pandas as pd
import argparse
import muspy
import json


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

    # data = music.to_ordered_dict()
    music = muspy.read_musicxml(str(MXL_FILE), resolution=1)
    data = json.loads(json.dumps(music.to_ordered_dict()))

    # -- split notes by treble and bass clef
    treble = list(filter(lambda x: x["pitch"] >= 60, data["tracks"][0]["notes"]))
    bass = list(filter(lambda x: x["pitch"] < 60, data["tracks"][0]["notes"]))

    # -- generate p_code -- #
    key_map = {32: 1, 16: 1, 12: 1.33, 8: 2, 6: 2.66, 4: 4, 3: 5.33, 2: 8, 1: 16}
    qpm = data["tempos"][0]["qpm"] if data.get("tempos") else 100
    num = data["time_signatures"][0]["numerator"] if data.get("time_signatures") else 4
    den = data["time_signatures"][0]["denominator"] if data.get("time_signatures") else 4
    p_code_treble = ["R", f"{int(qpm)}", f"{num}/{den}"]

    # -- format each note -- #
    for note in treble:
        key = note["pitch_str"].replace("#", "S")
        if "b" in key:
            key = key.replace(key[0], chr(ord(key[0]) - 1)).replace("b", "S")
        rate = key_map[note["duration"]]
        p_code_treble.append(f"{rate}/{key}")

    # -- export p-code --#
    with open("music.txt", "w") as f:
        f.write(" ".join(p_code_treble) + "\n")
    print(p_code_treble)

    # df = pd.DataFrame([dict(i) for i in data["tracks"][0]["notes"]])
    # df.to_csv(f'{BASE_PATH.joinpath(MXL_FILE.stem)}.csv', index=False)
    # print(df)

    with open(f'{BASE_PATH.joinpath(MXL_FILE.stem)}.json', 'w') as f:
        music.save_json(f)

