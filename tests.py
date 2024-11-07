import unittest
import typing as t
from os import remove
from pathlib import Path
from manager import Sqlite3Manager


class TestSqlite3(unittest.TestCase):
    create_table_sql_statement = """
    CREATE TABLE IF NOT EXISTS Linux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            distro TEXT UNIQUE NOT NULL,
            org TEXT DEFAULT 'community',
            logo BLOB NULLABLE,
            is_maintained BOOLEAN DEFAULT 1,
            updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """

    def setUp(self):
        self.db_path = Path("test.db")
        self.sqlite3_manager = Sqlite3Manager(self.db_path, auto_commit=True)

    def test_execute_sql_statements(self):
        success, feedback = self.sqlite3_manager.execute_sql_command(
            self.create_table_sql_statement
        )
        self.assertTrue(success)
        self.assertIsInstance(feedback, t.Iterable)

    def test_tables_listing(self):
        self.sqlite3_manager.execute_sql_command(self.create_table_sql_statement)
        success, feedback = self.sqlite3_manager.tables()
        self.assertTrue(success)
        self.assertIsInstance(feedback, t.Iterable)

    def test_table_columns_listing(self):
        self.sqlite3_manager.execute_sql_command(self.create_table_sql_statement)
        success, feedback = self.sqlite3_manager.table_columns("Linux")
        self.assertTrue(success)
        self.assertIsInstance(feedback, t.Iterable)

    def tearDown(self):
        if self.db_path.exists():
            remove(self.db_path)
        self.sqlite3_manager.__exit__()


if __name__ == "__main__":
    unittest.main()
