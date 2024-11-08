#!/usr/bin/python3
import os
import re
import cmd
import sys
import time
import rich
import click
import sqlite3
import getpass
import datetime
import typing as t
from pathlib import Path
from colorama import Fore
from functools import wraps

# Rich
from rich.table import Table
from rich.console import Console
from rich.markdown import Markdown
from rich.console import Console

# prompt toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion, ThreadedCompleter

__version__ = "0.0.2"

__author__ = "Smartwa"

__repo__ = "https://github.com/Simatwa/sqlite3-cli-manager.git"

get_arg = lambda e: e.args[1] if e.args and len(e.args) > 1 else str(e)
"""An ugly anonymous function to extract exception message"""


def cli_error_handler(func):
    """Decorator for handling exceptions accordingly"""

    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            click.secho("> Error - " + get_arg(e), fg="red")

    return decorator


class Sqlite3Manager:
    """Perform CRUD operations on db"""

    def __init__(self, db_path: t.Union[str, Path], auto_commit: bool = False):
        """Initializes `Sqlite3Manager`

        Args:
            db_path (t.Union[str, Path]): Path leading to sqlite3 database.
            auto_commit(optional, bool): Commit automatically. Defaults to False.
        """
        self.db_path = db_path
        self.auto_commit = auto_commit
        self.db_connection = sqlite3.connect(db_path, autocommit=auto_commit)

    def execute_sql_command(
        self, statement: str, commit: bool = False
    ) -> t.Tuple[t.Any]:
        """Run sql statements against database"""
        try:
            cursor = sqlite3.Cursor(self.db_connection)
            cursor.execute(statement)
            if commit:
                self.commit()
            return (True, cursor.fetchall())
        except Exception as e:
            return (False, e)
        finally:
            cursor.close()

    def tables(self):
        """List tables available"""
        return self.execute_sql_command("PRAGMA table_list;")

    def table_columns(self, table: str):
        """List table columns and their metadata"""
        return self.execute_sql_command(f"PRAGMA table_info({table});")

    def schema(self):
        """Sqlite schema contents"""
        return self.execute_sql_command("SELECT * FROM sqlite_schema;")

    def commit(self):
        """Commit changes"""
        if self.db_connection and not self.auto_commit:
            self.db_connection.commit()

    def __call__(self, *args, **kwargs):
        return self.execute_sql_command(*args, **kwargs)

    def __enter__(self) -> "Sqlite3Manager":
        return self

    def __exit__(self) -> t.NoReturn:
        """Close db connection"""
        if self.db_connection:
            self.db_connection.close()


class TextToSql:
    """Generate SQL Statement based on given prompt"""

    def __init__(self, db_manager: Sqlite3Manager):
        """Initializes `TextToSql`"""
        try:
            import pytgpt.auto as auto
        except ImportError:
            raise Exception(
                "Looks like pytgpt isn't installed. Install it before using TextToSql - "
                '"pip install python-tgpt"'
            )
        self.ai = auto.AUTO(update_file=False)
        assert isinstance(
            db_manager, Sqlite3Manager
        ), f"db_manager must be an instance of {Sqlite3Manager} not {type(db_manager)}"
        self.db_manager = db_manager
        self.sql_pattern = r"\{([\w\W]*)\}"

    @property
    def context_prompt(self) -> str:
        _, table_schema = self.db_manager.execute_sql_command(
            """SELECT tbl_name, sql FROM sqlite_schema WHERE type='table'
            AND NOT tbl_name LIKE '%sqlite%';
            """
        )
        table_schema_text = "\n".join(
            [tbl_schema[0] + " - " + tbl_schema[1] for tbl_schema in table_schema]
        )
        prompt = (
            (
                """You're going to act like TEXT to SQL translater.
        Action to be performed on the sqlite3 database will be provided and then
        you will generate a complete SQL statement for accomplishing the same.
        Enclose the sql statement in curly braces '{}'. DO NOT ADD ANY OTHER TEXT
        EXCEPT when seeking clarification or confirmation.

        Given below are the database table names and the SQL statements used to create them:
        \n"""
            )
            + "\n    "
            + table_schema_text
            + (
                """
        \n
        For example:
        User: List top 10 entries in the Linux table where distro contains letter 'a'LLM : {SELECT * FROM Linux WHERE distro LIKE '%a%';}

        User : Remove entries from table Linux whose id is greater than 10.
        LLLM : {DELETE * FROM Linux WHERE id > 10;}

        If the user's request IS UNDOUBTEDBLY INCOMPLETE, seek clarification.
        For example:
        User: Add column to Linux table.
        LLM: What kind of data will be stored in the column and suggest column name if possible?
        User: The column will be storing maintainance status of the linux distros.
        LLM: {ALTER TABLE Linux ADD COLUMN is_maintained BOOLEAN;}

        If the user's request can be disastrous then seek clarification or confirmation accordingly.
        These actions might include DELETE, ALTER and DROP.
        """
            )
        )

        return prompt

    def process_response(self, response: str) -> list[str]:
        """Tries to extract the sql statement from ai response

        Args:
            response (str): ai response
        """
        if response.startswith("{") and not response.strip().endswith("}"):
            response += "}"

        sql_statements = re.findall(self.sql_pattern, response)
        if sql_statements:
            return [sql for sql in re.split(";", sql_statements[0]) if sql]
        else:
            Console().print(Markdown(response))
            return []

    def generate(self, prompt: str):
        """Main method"""
        self.ai.intro = self.context_prompt
        assert prompt, f"Prompt cannot be null!"
        return self.process_response(self.ai.chat(prompt))


