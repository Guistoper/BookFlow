import mysql.connector
import os

class Install:
    __sql = mysql.connector.connect(
            user="root",
            password="admin",
            host="localhost",
    )
    def __run_scripts(directory):
        try:
            cursor = Install.__sql.cursor()
            files = sorted(f for f in os.listdir(directory) if f.endswith(".sql"))
            for filename in files:
                path = os.path.join(directory, filename)
                with open(path, "r", encoding="utf-8") as f:
                    sql_content = f.read()
                for statement in sql_content.split(";"):
                    stmt = statement.strip()
                    if stmt:
                        cursor.execute(stmt)
        except mysql.connector.Error as err:
            print(f"Error\n{err}")
        except Exception as e:
            print(f"Error\n{e}")
    def __check_database(database):
        try:
            cursor = Install.__sql.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            return database in databases
        except mysql.connector.Error as err:
            print(f"Error\n{err}")
        except Exception as e:
            print(f"Error\n{e}")
    def main(database):
        try:
            if Install.__check_database(database) == True:
                print(f"Database '{database}' found.")
                print("Skipping install...")
                return database
            else:
                print(f"Database '{database}' not found")
                print("Starting install...")
                Install.__run_scripts(directory="Banco-Dados-Biblioteca/scripts")
                Install.__sql.commit()
                print("Scripts ran successfully!")
                print("Stopping install...")          
                return database
        except mysql.connector.Error as err:
            print(f"Error\n{err}")
        except Exception as e:
            print(f"Error\n{e}")