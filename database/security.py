from cryptography.fernet import Fernet
import secrets
import string
import os
import ctypes

class PasswordGenerator:
    def __generate_password(length):
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
        # verifica se a chave de criptografia existe, se não, cria uma
        key_path = os.path.join(os.path.dirname(__file__), "data", "secret.key")
        if os.path.exists(key_path):
            with open(key_path, "rb") as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            try:
                # garante que o diretório existe
                os.makedirs(os.path.dirname(key_path), exist_ok=True)
                with open(key_path, "wb") as key_file:
                    key_file.write(key)
                # oculta arquivo da chave no Windows (mesma lógica do seu código)
                try:
                    ctypes.windll.kernel32.SetFileAttributesW(key_path, 0x02)
                except:
                    pass
                return key
            except IOError as e:
                print(f"DEBUG: Erro ao salvar a chave de criptografia ({e})")
                return None

    def __save_password(password, filename="mysql.env"):
        # obtém a chave e criptografa a senha
        key = PasswordGenerator.__get_or_create_key()
        if not key:
            return # aborta se não conseguir chave
        f = Fernet(key)
        # criptografa a senha (retorna bytes, precisamos decodificar para string para salvar no env)
        encrypted_password = f.encrypt(password.encode()).decode()
        # salva a senha criptografada no formato CHAVE=VALOR
        content = f"MYSQL_ROOT_PASSWORD='{encrypted_password}'"
        try:
            filepath = os.path.join(os.path.dirname(__file__), "data", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True) # garante pasta data
            
            with open(filepath, "w") as file:
                file.write(content)
            # oculta arquivo no Windows
            try:
                ctypes.windll.kernel32.SetFileAttributesW(filepath, 0x02)
            except:
                pass
            print(f"DEBUG: Senha criptografada e salva com sucesso em {os.path.abspath(filepath)}")
        except IOError as e:
            print(f"DEBUG: Erro ao salvar o arquivo ({e})")

    def _check_password_file(filename="mysql.env"):
        return os.path.isfile(os.path.join(os.path.dirname(__file__), "data", filename))

    def _main():
        print("DEBUG: Iniciando verificação de senha...")
        if PasswordGenerator._check_password_file():
            print("DEBUG: Arquivo de senha já existe. Nenhuma ação necessária.")
            return
        print("DEBUG: Gerando senha segura para o Root do MySQL...")
        new_password = PasswordGenerator.__generate_password(length=24)
        # a lógica de salvar agora inclui a criptografia internamente
        PasswordGenerator.__save_password(new_password)

if __name__ == "__main__":
    PasswordGenerator._main()