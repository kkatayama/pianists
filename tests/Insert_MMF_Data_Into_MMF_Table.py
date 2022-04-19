# coding: utf-8
from pathlib import Path
import sys

sys.path.append(str(Path(".").absolute().parent))

from db_functions import *
from rich import print
import sqlite3
import json


def getDB():
    db_file = Path().cwd().parent.joinpath("pianists.db").__str__()
    db = sqlite3.connect(db_file)
    db.text_factory = str
    db.row_factory = sqlite3.Row
    return db


def createTable(db, table, params):
    params, columns = mapUrlPaths("", params, table)
    res = addTable(db, table=table, columns=columns)
    res.update({"table": table})
    print(res)


def add(db, table, columns, col_values):
    col_id = insertRow(db, table=table, columns=columns, col_values=col_values)
    print({"col_id": col_id, "columns": columns, "col_values": col_values})
    db.commit()


if __name__ == "__main__":
    db = getDB()
    json_file = (
        Path().cwd().parent.joinpath("making_music_fun", "sheet_music_files.json")
    )
    with open(json_file) as f:
        mmf_data = json.load(f)

    # -- create table
    print("CREATE TABLE:")
    params = {
        "entry_id": "INTEGER",
        "title": "TEXT",
        "url": "TEXT",
        "category": "TEXT",
        "level": "INTEGER",
        "pdf_file": "TEXT",
        "pdf_url": "TEXT",
        "entry_time": "DATETIME",
    }
    createTable(db, table="mmf", params=params)

    # -- insert data to tables:
    print("INSERT DATA:")
    for item in mmf_data:
        required = ["title", "url", "category", "level", "pdf_file", "pdf_url"]
        entry = {k: item[k] for k in required}
        columns, col_values = list(entry.keys()), list(entry.values())
        add(db, table="mmf", columns=columns, col_values=col_values)
