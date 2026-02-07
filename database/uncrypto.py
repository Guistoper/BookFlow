from cryptography.fernet import Fernet
import os
import sys

class PasswordReader:
    def _get_mysql_password(filename="mysql.env"):
        # define caminhos baseados na localização deste script
        base_dir = os.path.join(os.path.dirname(__file__), "data")
        key_path = os.path.join(base_dir, "secret.key")
        env_path = os.path.join(base_dir, filename)
        # carrega a chave de criptografia (Otimização: tenta abrir direto)
        try:
            with open(key_path, "rb") as key_file:
                key = key_file.read()
        except FileNotFoundError:
            raise FileNotFoundError("UNCRYPTO: Chave de criptografia (secret.key) não encontrada.")
        # lê o arquivo env criptografado
        encrypted_token = None
        try:
            with open(env_path, "r") as file:
                content = file.read().strip()
                # lógica simples de parse
                if "MYSQL_ROOT_PASSWORD=" in content:
                    start_quote = content.find("'") + 1
                    end_quote = content.rfind("'")
                    encrypted_token = content[start_quote:end_quote]
        except FileNotFoundError:
            raise FileNotFoundError(f"UNCRYPTO: Arquivo de senha ({filename}) não encontrado.")
        except Exception as e:
            raise ValueError(f"UNCRYPTO: Erro ao ler token ({e})")
        # descriptografa a senha
        try:
            f = Fernet(key)
            decrypted_password = f.decrypt(encrypted_token.encode()).decode()
            return decrypted_password
        except Exception as e:
            print(f"UNCRYPTO: Falha na descriptografia ({e}). As credenciais estão dessincronizadas.")
            print("UNCRYPTO: Removendo arquivos corrompidos para permitir reinstalação...")
            try:
                os.remove(key_path)
            except: pass
            try:
                os.remove(env_path)
            except: pass
            print("UNCRYPTO: Reiniciando a aplicação automaticamente para corrigir o ambiente...")
            # reinicia o processo atual utilizando o interpretador Python atual e os mesmos argumentos
            os.execv(sys.executable, [sys.executable] + sys.argv)