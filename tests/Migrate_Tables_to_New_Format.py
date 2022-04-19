# coding: utf-8
# %load Migrate_Tables_to_New_Format.py
# %load Migrate_Tables_to_New_Format.py
from pathlib import Path
import sys

sys.path.append(str(Path(".").absolute().parent))

from rich import print
from db_functions import *
import sqlite3


def get(db, table):
    return fetchRows(db, table=table)


def add(db, table, columns, col_values):
    col_id = insertRow(db, table=table, columns=columns, col_values=col_values)
    print({"col_id": col_id, "columns": columns, "col_values": col_values})


def createTable(db, table, url_paths):
    params, columns = mapUrlPaths(url_paths, {}, table)
    res = addTable(db, table=table, columns=columns)
    res.update({"table": table})
    print(res)


def dropTable(db, table):
    res = deleteTable(db, table=table)
    res.update({"table": table})
    print(res)


if __name__ == "__main__":
    db = sqlite3.connect("../pianists.db")
    db.text_factory = str
    db.row_factory = sqlite3.Row

    # -- store existing table data
    # users = get(db, table="users")
    files = get(db, table="files")
    print("EXISTING TABLES:")
    # print(f'"users" = {users}')
    print(f'"files" = {files}')
    print()

    # -- delete existing tables
    print("DELETE TABLES:")
    # dropTable(db, table="users")
    dropTable(db, table="files")
    print()

    # -- create tables
    print("CREATE TABLES:")
    # createTable(
    #    db,
    #    table="users",
    #    url_paths="user_id/INTEGER/username/TEXT/password/TEXT/create_time/DATETIME",
    # )
    createTable(
        db,
        table="files",
        url_paths="entry_id/INTEGER/user_id/INTEGER/title/TEXT/level/TEXT/category/TEXT/file_name/TEXT/entry_time/DATETIME",
    )
    print()

    # -- insert data to tables:
    print("INSERT DATA:")
    # for user in users:
    #    required = ["username", "password"]
    #    entry = {k: user[k] for k in required}
    #    columns, col_values = list(entry.keys()), list(entry.values())
    #    add(db, table="users", columns=columns, col_values=col_values)
    for file in files:
        required = ["user_id", "title", "file_name"]
        entry = {k: file[k] for k in required}
        columns, col_values = list(entry.keys()), list(entry.values())
        add(db, table="files", columns=columns, col_values=col_values)
    db.commit()
