from cryptography.fernet import Fernet
import os

class PasswordReader:
    def get_mysql_password(filename="mysql.env"):
        # define caminhos baseados na localização deste script
        base_dir = os.path.join(os.path.dirname(__file__), "data")
        key_path = os.path.join(base_dir, "secret.key")
        env_path = os.path.join(base_dir, filename)
        # carrega a chave de criptografia
        if not os.path.exists(key_path):
            raise FileNotFoundError("UNCRYPTO: Chave de criptografia (secret.key) não encontrada.")
        with open(key_path, "rb") as key_file:
            key = key_file.read()
        # lê o arquivo env criptografado
        if not os.path.exists(env_path):
             raise FileNotFoundError(f"UNCRYPTO: Arquivo de senha ({filename}) não encontrado.")
        encrypted_token = None
        try:
            with open(env_path, "r") as file:
                content = file.read().strip()
                # lógica simples de parse para extrair o valor entre aspas simples
                # formato esperado: MYSQL_ROOT_PASSWORD='valor_criptografado'
                if "MYSQL_ROOT_PASSWORD=" in content:
                    start_quote = content.find("'") + 1
                    end_quote = content.rfind("'")
                    encrypted_token = content[start_quote:end_quote]
        except Exception as e:
            raise ValueError(f"UNCRYPTO: Erro ({e})")
        # descriptografa a senha
        try:
            f = Fernet(key)
            decrypted_password = f.decrypt(encrypted_token.encode()).decode()
            return decrypted_password
        except Exception as e:
            raise ValueError(f"UNCRYPTO: Erro ({e})")