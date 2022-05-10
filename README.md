github: [https://github.com/kkatayama/pianists](https://github.com/kkatayama/pianists)
website: [https://pianists.hopto.org](https://pianists.hopto.org)

# WatchDog Overview
* There are three `watchdog` scripts in the **pianists/systemd** directory
* Each `watchdog` script monitors an empty **watch** directory for a **file**.
* Once a **file** is detected, the **file** is moved to a **temp** directory for processing.
* After processing has completed, the **processed file** is then sent to the next **machine**

FLOW: \[Web Server\] -> \[Macbook\] -> \[Raspberry PI\]

| watchdog | running location | default paths | notes |
| :--- | :--- | :--- | :--- |
| monitor.py | web server | watch: `pianists/pdf_outgoing` | file added on `Process File` click |
| | | temp: `pianists/systemd/ml_results` | pdf moved here and processed | 
| monitor_MAC.py | macbook | watch: `$HOME/incoming` | waits for `ml_results.zip` file |
| | | temp: `$HOME/ml_processing` | `zip` extracted and processed here |
| monitor_PI.py | raspberry pi | watch: `$HOME/incoming` | waits for `.pcode` file |
| | | temp: `$HOME/pcode_processing` | `pcode` file processed here | 

## monitor.py (Web Server)
1. move pdf file to TEMP_PATH 
  * `pianists/pdf_outgoing/humpty-dumpty-piano.pdf` -> `pianists/systemd/ml_results/humpty-dumpty-piano.pdf`
2. run audiveris on the pdf file
  * `audiveris -batch -transcribe -export humpty-dumpty-piano.pdf -output omr_results`
3. parse mxl and extract notes
  * `pianists/utils/parse_mxl.py "pianists/systemd/ml_results/omr_result/humpty-dumpty-piano/humpty-dumpty-piano.mxl" "pianists/systemd/ml_results/omr_result"` 
4. crop image drawings
  * `pianists/utils/extract_pdf_drawings.py "pianists/systemd/ml_results/humpty-dumpty-piano/humpty-dumpty-piano.pdf" "pianists/systemd/ml_results"`
5. compress files to a .zip archive
  * `pianists/systemd/ml_results.zip`
6. send file
  * sends `ml_results.zip` to **macbook:$HOME/incoming**

### ml_results.zip
The **.csv** and **.json** file contain parsed results from the **audiveris ML run**
I hope these files are useful.

```c
ml_results
├── draw_crop
│   ├── 0.png
│   ├── 1.png
│   ├── 2.png
│   ├── 3.png
│   ├── ...
├── draw_raw
│   ├── 0.png
│   ├── 2.png
│   ├── 4.png
│   ├── ...
├── humpty-dumpty-piano.pdf
└── omr_results
    ├── humpty-dumpty-piano
    │   ├── humpty-dumpty-piano-20220510T1243.log
    │   ├── humpty-dumpty-piano.mxl
    │   └── humpty-dumpty-piano.omr
    ├── humpty-dumpty-piano.csv
    └── humpty-dumpty-piano.json
```

#### `ml_results/omg_results/humpty-dumpty-piano.csv`
```csv
┏━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃    ┃ time ┃ pitch ┃ duration ┃ velocity ┃ pitch_str ┃
┡━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ 0  │ 0    │ 59    │ 2        │ 64       │ B3        │
│ 1  │ 2    │ 62    │ 1        │ 64       │ D4        │
│ 2  │ 3    │ 60    │ 2        │ 64       │ C4        │
│ 3  │ 5    │ 64    │ 1        │ 64       │ E4        │
│ 4  │ 6    │ 62    │ 1        │ 64       │ D4        │
│ 5  │ 7    │ 64    │ 1        │ 64       │ E4        │
│ 6  │ 8    │ 66    │ 1        │ 64       │ F#4       │
│ 7  │ 9    │ 67    │ 3        │ 64       │ G4        │
│ 8  │ 12   │ 59    │ 2        │ 64       │ B3        │
│ 9  │ 14   │ 62    │ 1        │ 64       │ D4        │
│ .. │ ...  │ ...   │ ...      │ ...      │ ...       │
└────┴──────┴───────┴──────────┴──────────┴───────────┘
```

#### `ml_results/omg_results/humpty-dumpty-piano.json`
```json
{
  "metadata": {
    "schema_version": "0.2",
    "title": "[Audiveris detected movement]",
    "creators": ["Traditional", "arr. by Benny Chaw"],
    "source_filename": "humpty-dumpty-piano.mxl",
    "source_format": "musicxml"
  },
  "resolution": 1,
  "tempos": [{"time": 0, "qpm": 120.0}],
  "time_signatures": [{"time": 0, "numerator": 3, "denominator": 4}],
  "barlines": [{
      "time": 0
    },{
      "time": 3
    },{
      "time": ...
  }],
  "beats": [{
      "time": 0
    },{
      "time": 1
    },{
      "time": ...
  }],
  "tracks": [{
      "program": 1,
      "is_drum": false,
      "name": "Acoustic Grand Piano",
      "notes": [{
          "time": 0,
          "pitch": 59,
          "duration": 2,
          "velocity": 64,
          "pitch_str": "B3"
        },{
          "time": 2,
          "pitch": 62,
          "duration": 1,
          "velocity": 64,
          "pitch_str": "D4"
        },{
          "...": ...,
      }]
  }]
}
```

## monitor_MAC.py (Macbook)
1. move zip file to TEMP_PATH
2. extract zip file
3. parse signature and notes
4. parse drawings and do more machine learning ...?
5. generate p-code ...
6. send p-code to raspberry pi
7. touch p-code file on raspberry pi

### Steps 4. and 5. need to be edited

## monitor_PI.py (Raspberry PI)
1. move pcode file to TEMP_PATH
2. parse pcode file
3. send pcode instructions ... ?

### Right now the pcode file contains dummy text!

# Install and Setup Watchdog

## Macbook
**1. clone repo**

```bash
git clone https://github.com/kkatayama/pianists.git
cd pianists
```

**2. run installer**

```bash
python3 systemd/install_services.py
```

```bash
╭──────────────────────────────────────────────────────────────────────────────╮
│            Configure Setup: (press enter to select default value)            │
╰──────────────────────────────────────────────────────────────────────────────╯
USER (katayama):
SERVICE_NAME (com.pianists.watchdog):
WATCH_PATH (/Users/katayama/incoming):
PYTHON_EXE (/Users/katayama/.pyenv/versions/3.9.1/bin/python3):
WATCH_DOG (/Users/katayama/Documents/School/Senior_Design/CAPSTONE_2021/PIANIST/pianists/systemd/monitor_MAC.py):
TEMP_PATH (/Users/katayama/ml_processing):



Exporting Config: /Users/katayama/.config/pianists/config.ini

Notify Server
```

## Raspberry PI
**1. clone repo**

```bash
git clone https://github.com/kkatayama/pianists.git
cd pianists
```

**2. run installer**

```bash
python3 systemd/install_services.py
```

```bash
╭──────────────────────────────────────────────────────────────────────────────╮
│            Configure Setup: (press enter to select default value)            │
╰──────────────────────────────────────────────────────────────────────────────╯
USER (pi):
SERVICE_NAME (P-Code Monitor):
WATCH_PATH (/home/pi/incoming):
PYTHON_EXE (/usr/bin/python3):
WATCH_DOG (/home/pi/pianists/systemd/monitor_PI.py):
TEMP_PATH (/home/pi/pcode_processing):



Exporting Config: /home/pi/.config/pianists/config.ini

Notify Server
```

# Running Watchdog
These instructions work for both **Macbook** and **Raspberry PI**
Originally, I tried running as a `LaunchAgent Daemon` and a `systemd daemon` but some of the `subprocess` calls failed to run.
So while testing and debugging, run manually.

**Macbook**

```bash
python3 systemd/monitor_MAC.py
```

**Raspberry PI**

```bash
python3 systemd/monitor_PI.py
```

# Running Watchdog as a Background Process
When you are done testing, you can run in background **directly** or in a **tmux** shell.
I prefer **tmux** shell.

## Using Tmux
#### 1. start tmux

```bash
tmux
```

#### 2. run watchdog

```bash
python3 systemd/monitor_MAC.py
```

**OR**

```bash
python3 systemd/monitor_PI.py
```

#### 3. send tmux session to background "CTRL + b" -> "d"

```bash
1. press "CTRL + b" keys 
2. then release "CTRL" key and press "d" key
```

#### 4. to recover a **tmux** session

```bash
tmux attach -t 0
```

## Running in Background Directly

```bash
python3 systemd/monitor_MAC.py &
```

**OR**

```bash
python3 systemd/monitor_PI.py
```

# Accessing Watchdog Logs

```bash
tail -f logs/monitor_MAC.log
```

**OR**

```bash
tail -f logs/monitor_PI.log
```

---


# API Endpoints
All requests can be `Content-Type`: `application/json`, `application/x-www-form-urlencoded`, or `multipart/form-data`.

## https://pianists.hopto.org/login
**Method:  `POST`**

| Params | Description / Options |
| :--- | :--- |
| `username` | user login name |
| `password` | user password |

**Returns: `token`**

### Example:

```bash
curl -s -XPOST "https://pianists.hopto.org/login" -d '{"username": "user_1", "password": "user_1"}'
```

```json
{
  "message": "user login success",
  "user_id": 1,
  "username": "user_1",
  "token": "IU5nZ2JlRllEL1B0UjJZMnlkSzR0anc9PT9nQVdWRVFBQUFBQUFBQUNNQjNWelpYSmZhV1NVakFFeGxJYVVMZz09"
}
```

## https://pianists.hopto.org/createUser
**Method:  `POST`**

| Params | Description / Options |
| :--- | :--- |
| `username` | user login name |
| `password` | user password |
| `password2` | user password again |

**Returns: `token`**

### Example:

```bash
curl -s -XPOST "https://pianists.hopto.org/createUser" -d '{"username": "user_3", "password": "user_3", "password2": "user_3"}'
```

```json
{
  "message": "user created",
  "user_id": 12,
  "username": "user_3",
  "token": "IUhKN3dBUHJMeUEzNW1kOU8reGtSMXc9PT9nQVdWRWdBQUFBQUFBQUNNQjNWelpYSmZhV1NVakFJeE1wU0dsQzQ9"
}
```


## https://pianists.hopto.org/dashboard
**Method:  `GET`**

| Params | Description / Options |
| :--- | :--- |
| `token` | api_token provided at login |

**Returns: `json array`**

### Example:

```bash
curl -sL -XGET "https://pianists.hopto.org/dashboard?token=IU5nZ2JlRllEL1B0UjJZMnlkSzR0anc9PT9nQVdWRVFBQUFBQUFBQUNNQjNWelpYSmZhV1NVakFFeGxJYVVMZz09"
```

**OR**

```bash
curl -sL -XGET "https://pianists.hopto.org/dashboard" -d '{"token": "IU5nZ2JlRllEL1B0UjJZMnlkSzR0anc9PT9nQVdWRVFBQUFBQUFBQUNNQjNWelpYSmZhV1NVakFFeGxJYVVMZz09"}'
```

**OR**
```bash
 curl -sL -XGET "https://pianists.hopto.org/dashboard" -H 'Content-Type: application/json' -d '{"token": "IU5nZ2JlRllEL1B0UjJZMnlkSzR0anc9PT9nQVdWRVFBQUFBQUFBQUNNQjNWelpYSmZhV1NVakFFeGxJYVVMZz09"}'
```

```json
{
  "message": "user_dashboard",
  "files": [
    {
      "entry_id": 5,
      "user_id": 1,
      "title": "Amazing Grace",
      "level": "Level 1",
      "category": "Christian",
      "file_name": "amazing-grace-beginner-piano.pdf",
      "entry_time": "2022-04-19 10:36:51.983859"
    },
    {
      "entry_id": 6,
      "user_id": 1,
      "title": "Mexican Hat Dance",
      "level": "Level 1",
      "category": "no_category",
      "file_name": "mexican-hat-dance-piano-solo.pdf",
      "entry_time": "2022-04-19 10:37:07.447791"
    },
    ...
  ]
}
```

## https://pianists.hopto.org/search
**Method:  `GET`, `POST`**

| Params | Description / Options |
| :--- | :--- |
| `token` | api_token provided at login |
| `level` | `Level 1`, `Level 2`, `Level 3`, `Level 4`, `Level 5` |
| `category` | `Bach`, `Beethoven`, `Brahms`, `Celtic`, `Christian`, `Christmas`, `Classical`, `Duets`, `Jazz`, `Joplin`, `MMF Original`, `Mother Goose`, `Mozart`, `Nursery Rhyme`, `Patriotic`, `Scales`, `Tchaikovsky`, `no_category` |

**Returns: `json array`**

### Example

```bash
curl -sL -XGET "https://pianists.hopto.org/search" -d '{"level": "Level 1", "category": "Christian", "token": "IU5nZ2JlRllEL1B0UjJZMnlkSzR0anc9PT9nQVdWRVFBQUFBQUFBQUNNQjNWelpYSmZhV1NVakFFeGxJYVVMZz09"}'
```

```json
{
  "message": "search results",
  "files": [
    {
      "entry_id": 3,
      "title": "Amazing Grace",
      "url": "https://makingmusicfun.net/htm/f_printit_free_printable_sheet_music/amazing-grace-easy-piano.php",
      "category": "Christian",
      "level": "Level 1",
      "pdf_file": "pdf_files/Level_1/amazing-grace-beginner-piano.pdf",
      "pdf_url": "https://makingmusicfun.net/pdf/sheet_music/amazing-grace-beginner-piano.pdf",
      "entry_time": "2022-04-14 16:07:04.000"
    },
    {
      "entry_id": 38,
      "title": "It Is Well with My Soul",
      "url": "https://makingmusicfun.net/htm/f_printit_free_printable_sheet_music/it-is-well-with-my-soul-piano.php",
      "category": "Christian",
      "level": "Level 1",
      "pdf_file": "pdf_files/Level_1/it-is-well-with-my-soul-piano.pdf",
      "pdf_url": "https://makingmusicfun.net/pdf/sheet_music/it-is-well-with-my-soul-piano.pdf",
      "entry_time": "2022-04-14 16:07:04.000"
    },
    ...
  ]
}

```

## https://pianists.hopto.org/downloadFile
**Method:  `GET`, `POST`**

| Params | Description / Options |
| :--- | :--- |
| `token` | api_token provided at login |
| `entry_id` | file id provided in **/search** results |

**Returns: `json object`**

### Example:

```bash
curl -s -XPOST "https://pianists.hopto.org/downloadFile" -d '{"entry_id": 106, "token": "IUhKN3dBUHJMeUEzNW1kOU8reGtSMXc9PT9nQVdWRWdBQUFBQUFBQUNNQjNWelpYSmZhV1NVakFJeE1wU0dsQzQ9"}'
```

```json
{
  "message": "file downloaded",
  "mmf_entry_id": "106",
  "entry_id": "15"
}
```

## https://pianists.hopto.org/deleteFile
**Method:  `POST`**

| Params | Description / Options |
| :--- | :--- |
| `token` | api_token provided at login |
| `entry_id` | file id provided in **/dashboard** results |

**Returns: `json object`**

### Example:

```bash
curl -s -XPOST "https://pianists.hopto.org/deleteFile" -d '{"entry_id": 15, "token": "IUhKN3dBUHJMeUEzNW1kOU8reGtSMXc9PT9nQVdWRWdBQUFBQUFBQUNNQjNWelpYSmZhV1NVakFJeE1wU0dsQzQ9"}'
```

```json
{
  "message": "1 file deleted",
  "file": "/home/katayama/Documents/pianists/pdf_files/12/god-is-so-good-piano.pdf"
}
```

## https://pianists.hopto.org/processFile
**Method:  `POST`**

| Params | Description / Options |
| :--- | :--- |
| `username` | user login name |
| `password` | user password |

**Returns: `token`**

### Example:

```bash
 curl -sL -XPOST "https://pianists.hopto.org/processFile" -d '{"entry_id": 13, "token": "IU5nZ2JlRllEL1B0UjJZMnlkSzR0anc9PT9nQVdWRVFBQUFBQUFBQUNNQjNWelpYSmZhV1NVakFFeGxJYVVMZz09"}'
```

```json
{
  "message": "processing file",
  "file": "/home/katayama/Documents/pianists/pdf_files/1/humpty-dumpty-piano.pdf"
}
```





