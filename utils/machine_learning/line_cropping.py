#!/usr/bin/env python3
from pathlib import Path
import argparse
import cv2


def extractBar(img_file_1, img_file_2):
    images = {
        img_file_1: [
            [840, 990, 930, 2560],
            [1070, 1190, 930, 2560],
            [1330, 1480, 800, 2560],
            [1560, 1680, 800, 2560],
            [1810, 1970, 800, 2560],
        ],
        img_file_2: [
            [1125, 1255, 800, 2560],
            [1385, 1545, 800, 2560],
            [1600, 1730, 800, 2560],
        ]
    }

    for img, coords in images.items():
        for i, coord in enumerate(coords):
            image = cv2.imread(img)
            cropped = image[coord[0]:coord[1], coord[2]:coord[3]]
            name = f'line_crop/{Path(img).stem}_{i}.png'
            cv2.imwrite(name, cropped)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("img1")
    ap.add_argument("img2")
    args = ap.parse_args()

    extractBar(args.img1, args.img2)
