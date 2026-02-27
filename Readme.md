# Easy Status

`Python Version 3.12`  
because of Ubuntu LTS

## Setup venv on Ubuntu
`python -m venv /path/to/new/virtual/environment`  
`source <venv>/bin/activate`  
`pip install -r requirements.txt`  

## Server Startup Args
`python3 server.py FILE_PATH HOST PORT`

`FILE_PATH` String  
`HOST` String  
`PORT` int  

## Server Commands

- `add <name> p` protokoll noch nicht unterschrieben
- `add <name> f` finale erstellt
- `add <name> a` ausgehangen
- `rem <name> p` protokoll noch nicht unterschrieben
- `rem <name> f` finale erstellt
- `rem <name> a` ausgehangen
- `p` print wk overview
- `s` save to File 
-  `quit` programm

## Save File Format (*.txt)

| Name  | Protokoll | Aushang | Urkunden |
|-------|-----------|---------|----------|
| `str` | `bool`    | `bool`  | `bool`   |

## Build Client

`pyinstaller -F --windowed .\Client\ClientMainGui.py`