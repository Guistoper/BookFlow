from database.scripts import MySQLScriptRunner
from database.security import PasswordGenerator
from database.server import MySQLInstallerWindows
from database.uncrypto import PasswordReader

class RunApp:
    def _main():
        if not MySQLInstallerWindows._check_mysql_installed() or not PasswordGenerator._check_password_file():
            MySQLInstallerWindows._main()
        unc_password = PasswordReader.get_mysql_password()
        if not MySQLScriptRunner._check_database(unc_password, "biblioteca"):
            MySQLScriptRunner._main()

if __name__ == "__main__":
    RunApp._main()