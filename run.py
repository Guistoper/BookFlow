from database.scripts import MySQLScriptRunner
from database.security import PasswordGenerator
from database.server import MySQLInstallerWindows
from database.server import MySQLConnect
from database.uncrypto import PasswordReader
from assets.login import BookFlowLogin

class BookFlow:
    def _main():
        if not MySQLInstallerWindows._check_mysql_installed() or not PasswordGenerator._check_password_file():
            MySQLInstallerWindows._main()
        unc_password = PasswordReader.get_mysql_password()
        if not MySQLScriptRunner._check_database(unc_password, "bookflow"):
            MySQLScriptRunner._main()
        MySQLConnect._get_connection(unc_password, "bookflow")
        BookFlowLogin()

if __name__ == "__main__":
    BookFlow._main()