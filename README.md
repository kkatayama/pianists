
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
git clone https://github.com/kkatayama/m2band.git
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
sqlite3 m2band.db
```

### 1.b Create Tables
``` sql
CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, create_time TIMESTAMP NOT NULL);
CREATE TABLE oximeter (entry_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, heart_rate INTEGER, blood_o2 INTEGER, temperature DOUBLE, entry_time TIMESTAMP);
```

## 2. App

### 2.a Run App

``` bash
python3 server.py 8080
```


### 2.b Testing

Make a `GET` request to [http://raspberry-pi-ip-address:8080/](http://raspberry-pi-ip-address:8080/)

``` json
{
    "message": "available commands",
    "GET": [
        {
            "/": {
                "Note": "debug function",
                "Returns": "this list of available commands"
            }
        },
        {
            "/getUsers": {
                "Note": "debug function",
                "Returns": "list of users in the 'users' table"
            }
        },
        {
            "/getAllSensorData": {
                "Note": "debug function",
                "Returns": "Sensor data for all users"
            }
        }
    ],
    "POST": [
        {
            "/login": {
                "Params": [
                    "username",
                    "password"
                ],
                "Returns": [
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
            },
            "/createUser": {
                "Params": [
                    "username",
                    "password"
                ],
                "Returns": [
                    {
                        "message": "user exists",
                        "username": "username"
                    },
                    {
                        "message": "user created",
                        "user_id": "user_id",
                        "username": "username"
                    }
                ]
            },
            "/getUser": {
                "Params": [
                    "user_id"
                ],
                "Returns": [
                    {
                        "message": "user account details",
                        "data": "json object of user info for 'user_id'"
                    }
                ]
            },
            "/addSensorData": {
                "Params": [
                    "user_id",
                    "heart_rate",
                    "blood_o2",
                    "temperature"
                ],
                "Returns": [
                    {
                        "message": "sensor data added for 'user_id'",
                        "user_id": "user_id",
                        "row_id": "row_id"
                    }
                ]
            },
            "/getSensorData": {
                "Params": [
                    "user_id"
                ],
                "Returns": [
                    {
                        "message": "sensor data for 'user_id'",
                        "data": "list of sensor data for 'user_id'"
                    }
                ]
            }
        }
    ],
    "POST|PUT": [
        {
            "/editUser": {
                "Params": [
                    "user_id",
                    "username AND/OR password"
                ],
                "Returns": [
                    {
                        "message": "user edited",
                        "user_id": "user_id"
                    }
                ]
            }
        }
    ],
    "POST|DELETE": [
        {
            "/deleteUser": {
                "Params": [
                    "user_id"
                ],
                "Returns": [
                    {
                        "message": "user deleted",
                        "user_id": "user_id"
                    }
                ]
            }
        }
    ]
}
```

