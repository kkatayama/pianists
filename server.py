from bottle import request, response, run, template, static_file, redirect
from bottle_sqlite import SQLitePlugin, sqlite3
# from bottle_errorsrest import ErrorsRestPlugin
from utils.db_functions import (
    insertRow, fetchRow, fetchRows, deleteRow,
    securePassword, checkPassword, git_update,
    getLevels, getCategories, clean, parseParams, genToken,
    checkUserAgent, log_to_logger, ErrorsRestPlugin
)
from utils.secret import secret_key

from itertools import chain
from datetime import datetime
from pathlib import Path
# from hashlib import sha256
# from rich import print
# from rich.traceback import install
# from rich import print, inspect, print_json, pretty
import bottle
import shutil
import json
import sys
import os

# pretty.install()

# app = Bottle()
app = bottle.app()
plugin = SQLitePlugin(dbfile="db/pianists.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
app.install(plugin)
app.install(log_to_logger)
app.install(ErrorsRestPlugin())


@app.hook("before_request")
def getParams():
    parseParams(secret_key)

@app.route("/commands", method=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def commands():
    with open('docs/all_commands.json') as f:
        res = json.load(f)
    return res


@app.route("/test", method=["GET", "POST"])
def test():
    # parseParams(secret_key)
    res = {"PARAMS": request.params, "JSON": request.json, "COOKIES": request.cookies}
    return clean(res)

###############################################################################
#                            Users Table Functions                            #
###############################################################################
@app.route("/", method="GET")
@app.route("/login", method=["GET"])
def index():
    if request.params.get('webapp'):
        return template("static/templates/index.tpl")
    return clean({"message": "index/login", "request": request.url})

@app.route("/login", method="POST")
def login(db):
    try:
        username = request.params["username"]
        password = request.params["password"]
    except KeyError:
        res = {"message": "missing paramater", "required params": ["username", "password"]}
        if request.params.get('webapp'):
            return template("static/templates/index.tpl", res=res)
        return clean(res)

    # -- check if user exists
    row = fetchRow(db, table="users", where="username=?", values=username)
    if not row:
        res = {"message": "user does not exist", "username": username}
        if request.params.get('webapp'):
            return template("static/templates/index.tpl", res=res)
        return clean(res)

    # -- check user supplied password (previous row statement has user data for username=[username])
    if not checkPassword(password, row["password"]):
        # -- checkPassword() returned False
        res = {"message": "incorrect password", "password": password}
        if request.params.get('webapp'):
            return template("static/templates/index.tpl", res=res)
        return clean(res)

    # -- made it here: means username exists and checkPassword() returned True
    response.set_cookie("user_id", str(row["user_id"]), secret=secret_key)
    res = {"message": "user login success", "user_id": row["user_id"], "username": row["username"]}
    res.update({"token": genToken("user_id", str(row["user_id"]), secret_key)})
    if request.params.get('webapp'):
        return template("static/templates/delay.tpl", res=res, location="/dashboard")
    return clean(res)

@app.route("/register", method="GET")
def register():
    print("registration page")
    return template("static/templates/register.tpl")

@app.route("/createUser", method="POST")
def createUser(db):
    try:
        username = request.params["username"]
        plaintext = request.params["password"]
        password2 = request.params["password2"]
    except KeyError:
        res = {"message": "missing paramater", "required params": ["username", "password", "password2"]}
        if request.params.get('webapp'):
            return template("static/templates/register.tpl", res=res)
        return clean(res)

    if plaintext != password2:
        res = {"message": "passwords do not match", "password1": plaintext, "password2": password2}
        if request.params.get('webapp'):
            return template("static/templates/register.tpl", res=res)
        return clean(res)

    # -- check if user exists
    row = fetchRow(db, table="users", where="username=?", values=username)
    if row:
        res = {"message": "user exists", "username": row["username"]}
        if request.params.get('webapp'):
            return template("static/templates/register.tpl", res=res)
        return clean(res)

    # -- if user doesn't exist, create user
    password = securePassword(plaintext)
    user_id = insertRow(db, table="users", columns=["username", "password"], col_values=[username, password])
    res = {"message": "user created", "user_id": user_id, "username": username}
    res.update({"token": genToken("user_id", str(user_id), secret_key)})

    git_update()
    if request.params.get('webapp'):
        return template("static/templates/index.tpl", res=res)
    return clean(res)

@app.route('/logout', method="GET")
def logout():
    res = {"message": "user logged out"}
    if request.params.get('webapp'):
        response.delete_cookie('user_id')
        redirect('/')
    return clean(res)

@app.route('/dashboard', method="GET")
def dashboard(db):
    user_id = request.get_cookie("user_id", secret=secret_key)
    if not user_id:
        redirect('/')

    rows = fetchRows(db, table="files", where="user_id=?", values=user_id)
    if request.params.get("webapp"):
        if rows:
            return template("static/templates/dashboard.tpl", rows=rows)
        return template("static/templates/dashboard.tpl")
    return clean({"message": "user_dashboard", "files": rows})
###############################################################################
#                            files Table Functions                            #
###############################################################################
@app.route("/deleteFile", method="POST")
def deleteFile(db):
    user_id = request.get_cookie("user_id", secret=secret_key)
    if not user_id:
        redirect('/')

    entry_id = str(request.params.get("entry_id"))
    row = fetchRow(db, table="files", where="user_id=? AND entry_id=?", values=[user_id, entry_id])
    if not row:
        res = {"message": "no file with matching 'entry_id' and 'user_id'", "user_id": user_id, "entry_id": entry_id}
        if request.params.get("webapp"):
            return template("static/templates/delay.tpl", res=res, location="/dashboard")
        return clean(res)

    # -- file found and belongs to user
    file_name = row["file_name"]
    user_dir = Path(Path.cwd(), "pdf_files", user_id)
    user_pdf = Path(user_dir, file_name)

    # -- delete from file system
    if user_pdf.exists():
        user_pdf.unlink()

    # -- delete from database
    num_deletes = deleteRow(db, table="files", where="user_id=? AND entry_id=?", values=[user_id, entry_id])
    res = {"message": f"{num_deletes} file deleted", "file": user_pdf.as_posix()}

    git_update()
    if request.params.get("webapp"):
        return template("static/templates/delay.tpl", res=res, location="/dashboard")
    return clean(res)

@app.route('/processFile', method="POST")
def processFile(db):
    user_id = request.get_cookie("user_id", secret=secret_key)
    if not user_id:
        redirect('/')

    entry_id = str(request.params.get("entry_id"))
    row = fetchRow(db, table="files", where="user_id=? AND entry_id=?", values=[user_id, entry_id])
    if not row:
        res = {"message": "no file with matching 'entry_id' and 'user_id'", "user_id": user_id, "entry_id": entry_id}
        if request.params.get("webapp"):
            return template("static/templates/delay.tpl", res=res, location="/dashboard")
        return clean(res)

    # -- file found and belongs to user
    file_name = row["file_name"]
    user_dir = Path(Path.cwd(), "pdf_files", user_id)
    user_pdf = str(Path(user_dir, file_name))
    dst_pdf = str(Path(Path.cwd(), "pdf_outgoing", "temp.pdf"))
    shutil.copy(user_pdf, dst_pdf)
    # -- send file to [pdf_outgoing]

    res = {"message": "processing file", "file": user_pdf}
    if request.params.get("webapp"):
        return template("static/templates/delay.tpl", res=res, location="/dashboard")
    return clean(res)

@app.route("/search", method=["GET", "POST"])
def search(db):
    user_id = request.get_cookie("user_id", secret=secret_key)
    if not user_id:
        redirect('/')
    if (len(request.params) == 1) and (request.params.get("webapp")):
        return template("static/templates/search.tpl",
                        user_values={}, levels=getLevels(db), categories=getCategories(db))
    if (len(request.params) == 2) and (not request.params.get("webapp")):
        levels = {"level" + str(i + 1): d["level"] for i, d in enumerate(getLevels(db))}
        categories = {"category" + str(i + 1): d["category"] for i, d in enumerate(getCategories(db))}
        return clean({"message": "search", "levels": levels, "categories": categories})

    query = {}
    user_values = {}
    if request.params.get("title"):
        query.update({"title LIKE ?": ["%" + request.params["title"] + "%"]})
        user_values["title"] = request.params["title"]
    for term in {"level", "category"}:
        items = {k: v for k, v in request.params.items() if term in k}
        if items:
            item_key = " OR ".join([f"{term} = ?" for k in items.keys()])
            item_value = list(items.values())
            query.update({f"({item_key})": item_value})
            user_values[term] = list(items.keys())
    conditions = " AND ".join(query)
    values = list(chain(*query.values()))

    rows = fetchRows(db, table="mmf", where=conditions, values=values)
    if not rows:
        rows = {}
    if request.params.get("webapp"):
        return template("static/templates/search.tpl",
                        user_values=user_values, query=query,
                        levels=getLevels(db), categories=getCategories(db), rows=rows)
    return clean({"message": "search results", "files": rows})

@app.route("/downloadFile", method=["GET", "POST"])
def downloadFile(db):
    user_id = request.get_cookie("user_id", secret=secret_key)
    if not user_id:
        redirect('/')
    if not request.params.get("entry_id"):
        if request.params.get("webapp"):
            return template("static/templates/delay.tpl", res={"message": "missing 'entry_id'"}, location="/dashboard")
        return clean({"message": "missing 'entry_id'"})

    mmf_entry_id = str(request.params.get("entry_id"))
    mmf_file = fetchRow(db, table="mmf", where="entry_id = ?", values=[mmf_entry_id])
    print(f"mmf_file = {mmf_file}")

    # -- check if file exists
    title = mmf_file["title"]
    level = mmf_file["level"]
    category = mmf_file["category"]
    file_name = Path(mmf_file["pdf_file"]).name
    entry_time = datetime.now()
    user_dir = Path(Path.cwd(), "pdf_files", user_id)
    Path.mkdir(user_dir, exist_ok=True)

    if user_dir.joinpath(file_name).exists():
        res = {"message": "file exists!", "title": title, "file": user_dir.joinpath(file_name)}
        if request.params.get("webapp"):
            return template("static/templates/delay.tpl", res=clean(res), location="/dashboard")
        return clean(res)

    # -- download (copy) file
    src_file = str(Path(Path.cwd(), "lib/making_music_fun", mmf_file["pdf_file"]))
    dst_file = str(Path(user_dir, file_name))
    print("### COPY ###")
    print(f'src_file = "{src_file}"')
    print(f'dst_file = "{dst_file}"')
    shutil.copy(src_file, dst_file)
    params = {
        "table": "files",
        "columns": ["user_id", "title", "file_name", "level", "category", "entry_time"],
        "col_values": [user_id, title, file_name, level, category, entry_time]
    }
    entry_id = str(insertRow(db, **params))
    res = {"message": "file downloaded", "mmf_entry_id": mmf_entry_id, "entry_id": entry_id}

    git_update()
    if request.params.get("webapp"):
        return template("static/templates/delay.tpl", res=res, location="/dashboard")
    return clean(res)
    # redirect("/dashboard")


###############################################################################
#                                 Static Files                                #
###############################################################################
@app.route('/static/css/<filename:re:.*\.css>')
def send_css(filename):
    dirname = sys.path[0]
    print(f'dirname: {dirname}')
    print(f'filename: {filename}')
    print(f'sending: {filename}')
    return static_file(filename, root=f'{dirname}/static/css')


# -- Run Web Server
port = int(os.environ.get("PORT", 8080))
# run(app, host="0.0.0.0", port=port, reloader=True, debug=True)
run(app, host="0.0.0.0", port=port, reloader=True)

###############################################################################
#                                  Deprecated                                 #
###############################################################################
"""
@app.route("/uploadFile", method="GET")
def uploadFile():
    if not request.get_cookie("user_id", secret=secret_key):
        redirect('/')
    return template("static/templates/upload.tpl")

@app.route("/uploadFile", method="POST")
def uploadFile(db):
    if not request.get_cookie("user_id", secret=secret_key):
        redirect('/')

    user_id = str(request.get_cookie("user_id", secret=secret_key))
    upload  = request.files.get('upload')
    file_name = upload.filename
    name, ext = os.path.splitext(file_name)
    if ext.lower() != ".pdf":
        res = {
            "message": f"file extension {ext} is not allowed"
        }
        return template("static/templates/delay.tpl", res=clean(res), location="/dashboard")

    entry_time = datetime.now()
    user_dir = Path(Path.cwd(), "pdf_files", user_id)
    Path.mkdir(user_dir, exist_ok=True)
    if user_dir.joinpath(file_name).exists():
        res = {
            "message": "file exists!",
            "file": user_dir.joinpath(file_name)
        }
        return template("static/templates/delay.tpl", res=clean(res), location="/dashboard")

    upload.save(user_dir.as_posix())
    params = {
        "table": "files",
        "columns": ["user_id", "file_name", "entry_time"],
        "col_values": [user_id, file_name, entry_time]
    }
    entry_id = insertRow(db, **params)

    res = {
        "message": "file uploaded",
        "entry_id": entry_id
    }
    print(res)
    return template("static/templates/delay.tpl", res=res, location="/dashboard")
    # redirect("/dashboard")


"""
