# Easy Status

## Server Startup Args
`python3 server.py FILE_PATH HOST PORT`

`FILE_PATH` String  
`HOST` String  
`PORT` int  

## Server Commands

- `add <name> p` protokoll noch nicht unterschrieben
- `add <name> u` urkunden
- `add <name> a` ausgehangen
- `rem <name> p` protokoll noch nicht unterschrieben
- `rem <name> u` urkunden
- `rem <name> a` ausgehangen
- `p` print wk overview
- `s` save to File 

## Save File Format (*.txt)

| Name  | Protokoll | Aushang | Urkunden |
|-------|-----------|---------|----------|
| `str` | `bool`    | `bool`  | `bool`   |