# coding: utf-8
import sqlite3


def fetchRows(**kwargs):
    table = kwargs.get("table")
    columns = "*" if not kwargs.get("columns") else ",".join(kwargs["columns"])
    condition = "TRUE" if not kwargs.get("condition") else f'({kwargs["condition"]})'
    values = kwargs.get("values")

    query = f"SELECT {columns} FROM {table} WHERE {condition};"
    print(query)

    db = sqlite3.connect("m2band.db")
    db.text_factory = str
    db.row_factory = sqlite3.Row
    with db:
        cur = db.cursor()
        if values:
            rows = cur.execute(query, values).fetchall()
        else:
            rows = cur.execute(query).fetchall()
    if rows:
        return [dict(row) for row in rows]
    return False


params = {
    "table": "users",
    "columns": ["user_id", "username", "create_time"],
    "condition": "username=?",
    "values": ["user_1"],
}
row = fetchRows(**params)
print(row)

params = {"table": "users"}
rows = fetchRows(**params)
print(rows)
