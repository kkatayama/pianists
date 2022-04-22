from bottle import install, request, response, run, template, static_file, redirect, HTTPError, get
from bottle_sqlite import SQLitePlugin, sqlite3
# from bottle_errorsrest import ErrorsRestPlugin
from itertools import chain
from db_functions import *
from datetime import datetime
from pathlib import Path
from hashlib import sha256
from secret import key
from rich import print
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
plugin = SQLitePlugin(dbfile="pianists.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
app.install(plugin)
app.install(ErrorsRestPlugin())


@app.route("/commands", method=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def commands():
    with open('all_commands.json') as f:
        res = json.load(f)
    print(res)
    return res

###############################################################################
#                            Users Table Functions                            #
###############################################################################
@app.route("/", method="GET")
@app.route("/login", method=["GET"])
def index():
    return template("templates/index.tpl")

@app.route("/login", method="POST")
def login(db):
    try:
        username = request.POST["username"]
        password = request.POST["password"]
    except KeyError:
        res = {
            "message": "missing paramater",
            "required params": ["username", "password"]
        }
        print(res)
        return template("templates/index.tpl", res=res)

    # -- check if user exists
    params = {
        "table": "users",
        "where": "username=?",
        "values": username
    }
    row = fetchRow(db, **params)
    if not row:
        res = {
            "message": "user does not exist",
            "username": username
        }
        print(res)
        return template("templates/index.tpl", res=res)

    # -- check user supplied password (previous row statement has user data for username=[username])
    if not checkPassword(password, row["password"]):
        # -- checkPassword() returned False
        res = {
            "message": "incorrect password",
            "password": password
        }
        print(res)
        return template("templates/index.tpl", res=res)

    # -- made it here: means username exists and checkPassword() returned True
    response.set_cookie("user_id", row["user_id"], secret=key)
    res = {
        "message": "user login success",
        "user_id": row["user_id"],
        "username": row["username"]
    }
    print(res)
    return template("templates/delay.tpl", res=res, location="/dashboard")

@app.route("/register", method="GET")
def register():
    print("registration page")
    return template("templates/register.tpl")

@app.route("/createUser", method="POST")
def createUser(db):
    try:
        username  = request.POST["username"]
        plaintext = request.POST["password"]
        password2 = request.POST["password2"]
    except KeyError:
        res = {
            "message": "missing paramater",
            "required params": ["username", "password", "password2"]
        }
        print(res)
        return template("templates/register.tpl", res=res)

    if plaintext != password2:
        res = {
            "message": "passwords do not match",
            "password1": plaintext,
            "password2": password2
        }
        print(res)
        return template("templates/register.tpl", res=res)

    password  = securePassword(plaintext)
    create_time = datetime.now()

    # -- check if user exists
    params = {
        "table": "users",
        "where": "username=?",
        "values": username
    }
    row = fetchRow(db, **params)
    if row:
        res = {
            "message": "user exists",
            "username": row["username"]
        }
        print(res)
        return template("templates/register.tpl", res=res)

    # -- if user doesn't exist, create user
    params = {
        "table": "users",
        "columns": ["username", "password", "create_time"],
        "col_values": [username, password, create_time],
    }
    user_id = insertRow(db, **params)

    res = {
        "message": "user created",
        "user_id": user_id,
        "username": username
    }
    print(res)
    return template("templates/index.tpl", res=res)

@app.route('/logout', method="GET")
def logout():
    res = {
        "message": "user logged out"
    }
    print(res)
    response.delete_cookie('user_id')
    redirect('/')

@app.route('/dashboard', method="GET")
def dashboard(db):
    if not request.get_cookie("user_id", secret=key):
        redirect('/')

    user_id = str(request.get_cookie("user_id", secret=key))
    params = {
        "table": "files",
        "where": "user_id=?",
        "values": user_id
    }
    rows = fetchRows(db, **params)
    if rows:
        return template("templates/dashboard.tpl", rows=rows)
    return template("templates/dashboard.tpl")


###############################################################################
#                            files Table Functions                            #
###############################################################################
@app.route("/uploadFile", method="GET")
def uploadFile():
    if not request.get_cookie("user_id", secret=key):
        redirect('/')
    return template("templates/upload.tpl")

@app.route("/uploadFile", method="POST")
def uploadFile(db):
    if not request.get_cookie("user_id", secret=key):
        redirect('/')

    user_id = str(request.get_cookie("user_id", secret=key))
    upload  = request.files.get('upload')
    file_name = upload.filename
    name, ext = os.path.splitext(file_name)
    if ext.lower() != ".pdf":
        res = {
            "message": f"file extension {ext} is not allowed"
        }
        return template("templates/delay.tpl", res=clean(res), location="/dashboard")

    entry_time = datetime.now()
    user_dir = Path(Path.cwd(), "pdf_files", user_id)
    Path.mkdir(user_dir, exist_ok=True)
    if user_dir.joinpath(file_name).exists():
        res = {
            "message": "file exists!",
            "file": user_dir.joinpath(file_name)
        }
        return template("templates/delay.tpl", res=clean(res), location="/dashboard")

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
    return template("templates/delay.tpl", res=res, location="/dashboard")
    # redirect("/dashboard")

@app.route("/deleteFile", method="POST")
def deleteFile(db):
    if not request.get_cookie("user_id", secret=key):
        redirect('/')
    user_id = str(request.get_cookie("user_id", secret=key))
    entry_id = str(request.POST.get("entry_id"))
    params = {
        "table": "files",
        "where": "user_id=? AND entry_id=?",
        "values": [user_id, entry_id],
    }
    row = fetchRow(db, **params)

    if not row:
        res = {
            "message": "no file with matching 'entry_id' and 'user_id'",
            "user_id": user_id,
            "entry_id": entry_id
        }
        print(res)
        return template("templates/delay.tpl", res=res, location="/dashboard")

    # -- file found and belongs to user
    file_name = row["file_name"]
    user_dir = Path(Path.cwd(), "pdf_files", user_id)
    user_pdf = Path(user_dir, file_name)

    # -- delete from file system
    if user_pdf.exists():
        user_pdf.unlink()

    # -- delete from database
    params = {
        "table": "files",
        "where": "user_id=? AND entry_id=?",
        "values": [user_id, entry_id]
    }
    num_deletes = deleteRow(db, **params)
    res = {
        "message": f"{num_deletes} file deleted",
        "file": user_pdf.as_posix()
    }
    print(res)
    return template("templates/delay.tpl", res=res, location="/dashboard")

@app.route('/processFile', method="POST")
def processFile(db):
    if not request.get_cookie("user_id", secret=key):
        redirect('/')
    user_id = str(request.get_cookie("user_id", secret=key))
    entry_id = str(request.POST.get("entry_id"))
    params = {
        "table": "files",
        "where": "user_id=? AND entry_id=?",
        "values": [user_id, entry_id],
    }
    row = fetchRow(db, **params)

    if not row:
        res = {
            "message": "no file with matching 'entry_id' and 'user_id'",
            "user_id": user_id,
            "entry_id": entry_id
        }
        print(res)
        return template("templates/delay.tpl", res=res, location="/dashboard")
    # -- file found and belongs to user
    file_name = row["file_name"]
    user_dir = Path(Path.cwd(), "pdf_files", user_id)
    user_pdf = Path(user_dir, file_name).as_posix()
    res = {
        "message": "processing file",
        "file": user_pdf
    }
    print(res)
    return template("templates/delay.tpl", res=res, location="/dashboard")

@app.route("/search", method=["GET", "POST"])
def search(db):
    print(f'params = {request.params}')
    if not request.get_cookie("user_id", secret=key):
        redirect('/')
    if not request.params:
        return template("templates/search.tpl",
                        user_values={}, levels=getLevels(db), categories=getCategories(db))

    user_id = str(request.get_cookie("user_id", secret=key))
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
    print(rows)
    return template("templates/search.tpl",
                    user_values=user_values, query=query,
                    levels=getLevels(db), categories=getCategories(db), rows=rows)

@app.route("/downloadFile", method=["GET", "POST"])
def downloadFile(db):
    if not request.get_cookie("user_id", secret=key):
        redirect('/')
    if not request.params.get("entry_id"):
        return template("templates/delay.tpl", res={"message": "missing 'entry_id'"}, location="/dashboard")
    user_id = str(request.get_cookie("user_id", secret=key))
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
        res = {
            "message": "file exists!",
            "title": title,
            "file": user_dir.joinpath(file_name)
        }
        return template("templates/delay.tpl", res=clean(res), location="/dashboard")

    # -- download (copy) file
    src_file = str(Path(Path.cwd(), "making_music_fun", mmf_file["pdf_file"]))
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
    entry_id = insertRow(db, **params)

    res = {
        "message": "file downloaded",
        "entry_id": entry_id
    }
    print(res)
    return template("templates/delay.tpl", res=res, location="/dashboard")
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
run(app, host="0.0.0.0", port=port, reloader=True, debug=True)
# run(app, host="0.0.0.0", port=port, reloader=True)
