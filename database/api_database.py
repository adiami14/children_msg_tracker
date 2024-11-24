import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "test_db"
}

BACKUP_DIR = "./db_backups"

class MySQLServer:
    """
    A wrapper for MySQL database operations, including connection management and CRUD operations.
    """

    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        """Establish a connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print("MySQL database connected.")
                self.connection.set_charset_collation(charset="utf8mb4", collation="utf8mb4_general_ci")
        except Error as e:
            print("Error connecting to MySQL:", e)
            raise

    def get_data(self, table_name):
        """Retrieve all data from a specified table."""
        try:
            query = f"SELECT * FROM `{table_name}`"
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print("Error retrieving data:", e)
            raise

    def insert_data(self, table_name, data):
        """Insert a record into a specified table."""
        try:
            keys = ', '.join(f"`{key}`" for key in data.keys())
            values = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO `{table_name}` ({keys}) VALUES ({values})"
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print("Error inserting data:", e)
            raise

    def update_data(self, table_name, data, where_clause):
        """Update records in a specified table."""
        try:
            set_clause = ', '.join([f"`{key}`=%s" for key in data.keys()])
            query = f"UPDATE `{table_name}` SET {set_clause} WHERE {where_clause}"
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print("Error updating data:", e)
            raise

    def delete_data(self, table_name, where_clause, params=None):
        """Delete records from a specified table."""
        try:
            query = f"DELETE FROM `{table_name}` WHERE {where_clause}"
            cursor = self.connection.cursor()
            cursor.execute(query, params if params else ())
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print("Error deleting data:", e)
            raise

    def free_query(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            return cursor.fetchall()
        except Error as e:
            print("Error deleting data:", e)
            raise
