from security import PasswordGenerator
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
        print("DEBUG: Verificando se o MySQL está instalado...")
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
        print("DEBUG: MySQL não foi encontrado nem no PATH e nem nas pastas padrão.")
        return False

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
            # definições de versão (mantive a mesma para Server e Workbench para evitar conflito)
            target_version = "8.0.44"
            target_arch = "x64"
            # ETAPA 2: instalar o MySQL Server
            print("DEBUG: Configurando o Servidor MySQL e definindo senha...")
            product_name = "server" 
            # configuração do server exige a senha e liberação de firewall
            server_config = (f"{product_name};{target_version};{target_arch}:*:type=main;open_windows_firewall=true;"f"root_password={root_password}")
            install_server_cmd = [installer_console, "community", "install", server_config, "-silent"]
            subprocess.run(install_server_cmd, check=True)
            print("DEBUG: Servidor instalado e configurado com sucesso.")
            # ETAPA 3: Instalar o MySQL Workbench
            print("DEBUG: Instalando MySQL Workbench...")
            # o Workbench não precisa de configuração de senha, apenas instalar
            workbench_config = f"workbench;{target_version};{target_arch}"
            install_wb_cmd = [installer_console, "community", "install", workbench_config, "-silent"]
            subprocess.run(install_wb_cmd, check=True)
            print("DEBUG: MySQL Workbench instalado com sucesso.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"DEBUG: Erro durante o processo de instalação ({e})")
            return False

    def _main():
        # 1. verifica se tem o MySQL instalado
        while not MySQLInstallerWindows._check_mysql_installed():
            # 2. se não tiver, checa se o Terminal/CMD é admin
            if not MySQLInstallerWindows.__is_admin():
                print("DEBUG: Este Terminal/CMD não está como Administrador.")
                break
            # 3. verifica se já tem a senha root gerada
            if not PasswordGenerator._check_password_file():
                print("DEBUG: Arquivo de senha não encontrado.")
                print("DEBUG: Iniciando gerador de senha...")
                PasswordGenerator._main()
                print("DEBUG: Senha gerada.")
            # 4. carrega a senha do arquivo mysql.env específico
            env_path = r"database\data\mysql.env"
            print(f"DEBUG: Lendo variáveis de ambiente de: {env_path}")
            load_dotenv(dotenv_path=env_path)
            env_password = os.getenv("MYSQL_ROOT_PASSWORD")
            # 5. checa se conseguiu ler a senha
            if env_password is None:
                print("DEBUG: A variável MYSQL_ROOT_PASSWORD não foi encontrada.")
                continue
            else:
                print(f"DEBUG: Senha carregada com sucesso.")
            # 6. roda o instalador do MySQL
            MySQLInstallerWindows.__run_installer(env_password)
        print("DEBUG: Encerrando o instalador...")

if __name__ == "__main__":
    MySQLInstallerWindows._main()