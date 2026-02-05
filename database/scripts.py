from database.server import MySQLInstallerWindows
from database.uncrypto import PasswordReader
from dotenv import load_dotenv
import mysql.connector
import os
import sys

class MySQLScriptRunner:
    def __get_connection(password):
        # tenta conectar ao servidor MySQL (sem selecionar banco específico ainda)
        try:
            cnx = mysql.connector.connect(
                user='root',
                password=password,
                host='localhost'
            )
            return cnx
        except mysql.connector.Error as err:
            print(f"SCRIPTS: Erro ({err})")
            return None
        
    def _check_database(password, database):
        print(f"SCRIPTS: Iniciando verificação da existência do banco de dados '{database}'...")
        # reutiliza o método privado de conexão da classe
        cnx = MySQLScriptRunner.__get_connection(password)
        try:
            cursor = cnx.cursor()
            # executa a query para verificar se o schema existe
            cursor.execute(f"SHOW DATABASES LIKE '{database}'")
            result = cursor.fetchone()
            # fecha recursos temporários
            cursor.close()
            cnx.close()
            if result:
                print(f"SCRIPTS: O banco de dados '{database}' já existe.")
                return True
            else:
                print(f"SCRIPTS: O banco de dados '{database}' não foi encontrado.")
                return False
        except mysql.connector.Error as err:
            print(f"SCRIPTS: Erro ({err})")
            return False

    def __run_sql_file(cursor, cnx, script_path):
        filename = os.path.basename(script_path)
        if not os.path.exists(script_path):
            print(f"SCRIPTS: Arquivo não encontrado: {filename}")
            return False
        print(f"SCRIPTS: Lendo e executando script: {filename}...")
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
                        print(f"SCRIPTS: Aviso ({err})")
                        # se for um erro crítico, retornamos False
            # confirma as alterações
            cnx.commit()
            print(f"SCRIPTS: Sucesso ao executar {filename}.")
            return True
        except Exception as e:
            print(f"SCRIPTS: Erro ({e})")
            return False

    def _main():
        print("SCRIPTS: Iniciando execução de scripts SQL...")
        # carrega a senha do arquivo mysql.env
        unc_password = PasswordReader.get_mysql_password()
        # cria a conexão com o banco
        cnx = MySQLScriptRunner.__get_connection(unc_password)
        if cnx is None:
            return # encerra se não conectar
        cursor = cnx.cursor()
        # definição dos caminhos e ordem
        base_script_path = r"database\data\scripts"
        mandatory_scripts = ["database.sql", "tables.sql", "views.sql"]
        # executa os scripts obrigatórios
        for script_name in mandatory_scripts:
            full_path = os.path.join(base_script_path, script_name)
            success = MySQLScriptRunner.__run_sql_file(cursor, cnx, full_path)
            if not success:
                print("SCRIPTS: A execução foi interrompida devido a um erro crítico.")
                cursor.close()
                cnx.close()
                return
        # lógica opcional para o examples.sql
        print("SCRIPTS: Scripts estruturais finalizados.")
        # input() pausa o script esperando o usuário
        user_input = input("SCRIPTS: Deseja popular o banco de dados com dados de exemplo? (S/N): ").strip().lower()
        if user_input in ['s', 'sim', 'y', 'yes']:
            examples_path = os.path.join(base_script_path, "examples.sql")
            MySQLScriptRunner.__run_sql_file(cursor, cnx, examples_path)
        else:
            print("SCRIPTS: Pular etapa de dados exemplo.")
        # limpeza e fechamento
        print("SCRIPTS: Encerrando conexões...")
        cursor.close()
        cnx.close()
        print("SCRIPTS: Processo finalizado.")