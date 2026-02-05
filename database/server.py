from database.security import PasswordGenerator
from database.uncrypto import PasswordReader
from dotenv import load_dotenv
import time
import subprocess
import os
import ctypes

class MySQLInstallerWindows:
    def __is_admin():
        # checa se o script está rodando como administrador
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def _check_mysql_installed():
        # tenta rodar o comando 'mysql --version' para ver se existe
        # TENTATIVA 1: via comando no PATH
        try:
            # o parâmetro shell=True permite encontrar o comando no PATH do Windows
            result = subprocess.run("mysql --version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"DEBUG: MySQL já está instalado ({result.stdout.strip()})")
                return True
        except:
            pass
        # TENTATIVA 2: verificar em caminhos comuns de instalação
        common_paths = [r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe", r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe"]
        for path in common_paths:
            if os.path.exists(path):
                print(f"DEBUG: MySQL encontrado fisicamente em {path}")
                return True
        return False
    
    def __run_uninstaller():
        # tenta rodar o desinstalador do MySQL Installer para remover instalações anteriores
        print("DEBUG: Verificando se há instalações anteriores do MySQL Installer para remover...")
        installer_console = r"C:\Program Files (x86)\MySQL\MySQL Installer for Windows\MySQLInstallerConsole.exe"
        if os.path.exists(installer_console):
            try:
                print("DEBUG: Instalador encontrado. Tentando limpar produtos MySQL existentes...")
                # comando para remover todos (*) os produtos da versão community silenciosamente
                uninstall_cmd = [installer_console, "community", "remove", "*", "--silent"]
                subprocess.run(uninstall_cmd, check=True)
                print("DEBUG: Produtos anteriores removidos com sucesso.")
            except subprocess.CalledProcessError as e:
                # apenas loga o erro e segue, caso a desinstalação falhe ou não haja nada para remover
                print(f"DEBUG: Falha ou nada a remover no processo de desinstalação ({e})")
        else:
            print("DEBUG: O MySQLInstallerConsole não foi encontrado. Nada a desinstalar.")

    def __run_installer(root_password):
        # executa o instalador MSI
        print("DEBUG: Iniciando o instalador...")
        # 1. caminho do instalador MSI
        msi_path = os.path.join("database\data", "windows-mysql-web-installer.msi")
        try:
            # ETAPA 1: instalar o MySQL Installer
            # usamos /qn para ser totalmente silencioso
            print("DEBUG: Instalando o gerenciador MySQL Installer...")
            subprocess.run(["msiexec", "/i", msi_path, "/qn"], check=True)
            # aguarda um momento para o Windows registrar o executável
            time.sleep(5) 
            # localiza o Console do Instalador
            installer_console = r"C:\Program Files (x86)\MySQL\MySQL Installer for Windows\MySQLInstallerConsole.exe"
            if not os.path.exists(installer_console):
                print("DEBUG: O MySQLInstallerConsole não foi encontrado.")
                return False
            # definições de versão (mantivemos a mesma para Server e Workbench para evitar conflito)
            target_version = "8.0.44"
            target_arch = "x64"
            # ETAPA 2: instalar o MySQL Server
            print("DEBUG: Configurando o Servidor MySQL e definindo senha...")
            product_name = "server" 
            # configuração do server exige a senha e liberação de firewall
            server_config = (f"{product_name};{target_version};{target_arch}:*:type=main;open_windows_firewall=true;"f"root_password={root_password}")
            install_server_cmd = [installer_console, "community", "install", server_config, "--silent"]
            subprocess.run(install_server_cmd, check=True)
            print("DEBUG: Servidor instalado e configurado com sucesso.")
            # ETAPA 3: instalar o MySQL Workbench (opcional)
            print("DEBUG: Verificando preferência de instalação do Workbench...")
            # pergunta ao usuário se deseja instalar o Workbench
            confirm = input("DEBUG: Deseja instalar o MySQL Workbench? (S/N): ").strip().upper()
            if confirm in ['S', 'SIM', 'Y', 'YES']:
                print("DEBUG: Instalando MySQL Workbench...")
                # o Workbench não precisa de configuração de senha, apenas instalar
                workbench_config = f"workbench;{target_version};{target_arch}"
                install_wb_cmd = [installer_console, "community", "install", workbench_config, "--silent"]
                subprocess.run(install_wb_cmd, check=True)
                print("DEBUG: MySQL Workbench instalado com sucesso.")
            else:
                print("DEBUG: Instalação do MySQL Workbench ignorada pelo usuário.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"DEBUG: Erro durante o processo de instalação ({e})")
            return False

    def _main():
        print("DEBUG: Iniciando verificação de instalação do MySQL...")
        # verifica se já tem a senha root gerada
        if not PasswordGenerator._check_password_file():
            print("DEBUG: Arquivo de senha não encontrado.")
            # lógica de reinstalação: Se não tem arquivo de senha, mas o MySQL existe,
            # forçamos a desinstalação para evitar conflito de credenciais perdidas.
            if MySQLInstallerWindows._check_mysql_installed():
                # checa se o terminal é CMD/PowerShell com privilégios de administrador antes de tentar desinstalar
                if not MySQLInstallerWindows.__is_admin():
                    print("DEBUG: Este Terminal/CMD não está como Administrador.")
                    return
                print("DEBUG: MySQL instalado sem arquivo de senha.")
                print("DEBUG: Executando desinstalação prévia para redefinir o ambiente...")
                MySQLInstallerWindows.__run_uninstaller()
            print("DEBUG: Iniciando gerador de senha...")
            PasswordGenerator._main()
        # carrega a senha do arquivo mysql.env específico e já descriptografa ela
        unc_password = PasswordReader.get_mysql_password()
        MySQLInstallerWindows.__run_installer(unc_password)
        print("DEBUG: Encerrando o instalador...")

if __name__ == "__main__":
    MySQLInstallerWindows._main()