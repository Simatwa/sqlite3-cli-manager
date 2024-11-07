<h1 align="center">sqlite3-cli-manager</h1>

<p align="center">
<a href="https://github.com/Simatwa/sqlite3-cli-manager/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/static/v1?logo=GPL&color=Blue&message=MIT&label=License"/></a>
<a href="https://github.com/psf/black"><img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>
<a href="https://github.com/Simatwa/sqlite3-cli-manager/actions/workflows/python-package.yml"><img alt="Python Package flow" src="https://github.com/Simatwa/sqlite3-cli-manager/actions/workflows/python-test.yml/badge.svg?branch=main"/></a>
<a href="https://github.com/Simatwa/sqlite3-cli-manager/releases/latest"><img src="https://img.shields.io/github/downloads/Simatwa/sqlite3-cli-manager/total?label=Asset%20Downloads&color=success" alt="Downloads"></img></a>
<a href="https://github.com/Simatwa/sqlite3-cli-manager/releases"><img src="https://img.shields.io/github/v/release/Simatwa/sqlite3-cli-manager?color=success&label=Release&logo=github" alt="Latest release"></img></a>
<a href="https://github.com/Simatwa/sqlite3-cli-manager/releases"><img src="https://img.shields.io/github/release-date/Simatwa/sqlite3-cli-manager?label=Release date&logo=github" alt="release date"></img></a>
</p>

Python tool designed to interact with SQLite databases via command-line interface

# Pre-requisite

