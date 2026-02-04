from server import MySQLInstallerWindows
from dotenv import load_dotenv
from mysql.connector import errorcode
import mysql.connector
import os
import sys

class MySQLScriptRunner:
    def __get_connection(password):
        # tenta conectar ao servidor MySQL (sem selecionar banco específico ainda)
        print("DEBUG: Conectando ao servidor MySQL via conector Python...")
        try:
            cnx = mysql.connector.connect(
                user='root',
                password=password,
                host='localhost',
                use_pure=True, # força o uso do cursor Python que aceita multi=True
                auth_plugin='mysql_native_password' # se tiver problemas de autenticação no MySQL 8, descomente esta linha
            )
            print("DEBUG: Conexão estabelecida com sucesso.")
            return cnx
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("DEBUG: Nome de usuário ou senha incorretos.")
            else:
                print(f"DEBUG: {err}")
            return None

    def __run_sql_file(cursor, cnx, script_path):
        filename = os.path.basename(script_path)
        if not os.path.exists(script_path):
            print(f"DEBUG: Arquivo não encontrado: {filename}")
            return False
        print(f"DEBUG: Lendo e executando script: {filename}...")
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            # divide o script por ponto e vírgula
            commands = sql_script.split(';')
            for command in commands:
                # limpa espaços em branco e pulos de linha
                cleaned_command = command.strip()
                # se o comando não estiver vazio, executa
                if cleaned_command:
                    try:
                        cursor.execute(cleaned_command)
                    except mysql.connector.Error as err:
                        # ignora erros de "Query was empty" que podem sobrar da divisão
                        print(f"DEBUG: Aviso ao rodar parte do script: {err}")
                        # se for um erro crítico, retornamos False (opcional)
            # confirma as alterações
            cnx.commit()
            print(f"DEBUG: Sucesso ao executar {filename}.")
            return True

        except Exception as e:
            print(f"DEBUG: Erro crítico ao processar o arquivo ({e})")
            return False

    def _main():
        # 1. checa se o MySQL está instalado
        if MySQLInstallerWindows._check_mysql_installed() is False:
            print("DEBUG: MySQL não está instalado.")
            return
        print("DEBUG: Iniciando rotina de execução de scripts SQL...")
        # 2. carrega a senha do arquivo mysql.env
        env_path = r"database\data\mysql.env"
        if not os.path.exists(env_path):
             print(f"DEBUG: Arquivo de ambiente {env_path} não encontrado.")
             return
        load_dotenv(dotenv_path=env_path)
        env_password = os.getenv("MYSQL_ROOT_PASSWORD")
        if not env_password:
            print("DEBUG: Senha não encontrada nas variáveis de ambiente.")
            return
        # 3. cria a conexão com o banco
        cnx = MySQLScriptRunner.__get_connection(env_password)
        if cnx is None:
            return # encerra se não conectar
        cursor = cnx.cursor()
        # 4. definição dos caminhos e ordem
        base_script_path = r"database\data\scripts"
        mandatory_scripts = ["database.sql", "tables.sql", "views.sql"]
        # 5. executa os scripts obrigatórios
        for script_name in mandatory_scripts:
            full_path = os.path.join(base_script_path, script_name)
            success = MySQLScriptRunner.__run_sql_file(cursor, cnx, full_path)
            if not success:
                print("DEBUG: A execução foi interrompida devido a um erro crítico.")
                cursor.close()
                cnx.close()
                return
        # 6. lógica opcional para o examples.sql
        print("DEBUG: Scripts estruturais finalizados.")
        # input() pausa o script esperando o usuário
        user_input = input("DEBUG: Deseja popular o banco de dados com dados de exemplo? (S/N): ").strip().lower()
        if user_input in ['s', 'sim', 'y', 'yes']:
            examples_path = os.path.join(base_script_path, "examples.sql")
            MySQLScriptRunner.__run_sql_file(cursor, cnx, examples_path)
        else:
            print("DEBUG: Pular etapa de exemplos.")
        # 7. limpeza e fechamento
        print("DEBUG: Encerrando conexões...")
        cursor.close()
        cnx.close()
        print("DEBUG: Processo finalizado.")

if __name__ == "__main__":
    MySQLScriptRunner._main()