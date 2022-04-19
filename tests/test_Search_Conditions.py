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


if __name__ == "__main__":
    db = getDB()
    params = {
        "title": "mary",
        "level1": "Level 1",
        "level2": "Level 2",
        "category1": "Nursery Rhyme",
    }

    query = {}
    if params.get("title"):
        query.update({"title LIKE ?": ["%" + params["title"] + "%"]})
    for term in {"level", "category"}:
        items = {k: v for k, v in params.items() if term in k}
        if items:
            key = " OR ".join([f"{term} = ?" for k in items.keys()])
            value = list(items.values())
            query.update({f"({key})": value})
    conditions = " AND ".join(query)
    values = list(chain(*query.values()))
    res = fetchRows(db, table="mmf", where=conditions, values=values)
    print(res)
