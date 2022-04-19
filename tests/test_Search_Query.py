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


def search(db, url_paths="", params={}):
    tables = getTables(db)
    table = getTable(db, tables=tables, table_name="mmf")

    # -- parse "params" and "filters" from HTTP request
    # params, filters = parseUrlPaths(url_paths, request.params, table["columns"])
    params, filters = parseUrlPaths(url_paths, params, table["columns"])

    # -- build "conditions" string and "values" array for "fetchRows()"
    conditions = " OR ".join([f'{param} LIKE ?' for param in params.keys()])
    values = ['%'+p+'%' for p in params.values()]
    if filters:
        conditions, values = parseFilters(filters, conditions, values)

    results = fetchRows(db, table="mmf", where=conditions, values=values)
    print(results)

if __name__ == "__main__":
    db = getDB()
    search(db, url_paths="title/elise")
