import sqlite3
import logging, yaml, sys
# sys.path.append('/home/adiami/check_for_deleted/')
from typing import Any, Dict, List, Optional
from pprint import pprint

CONFIG_FILE_PATH = '/config/configuration.yaml'

def load_config(file_path: str):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

class SQLiteWrapper:
    def __init__(self):
        """
        Initialize the SQLiteWrapper instance.
        :param db_path: Path to the SQLite database file.
        """
        config = load_config(CONFIG_FILE_PATH)
        self.db_cofig = config['database']
        self.whatsapp_cofig = config['whatsapp']
        self.last_msgs_from_me = []
        
    def _connect(self) -> sqlite3.Connection:
        """
        Establish a connection to the SQLite database.
        :return: SQLite connection object.
        """
        try:
            conn = sqlite3.connect(self.db_cofig['file_path'])
            conn.row_factory = sqlite3.Row  # Ensure rows are dictionary-like
            return conn
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def fetch_all(self, table_name: str) -> List[Dict[str, Optional[Any]]]:
        """
        Fetch all rows from a given table and return them as a list of dictionaries.
        :param table_name: Name of the table to fetch data from.
        :return: A list of dictionaries containing all rows from the table.
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                query = f"SELECT * FROM {table_name}"
                cursor.execute(query)
                rows = cursor.fetchall()
                result = [{key: row[key] for key in row.keys()} for row in rows]
                logging.info(f"Fetched all rows from table '{table_name}': {result}")
                return result
        except sqlite3.Error as e:
            logging.error(f"Error fetching data from table '{table_name}': {e}")
            return []

    def fetch_one(self, table_name: str, where_clause: str, params: tuple) -> Optional[Dict[str, Optional[Any]]]:
        """
        Fetch a single row from a given table and return it as a dictionary.
        :param table_name: Name of the table to fetch data from.
        :param where_clause: SQL WHERE clause (e.g., "column = ?").
        :param params: Tuple of parameters for the WHERE clause.
        :return: A dictionary containing the row data, or None if no row matches.
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                query = f"SELECT * FROM {table_name} WHERE {where_clause}"
                cursor.execute(query, params)
                row = cursor.fetchone()
                result = {key: row[key] for key in row.keys()} if row else None
                logging.info(f"Fetched row from table '{table_name}' with condition '{where_clause}': {result}")
                return result
        except sqlite3.Error as e:
            logging.error(f"Error fetching row from table '{table_name}' with condition '{where_clause}': {e}")
            return None

    def insert(self, table_name: str, data: Dict[str, Any]) -> bool:
        """
        Insert a new record into a table.
        :param table_name: Name of the table to insert data into.
        :param data: A dictionary where keys are column names and values are the values to insert.
        :return: True if the operation succeeds, False otherwise.
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?'] * len(data))
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(query, tuple(data.values()))
                conn.commit()
                logging.info(f"Inserted data into table '{table_name}': {data}")
                return True
        except sqlite3.Error as e:
            logging.error(f"Error inserting data into table '{table_name}': {e}")
            return False

    def update(self, table_name: str, data: Dict[str, Any], where_clause: str, params: tuple) -> bool:
        """
        Update existing records in a table.
        :param table_name: Name of the table to update data in.
        :param data: A dictionary where keys are column names and values are the new values.
        :param where_clause: SQL WHERE clause to filter the rows to update.
        :param params: Tuple of parameters for the WHERE clause.
        :return: True if the operation succeeds, False otherwise.
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                updates = ', '.join([f"{col} = ?" for col in data.keys()])
                query = f"UPDATE {table_name} SET {updates} WHERE {where_clause}"
                print(query)
                cursor.execute(query, tuple(data.values()) + params)
                conn.commit()
                logging.info(f"Updated table '{table_name}' with data {data} where {where_clause}")
                return True
        except sqlite3.Error as e:
            logging.error(f"Error updating table '{table_name}': {e}")
            return False

    def delete(self, table_name: str, where_clause: str) -> bool:
        """
        Delete records from a table based on a condition.
        :param table_name: Name of the table to delete data from.
        :param where_clause: SQL WHERE clause to filter the rows to delete.
        :param params: Tuple of parameters for the WHERE clause.
        :return: True if the operation succeeds, False otherwise.
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                query = f"DELETE FROM {table_name} WHERE {where_clause}"
                cursor.execute(query)
                conn.commit()
                logging.info(f"Deleted rows from table '{table_name}' where {where_clause}")
                return True
        except sqlite3.Error as e:
            logging.error(f"Error deleting from table '{table_name}': {e}")
            return False

    def free_query(self, query, fetch=False):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                if fetch:
                    rows = cursor.fetchall()
                    result = [{key: row[key] for key in row.keys()} for row in rows]
                    logging.info(f"Fetched all from free quey")
                    return result
                else: return True
        except sqlite3.Error as e:
            logging.error(f"Error initializing database: {e}")
            return False
if __name__ == "__main__":
    data = """
    CREATE TABLE IF NOT EXISTS saved_messages (
        chat_id VARCHAR(255),
        msg_id VARCHAR(255),
        body TEXT,
        is_group tinyint(1),
        group_name VARCHAR(255),
        user_name VARCHAR(255),
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    # db = SQLiteWrapper()
    # db.free_query(data)
    # # db.delete("saved_messages", "msg_id=31")
    # # db.insert("saved_messages", {"chat_id": """Alic,"דגכ,"e""", "msg_id": '30'})
    # data = db.fetch_all("saved_messages")
    # # pprint(data)
    # # db.update("saved_messages", {"msg_id": '31'}, "chat_id = ?", ('Alic,"דגכ,"e',))
    # # data = db.fetch_all("saved_messages")
    # pprint(data)
    
    config = load_config("/config/configuration.yaml")
    pprint(config)