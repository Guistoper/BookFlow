from database.security import PasswordGenerator
from database.uncrypto import PasswordReader
from dotenv import load_dotenv
import mysql.connector
import time
import subprocess
import os
import ctypes

class MySQLInstallerWindows:
    def __is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            print("SERVER: Este Terminal/CMD não está como Administrador.")
            return False

    def _check_mysql_installed():
        print("SERVER: Iniciando verificação de instalação do MySQL...")
        try:
            # tenta executar o comando 'mysql --version' para verificar se o MySQL está no PATH
            result = subprocess.run("mysql --version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"SERVER: MySQL instalado ({result.stdout.strip()})")
                return True
        except:
            # ignorar erros, pois o comando pode falhar se o MySQL não estiver no PATH
            pass
        # verificação alternativa: procura por executáveis comuns do MySQL em locais típicos de instalação no Windows
        common_paths = [r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe", r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe"]
        for path in common_paths:
            if os.path.exists(path):
                print(f"SERVER: MySQL instalado ({path})")
                return True
        return False
    
    def __run_uninstaller():
        print("SERVER: Iniciando verificação de versões anteriores do MySQLInstaller para remover...")
        installer_console = r"C:\Program Files (x86)\MySQL\MySQL Installer for Windows\MySQLInstallerConsole.exe"
        if os.path.exists(installer_console):
            try:
                print("SERVER: Tentando limpar produtos MySQL existentes...")
                # comando de desinstalação do MySQL Installer para remover todos os produtos MySQL instalados
                uninstall_cmd = [installer_console, "community", "remove", "*", "--silent"]
                subprocess.run(uninstall_cmd, check=True)
                print("SERVER: Produtos anteriores removidos com sucesso.")
            except subprocess.CalledProcessError as e:
                print(f"SERVER: Erro ({e})")
        else:
            print("SERVER: O MySQLInstallerConsole não foi encontrado.")

    def __run_installer(root_password):
        print("SERVER: Iniciando a instalação dos produtos MySQL...")
        # caminho do instalador MSI (certifique que o arquivo exista nesse caminho)
        msi_path = os.path.join("database", "data", "windows-mysql-web-installer.msi")
        try:
            print("SERVER: Instalando o gerenciador MySQL Installer...")
            # instala o MySQL Installer usando o MSI baixado
            subprocess.run(["msiexec", "/i", msi_path, "/qn"], check=True)
            # espera um pouco para garantir que o instalador esteja pronto para uso
            time.sleep(5)
            # configura o MySQL Server usando o MySQL Installer Console
            installer_console = r"C:\Program Files (x86)\MySQL\MySQL Installer for Windows\MySQLInstallerConsole.exe"
            if not os.path.exists(installer_console):
                print("SERVER: O MySQLInstallerConsole não foi encontrado.")
                return False
            # configurações para instalação do MySQL Server e MySQL Workbench
            target_version = "8.0.44"
            target_arch = "x64"
            print("SERVER: Configurando o MySQL Server...")
            product_name = "server"
            # configuração do produto para instalação silenciosa
            server_config = (f"{product_name};{target_version};{target_arch}:*:type=main;open_windows_firewall=true;"f"root_password={root_password}")
            install_server_cmd = [installer_console, "community", "install", server_config, "--silent"]
            # executa o comando de instalação do MySQL Server
            subprocess.run(install_server_cmd, check=True)
            print("SERVER: MySQL Server instalado e configurado com sucesso.")
            # pergunta ao usuário se deseja instalar o MySQL Workbench
            confirm = input("SERVER: Deseja instalar o MySQL Workbench? (S/N): ").strip().upper()
            if confirm in ['S', 'SIM', 'Y', 'YES']:
                print("SERVER: Instalando MySQL Workbench...")
                # configuração do produto para instalação silenciosa do MySQL Workbench (mesma versão do Server para compatibilidade)
                workbench_config = f"workbench;{target_version};{target_arch}"
                install_wb_cmd = [installer_console, "community", "install", workbench_config, "--silent"]
                # executa o comando de instalação do MySQL Workbench
                subprocess.run(install_wb_cmd, check=True)
                print("SERVER: MySQL Workbench instalado com sucesso.")
            else:
                print("SERVER: Instalação do MySQL Workbench ignorada pelo usuário.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"SERVER: Erro ({e})")
            return False

    def _main():
        # verifica se o MySQL está instalado e se os arquivos de senha e chave existem; se não, executa a instalação
        if not PasswordGenerator._check_password_file() or not PasswordGenerator._check_password_secret():
            if MySQLInstallerWindows._check_mysql_installed():
                if not MySQLInstallerWindows.__is_admin():
                    return
                print("SERVER: MySQL instalado sem arquivo de senha ou chave de criptografia.")
                print("SERVER: Executando desinstalação prévia para redefinir o ambiente...")
                MySQLInstallerWindows.__run_uninstaller()
            PasswordGenerator._main()
        unc_password = PasswordReader._get_mysql_password()
        MySQLInstallerWindows.__run_installer(unc_password)

class MySQLConnect:
    # tenta conectar com o MySQL Server usando as credenciais fornecidas
    def _get_connection(password, database):
        try:
            cnx = mysql.connector.connect(
                user='root',
                password=password,
                host='localhost',
                database=database,
                auth_plugin='mysql_native_password'
            )
            return cnx
        except mysql.connector.Error as err:
            print(f"SERVER: Erro ({err})")
            return None