- [x] [Python>=3.12](https://python.org) *(optional)*

# Installation and Usage

## Installation

- Clone repo and install requirements

```sh
git clone https://github.com/Simatwa/sqlite3-cli-manager.git
cd sqlite3-cli-manager
pip install -r requirements.txt
```

Alternatively, you can download standalone executables for your system from [here](https://github.com/Simatwa/sqlite3-cli-manager/releases/latest).

## Usage 

<details open>

<summary><code>$ python manager.py --help</code></summary>

```
Usage: manager.py [OPTIONS] COMMAND [ARGS]...

  Interact with SQLite databases via command-line interface

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  execute       Run sql statements against database [AUTO-COMMITS]
  interactive   Execute sql statements interactively
  show-columns  List columns for a particular table
  show-tables   List tables contained in the database

```

</details>

### Execute

- The `execute` command accepts multiple sql statements and run each against the database before auto-commiting the changes.
<details open>

<summary><code>$ python manager.py execute --help </code></summary>

```
Usage: sqlite-manager execute [OPTIONS] DATABASE

  Run sql statements against database [AUTO-COMMITS]

Options:
  -s, --sql TEXT  Sql statements  [required]
  -j, --json      Stdout results in json format
  -q, --quiet     Do not stdout results
  --help          Show this message and exit.
```

</details>

`$ sqlite-manager execute <path-to-sqlite3-database> -s "<sql-statement>"`

> For example:
<details>
<summary><code>$ python manager execute test.db -s "select * from linux"</code></summary>

``` 
┏━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Index ┃ Col. 1 ┃ Col. 2 ┃ Col. 3    ┃ Col. 4 ┃ Col. 5 ┃ Col. 6     ┃ Col. 7     ┃
┡━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│   0   │ 1      │ Parrot │ community │ None   │ 1      │ 2024-11-07 │ 2024-11-07 │
│       │        │        │           │        │        │ 13:22:13   │ 13:22:13   │
├───────┼────────┼────────┼───────────┼────────┼────────┼────────────┼────────────┤
│   1   │ 2      │ Kali   │ community │ None   │ 1      │ 2024-11-07 │ 2024-11-07 │
│       │        │        │           │        │        │ 13:22:21   │ 13:22:21   │
├───────┼────────┼────────┼───────────┼────────┼────────┼────────────┼────────────┤
│   2   │ 3      │ Ubuntu │ community │ None   │ 1      │ 2024-11-07 │ 2024-11-07 │
│       │        │        │           │        │        │ 13:48:18   │ 13:48:18   │
├───────┼────────┼────────┼───────────┼────────┼────────┼────────────┼────────────┤
│   3   │ 4      │ Fedora │ community │ None   │ 1      │ 2024-11-07 │ 2024-11-07 │
│       │        │        │           │        │        │ 13:48:49   │ 13:48:49   │
└───────┴────────┴────────┴───────────┴────────┴────────┴────────────┴────────────┘──┘
```
</details>

---

### Interactive

- The `interactive` command launches a recursive prompt that takes in sql statements and proceed to run them against the database.
<details open>

<summary><code>$ python manager.py interactive --help </code></summary>

```
Usage: sqlite-manager interactive [OPTIONS] DATABASE

  Execute sql statements interactively

Options:
  -a, --auto-commit          Enable auto-commit
  -C, --disable-coloring     Stdout prompt text in white font color
  -S, --disable-suggestions  Do not suggest sql statements
  -N, --new-history-thread   Start a new history thread
  --help                     Show this message and exit.
```

</details>

`$ sqlite-manager execute <path-to-sqlite3-database> -s "<sql-statement>"`

> For example:
<details>
<summary><code>$ sqlite-manager interactive test.db </code></summary>

``` 
Welcome to interactive sqlite3-db manager.
Run help or h <command> for usage info.
Repo : https://github.com/Simatwa/sqlite3-cli-manager
 
╰─>select * from Linux
┏━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Index ┃ Col. 1 ┃ Col. 2 ┃ Col. 3    ┃ Col. 4 ┃ Col. 5 ┃ Col. 6     ┃ Col. 7     ┃
┡━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│   0   │ 1      │ Parrot │ community │ None   │ 1      │ 2024-11-07 │ 2024-11-07 │
│       │        │        │           │        │        │ 13:22:13   │ 13:22:13   │
├───────┼────────┼────────┼───────────┼────────┼────────┼────────────┼────────────┤
│   1   │ 2      │ Kali   │ community │ None   │ 1      │ 2024-11-07 │ 2024-11-07 │
│       │        │        │           │        │        │ 13:22:21   │ 13:22:21   │
├───────┼────────┼────────┼───────────┼────────┼────────┼────────────┼────────────┤
│   2   │ 3      │ Ubuntu │ community │ None   │ 1      │ 2024-11-07 │ 2024-11-07 │
│       │        │        │           │        │        │ 13:48:18   │ 13:48:18   │
├───────┼────────┼────────┼───────────┼────────┼────────┼────────────┼────────────┤
│   3   │ 4      │ Fedora │ community │ None   │ 1      │ 2024-11-07 │ 2024-11-07 │
│       │        │        │           │        │        │ 13:48:49   │ 13:48:49   │
└───────┴────────┴────────┴───────────┴────────┴────────┴────────────┴────────────┘
╭─[Smartwa@test.db]~[🕒16:55:56-💻00:00:03-⚡-3.9s] 
╰─>select * from 
                  select * from Linux  
                  select * from sqlite_schema
                  select * from sqlite_temp_schema



```
</details>

---

### Show-columns

- The `show-columns` command lists the columns for a particular table in the database.
<details open>

<summary><code>$ python manager.py show-columns --help </code></summary>

```
Usage: sqlite-manager show-columns [OPTIONS] DATABASE TABLE

  List columns for a particular table

Options:
  -j, --json  Stdout results in json format
  --help      Show this message and exit.
```

</details>

`$ python manager.py show-columns <path-to-sqlite3-database> <table-name>"`

> For example:
<details>
<summary><code>$ python manager.py show-columns test.db linux</code></summary>

```
┏━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Index ┃ Col. 1 ┃ Col. 2        ┃ Col. 3        ┃ Col. 4 ┃ Col. 5       ┃ Col. 6 ┃
┡━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│   0   │ 0      │ id            │ INTEGER       │ 0      │ None         │ 1      │
├───────┼────────┼───────────────┼───────────────┼────────┼──────────────┼────────┤
│   1   │ 1      │ distro        │ TEXT          │ 1      │ None         │ 0      │
├───────┼────────┼───────────────┼───────────────┼────────┼──────────────┼────────┤
│   2   │ 2      │ org           │ TEXT          │ 0      │ 'community'  │ 0      │
├───────┼────────┼───────────────┼───────────────┼────────┼──────────────┼────────┤
│   3   │ 3      │ logo          │ BLOB NULLABLE │ 0      │ None         │ 0      │
├───────┼────────┼───────────────┼───────────────┼────────┼──────────────┼────────┤
│   4   │ 4      │ is_maintained │ BOOLEAN       │ 0      │ 1            │ 0      │
├───────┼────────┼───────────────┼───────────────┼────────┼──────────────┼────────┤
│   5   │ 5      │ updated_on    │ TIMESTAMP     │ 0      │ CURRENT_TIM… │ 0      │
├───────┼────────┼───────────────┼───────────────┼────────┼──────────────┼────────┤
│   6   │ 6      │ created_at    │ TIMESTAMP     │ 1      │ CURRENT_TIM… │ 0      │
└───────┴────────┴───────────────┴───────────────┴────────┴──────────────┴────────┘
```
</details>

---

### Show-tables

- The `show-tables` command lists the available tables across the entire database.
<details open>

<summary><code>$ python manager.py show-tables --help </code></summary>

```
Usage: manager.py show-tables [OPTIONS] DATABASE

  List tables contained in the database

Options:
  -j, --json  Stdout results in json format
  --help      Show this message and exit.
```

</details>

`$ python manager.py show-tables <path-to-sqlite3-database>`

> For example:
<details>
<summary><code>$ python manager.py show-tables test.db</code></summary>

```
┏━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ Index ┃ Col. 1 ┃ Col. 2             ┃ Col. 3 ┃ Col. 4 ┃ Col. 5 ┃ Col. 6 ┃
┡━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩
│   0   │ main   │ sqlite_sequence    │ table  │ 2      │ 0      │ 0      │
├───────┼────────┼────────────────────┼────────┼────────┼────────┼────────┤
│   1   │ main   │ Linux              │ table  │ 7      │ 0      │ 0      │
├───────┼────────┼────────────────────┼────────┼────────┼────────┼────────┤
│   2   │ main   │ sqlite_schema      │ table  │ 5      │ 0      │ 0      │
├───────┼────────┼────────────────────┼────────┼────────┼────────┼────────┤
│   3   │ temp   │ sqlite_temp_schema │ table  │ 5      │ 0      │ 0      │
└───────┴────────┴────────────────────┴────────┴────────┴────────┴────────┘
```
</details>