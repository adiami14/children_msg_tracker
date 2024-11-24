import os
import mysql.connector
from datetime import datetime
import subprocess
import glob
from api_database import MySQLServer, DB_CONFIG, BACKUP_DIR

# Database configuration

class MySQLServerConfig(MySQLServer):
    """
    A wrapper for MySQL database operations, including connection management, table initialization,
    and backup/restore functionality.
    """
    def __init__(self, config):
        super().__init__(config)

    def create_database(self):
        """Create the database if it doesn't exist."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
            self.connection.close()
            print(f"Database '{self.config['database']}' created or already exists.")
        except Error as e:
            print("Error creating database:", e)
            raise

    def create_saved_messages_table(self):
        """Create the saved_messages table."""
        try:
            query = """
            CREATE TABLE IF NOT EXISTS saved_messages (
                chat_id VARCHAR(255),
                msg_id VARCHAR(255),
                body LONGTEXT,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor = self.connection.cursor()
            cursor.execute(query)
            print("Table 'saved_messages' created successfully.")
        except Error as e:
            print("Error creating table:", e)
            raise

    def backup_database(self):
        """Perform a backup of the database using mysqldump."""
        try:
            if not os.path.exists(config.BACKUP_DIR):
                os.makedirs(config.BACKUP_DIR)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(config.BACKUP_DIR, f"backup_{timestamp}.sql")

            command = [
                "mysqldump",
                "-u", self.config["user"],
                f"-p{self.config['password']}",
                self.config["database"],
                "--routines",
                "--triggers"
            ]

            with open(backup_file, "w") as outfile:
                subprocess.run(command, stdout=outfile, check=True)
            
            print(f"Backup created: {backup_file}")
        except Exception as e:
            print("Error creating backup:", e)
            raise

    def restore_from_backup(self):
        """Restore the database from the latest backup if it exists."""
        try:
            # Find the latest backup file
            backup_files = glob.glob(os.path.join(config.BACKUP_DIR, "*.sql"))
            if not backup_files:
                print("No backup files found.")
                return False
            
            latest_backup = max(backup_files, key=os.path.getctime)
            print(f"Restoring from backup: {latest_backup}")

            command = [
                "mysql",
                "-u", self.config["user"],
                f"-p{self.config['password']}",
                self.config["database"]
            ]

            with open(latest_backup, "r") as infile:
                subprocess.run(command, stdin=infile, check=True)
            
            print("Database restored successfully.")
            return True
        except Exception as e:
            print("Error restoring from backup:", e)
            return False
