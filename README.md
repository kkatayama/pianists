
# RaspberryPi Setup

To run this server, we will need to install additional packages:

0. git
1. Python
   a. python3
   b. python3-pip
2. Web Framework
   a. bottle
   b. bottle-sqlite
3. Database
   a. sqlite3

## 0. git

### 0.a Install Git (this is optional)

``` bash
sudo apt-get install git
```

### 0.b Clone this Repo

``` bash
git clone https://github.com/kkatayama/pianists.git
```

## 1. Python

### 1.a Installing `python3`

```bash
sudo apt-get install python3

```

### 1.b Installingg `python3-pip`

```bash
sudo apt-get install python3-pip
```

## 2. Web Framework

### 2.a Installing `bottle`
```bash
pip3 install bottle
```

### 2.b Installing `bottle-sqlite`
The `bottle-sqlite` library does not include `detect_types` which is needed for python `datetime` support.
I copied the source code and added this functionality.

```bash
pip3 install -U git+https://github.com/kkatayama/bottle-sqlite.git@master
```

## 3. Database

### 3.a Installing `sqlite3`
```bash
sudo apt-get install sqlite3
```

# APP Setup

## 1. Database (Optional)
These database steps are only needed if you did not do step `0.b`

### 1.a Create Database

``` bash
sqlite3 pianists.db
```

### 1.b Create Tables
``` sql
CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, create_time TIMESTAMP NOT NULL);
CREATE TABLE files (entry_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, file_name TEXT NOT NULL, entry_time TIMESTAMP);
```

## 2. App

### 2.a Run App

``` bash
python3 server.py
```


### 2.b Testing

Make a `GET` request to [http://raspberry-pi-ip-address:8080/commands](http://raspberry-pi-ip-address:8080/commands)

``` json
{
  "message": "available commands",
  "GET": [
    {
      "/commands": {
        "Note": "debug function",
        "Returns": "this list of available commands"
      }
    },
    {
      "/": {
        "Note": "index",
        "Returns": "login page"
      }
    },
    {
      "/login": {
        "Note": "login",
        "Returns": "login page"
      }
    },
    {
      "/register": {
        "Note": "add a user",
        "Returns": "user registration page"
      }
    },
    {
      "/logout": {
        "Note": "log a user out",
        "Returns": "login page"
      }
    },
    {
      "/dashboard": {
        "Note": "page for logged in users",
        "Returns": "user dashboard"
      }
    },
    {
      "/uploadFile": {
        "Note": "only pdf files accepted",
        "Returns": "upload file page"
      }
    }
  ],
  "POST": [
    {
      "/login": {
        "Params": [
          "username",
          "password",
          "password2"
        ],
        "Returns": [
          {
            "message": "missing parameter"
          },
          {
            "message": "user does not exist",
            "username": "username"
          },
          {
            "message": "incorrect password",
            "password": "password"
          },
          {
            "message": "user login success",
            "user_id": "user_id",
            "username": "username"
          }
        ]
      }
    },
    {
      "/uploadFile": {
        "Params": [
          "user_id",
          "upload"
        ],
        "Returns": [
          {
            "message": "file extension (ext) is not allowed"
          },
          {
            "message": "file exists!"
          },
          {
            "message": "file uploaded"
          }
        ]
      }
    },
    {
      "/deleteFile": {
        "Params": [
          "user_id",
          "entry_id"
        ],
        "Returns": [
          {
            "message": "no file with matching 'entry_id' and 'user_id'"
          },
          {
            "message": "(num_deletes) files deleted"
          }
        ]
      }
    },
    {
      "/processFile": {
        "Params": [
          "user_id",
          "entry_id"
        ],
        "Returns": [
          {
            "message": "no file with matching 'entry_id' and 'user_id'"
          },
          {
            "message": "processing file"
          }
        ]
      }
    }
  ]
}
```