class HistoryCompletions(Completer):
    def __init__(self, session, disable_suggestions):
        self.session: PromptSession = session
        self.disable_suggestions = disable_suggestions

    def get_completions(self, document: Document, complete_event):
        if self.disable_suggestions:
            return
        text = document.text
        history = self.session.history.get_strings()
        for entry in reversed(list(set(history))):
            if entry.startswith(text):
                yield Completion(entry, start_position=-len(text))


class Interactive(cmd.Cmd):
    intro = (
        "Welcome to interactive sqlite3-db manager.\n"
        "Run help or h <command> for usage info.\n"
        "Repository : https://github.com/Simatwa/sqlite3-cli-manager"
    )
    __init_time = time.time()

    def __init__(
        self,
        db_path,
        auto_commit,
        disable_coloring,
        disable_suggestions,
        new_history_thread,
        json,
        yes,
        color,
        ai,
    ):
        super().__init__()
        self.__start_time = time.time()
        self.__end_time = time.time()
        self.db_manager = Sqlite3Manager(db_path, auto_commit)
        self.disable_coloring = disable_coloring
        self.json = json
        self.yes = yes
        self.color = color
        history_file_path = Path.home() / ".sqlite3-cli-manager-history.txt"
        if new_history_thread and history_file_path.exists():
            os.remove(history_file_path)
        history = FileHistory(history_file_path)
        self.completer_session = PromptSession(history=history)
        self.completer_session.completer = ThreadedCompleter(
            HistoryCompletions(self.completer_session, disable_suggestions)
        )
        self.ai = ai
        if self.ai:
            self.text_to_sql = TextToSql(self.db_manager)

    @property
    def prompt(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        def find_range(start, end, hms: bool = False):
            in_seconds = round(end - start, 1)
            return (
                str(datetime.timedelta(seconds=in_seconds)).split(".")[0].zfill(8)
                if hms
                else in_seconds
            )

        if not self.disable_coloring:
            cmd_prompt = (
                f"╭─[`{Fore.CYAN}{getpass.getuser().capitalize()}@localhost]`"
                f"(`{Fore.MAGENTA}{self.db_manager.db_path})`"
                f"~[`{Fore.LIGHTWHITE_EX}🕒{Fore.BLUE}{current_time}-`"
                f"{Fore.LIGHTWHITE_EX}💻{Fore.RED}{find_range(self.__init_time, time.time(), True)}-`"
                f"{Fore.LIGHTWHITE_EX}⚡{Fore.YELLOW}{find_range(self.__start_time, self.__end_time)}s]`"
            )
            whitelist = ["[", "]", "~", "-", "(", ")"]
            for character in whitelist:
                cmd_prompt = cmd_prompt.replace(character + "`", Fore.RESET + character)
            return cmd_prompt

        else:
            return (
                f"╭─[{getpass.getuser().capitalize()}@localhost]"
                f"({self.db_manager.db_path})"
                f"~[🕒{current_time}"
                f"-💻{find_range(self.__init_time, time.time(), True)}"
                f"-⚡{find_range(self.__start_time, self.__end_time)}s]"
            )

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        """

        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline

                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                if hasattr(readline, "backend") and readline.backend == "editline":
                    if self.completekey == "tab":
                        # libedit uses "^I" instead of "tab"
                        command_string = "bind ^I rl_complete"
                    else:
                        command_string = f"bind {self.completekey} rl_complete"
                else:
                    command_string = f"{self.completekey}: complete"
                readline.parse_and_bind(command_string)
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            print(self.prompt, end="")
                            line = self.completer_session.prompt("\n╰─>")
                        except EOFError:
                            line = "EOF"
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = "EOF"
                        else:
                            line = line.rstrip("\r\n")
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline

                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    def do_clear(self, line):
        """Clear console"""
        sys.stdout.write("\u001b[2J\u001b[H")
        sys.stdout.flush()

    def do_h(self, line):
        """Show help info in tabular form"""
        table = Table(
            title="Help info",
            show_lines=True,
        )
        table.add_column("No.", style="white", justify="center")
        table.add_column("Command", style="yellow", justify="left")
        table.add_column("Function", style="cyan")
        command_methods = [
            getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method)) and method.startswith("do_")
        ]
        command_methods.append(self.default)
        command_methods.reverse()
        for no, method in enumerate(command_methods):
            table.add_row(
                str(no + 1),
                method.__name__[3:] if not method == self.default else method.__name__,
                method.__doc__,
            )
        Console().print(table)

    def do_sys(self, line):
        """Execute system commands
        shortcut [./<command>]
        Usage:
            sys <System command>
                  or
             ./<System command>
        """
        os.system(line)

    def do_sql(self, line):
        """Execute sql statement"""
        self.default("/sql " + line)

    def do_ai(self, line):
        """Generate sql statements with AI and execute"""
        self.default("/ai " + line)

    @cli_error_handler
    def do_schema(self, line):
        """Show database schema"""
        success, tables = self.db_manager.schema()
        Commands.stdout_data(success, tables, json=self.json, color=self.color)

    @cli_error_handler
    def do_tables(self, line):
        """Show database tables"""
        success, tables = self.db_manager.tables()
        Commands.stdout_data(success, tables, json=self.json, color=self.color)

    @cli_error_handler
    def do_columns(self, line):
        """Show columns for a particular table
        Usage:
            columns <table-name>"""
        if line:
            success, tables = self.db_manager.table_columns(line)
            Commands.stdout_data(success, tables, json=self.json, color=self.color)
        else:
            click.secho("Table name is required.", fg="yellow")

    @cli_error_handler
    def default(self, line: str, prompt_confirmation: bool = False, ai_generated=False):
        """Run sql statemnt against database"""

        if line.startswith("./"):
            self.do_sys(line[2:])
            return

        elif line.startswith("!"):
            # Let's try to mimic the unix' previous command(s) execution shortcut
            history = self.completer_session.history.get_strings()
            command_number = line.count("!")
            if len(history) >= command_number:
                line = [history[-command_number - 1]]
                prompt_confirmation = True
            else:
                click.secho("Index out of range!", fg="yellow")
                return

        elif line.startswith("/sql"):
            line = [line[4:]]
        elif line.startswith("/ai"):
            line = TextToSql(self.db_manager).generate(line[3:])
            ai_generated = prompt_confirmation = True
        elif self.ai:
            line = self.text_to_sql.generate(line)
            ai_generated = prompt_confirmation = True
        else:
            line = [line]
        self.__start_time = time.time()
        for sql_statement in line:
            if (
                not self.yes
                and prompt_confirmation
                and not click.confirm("[Exc] - " + sql_statement)
            ):
                continue
            if ai_generated:
                self.completer_session.history.append_string(sql_statement)
            success, response = self.db_manager.execute_sql_command(sql_statement)
            Commands.stdout_data(success, response, json=self.json, color=self.color)
        self.__end_time = time.time()

    def do_exit(self, line):
        """Quit this program"""
        if click.confirm("Are you sure to exit"):
            click.secho("^-^ Okay Goodbye!", fg="yellow")
            return True


class Commands:

    @staticmethod
    def stdout_data(
        success: bool,
        data: t.List[t.Tuple[t.Any]],
        color: str = "cyan",
        title: str = None,
        json: bool = False,
    ):
        """Stdout info.

        Args:
            data (t.List[t.Tuple[t.Any]]):
            color (str, optional):. Defaults to 'cyan'.
            title (str, optional): Table title. Defaults to None.
            json (bool, optional): Output in Json format. Defaults to False.
        """

        if not success:
            raise data

        elif data and data[0]:
            if json:
                entry_items = {}
                for index, entry in enumerate(data):
                    entry_items[index] = entry
                rich.print_json(data=entry_items)
                return

            table = Table(title=title, show_lines=True, show_header=True, style=color)
            ref_data = data[0]
            table.add_column("Index", justify="center")
            for x in range(len(ref_data)):
                table.add_column(f"Col. {x+1}")
            for index, entry in enumerate(data):
                table.add_row(*[str(index)] + [str(token) for token in entry])
            rich.print(table)

    @staticmethod
    @click.command()
    @click.argument(
        "database", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
    )
    @click.option("-j", "--json", is_flag=True, help="Stdout results in json format")
    def show_tables(database, json):
        """List tables contained in the database"""
        db_manager = Sqlite3Manager(database)
        success, tables = db_manager.tables()
        Commands.stdout_data(success, tables, json=json)

    @staticmethod
    @click.command()
    @click.argument(
        "database", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
    )
    @click.argument("table")
    @click.option("-j", "--json", is_flag=True, help="Stdout results in json format")
    def show_columns(database, table, json):
        """List columns for a particular table"""
        db_manager = Sqlite3Manager(database)
        success, tables = db_manager.table_columns(table)
        Commands.stdout_data(success, tables, json=json)

    @staticmethod
    @click.command()
    @click.argument(
        "database", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
    )
    @click.option("-s", "--sql", multiple=True, help="Sql statements", required=True)
    @click.option(
        "-i", "--ai", is_flag=True, help="Generate sql statements from prompt by AI"
    )
    @click.option("-j", "--json", is_flag=True, help="Stdout results in json format")
    @click.option("-q", "--quiet", is_flag=True, help="Do not stdout results")
    def execute(database, sql, ai, json, quiet):
        """Run sql statements against database [AUTO-COMMITS]"""
        db_manager = Sqlite3Manager(database, auto_commit=True)
        if ai:
            text_to_sql = TextToSql(db_manager)
            ai_gen_sql_statements = []
            for prompt in sql:
                ai_gen_sql_statements.extend(text_to_sql.generate(prompt))

        for sql_statement in sql if not ai else ai_gen_sql_statements:
            success, tables = db_manager.execute_sql_command(sql_statement)
            if not quiet:
                Commands.stdout_data(success, tables, json=json)

    @staticmethod
    @click.command()
    @click.argument("database", type=click.Path(exists=True, dir_okay=False))
    @click.option(
        "-c",
        "--color",
        help="Results font color",
        default="cyan",
    )
    @click.option("-j", "--json", help="Stdout results in json format", is_flag=True)
    @click.option(
        "-y",
        "--yes",
        help="Okay to execution of AI generated sql statements",
        is_flag=True,
    )
    @click.option("-a", "--auto-commit", is_flag=True, help="Enable auto-commit")
    @click.option(
        "-i", "--ai", is_flag=True, help="Generate sql statements from prompt by AI"
    )
    @click.option(
        "-C",
        "--disable-coloring",
        is_flag=True,
        help="Stdout prompt text in white font color",
    )
    @click.option(
        "-S",
        "--disable-suggestions",
        is_flag=True,
        help="Do not suggest sql statements",
    )
    @click.option(
        "-N", "--new-history-thread", is_flag=True, help="Start a new history thread"
    )
    def interactive(
        database,
        color,
        json,
        yes,
        auto_commit,
        ai,
        disable_coloring,
        disable_suggestions,
        new_history_thread,
    ):
        """Execute sql statements interactively"""
        main = Interactive(
            db_path=database,
            auto_commit=auto_commit,
            disable_coloring=disable_coloring,
            disable_suggestions=disable_suggestions,
            new_history_thread=new_history_thread,
            json=json,
            yes=yes,
            color=color,
            ai=ai,
        )
        main.cmdloop()

    @staticmethod
    def build_commands() -> object:
        @click.group()
        @click.version_option(version=__version__)
        def db_manager():
            """Interact with SQLite databases via command-line interface"""
            pass

        db_manager.add_command(Commands.show_tables)
        db_manager.add_command(Commands.show_columns)
        db_manager.add_command(Commands.execute)
        db_manager.add_command(Commands.interactive)
        return db_manager


if __name__ == "__main__":
    try:
        Commands.build_commands()()
    except Exception as e:
        print("> Error : ", get_arg(e), "\nQuitting!")
        sys.exit(1)
