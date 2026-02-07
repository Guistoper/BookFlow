from cryptography.fernet import Fernet
import secrets
import string
import os
import ctypes

class PasswordGenerator:
    def __generate_password(length):
        print("SECURITY: Iniciando gerador de senha...")
        letters = string.ascii_letters
        numbers = string.digits
        symbols = "-_+=." 
        alphabet = letters + numbers + symbols
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_number = any(c.isdigit() for c in password)
            has_symbol = any(c in symbols for c in password)
            if has_upper and has_lower and has_number and has_symbol:
                return password

    def __get_or_create_key():
        key_path = os.path.join(os.path.dirname(__file__), "data", "secret.key")
        # tenta ler a chave existente; se não existir, cria uma nova.
        try:
            with open(key_path, "rb") as key_file:
                return key_file.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            try:
                os.makedirs(os.path.dirname(key_path), exist_ok=True)
                with open(key_path, "wb") as key_file:
                    key_file.write(key)
                try:
                    ctypes.windll.kernel32.SetFileAttributesW(key_path, 0x02)
                except:
                    pass
                return key
            except IOError as e:
                print(f"SECURITY: Erro ({e})")
                return None

    def __save_password(password, filename="mysql.env"):
        key = PasswordGenerator.__get_or_create_key()
        if not key: return 
        f = Fernet(key)
        encrypted_password = f.encrypt(password.encode()).decode()
        content = f"MYSQL_ROOT_PASSWORD='{encrypted_password}'"
        try:
            filepath = os.path.join(os.path.dirname(__file__), "data", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as file:
                file.write(content)
            try:
                ctypes.windll.kernel32.SetFileAttributesW(filepath, 0x02)
            except:
                pass
            print(f"SECURITY: Senha criptografada e salva com sucesso ({os.path.abspath(filepath)})")
        except IOError as e:
            print(f"SECURITY: Erro ({e})")

    def _check_password_file(filename="mysql.env"):
        return os.path.isfile(os.path.join(os.path.dirname(__file__), "data", filename))
    
    def _check_password_secret(filename="secret.key"):
        return os.path.isfile(os.path.join(os.path.dirname(__file__), "data", filename))

    def _main():
        print("SECURITY: Iniciando verificação de senha...")
        if PasswordGenerator._check_password_file() and PasswordGenerator._check_password_secret():
            print("SECURITY: Arquivo de senha existente")
            print("SECURITY: Chave de criptografia existente")
            return
        # se chegou aqui, gera tudo
        new_password = PasswordGenerator.__generate_password(length=24)
        PasswordGenerator.__save_password(new_password)