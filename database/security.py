import secrets
import string
import os
import ctypes

class PasswordGenerator:
    def __generate_password(length):
        # gera uma senha criptograficamente forte
        # garante pelo menos 1 letra maiúscula, 1 minúscula, 1 número e 1 símbolo
        # definição dos caracteres permitidos
        # removemos as aspas simples e duplas para evitar erros na linha de comando SQL
        letters = string.ascii_letters
        numbers = string.digits
        symbols = "!@$%^*()_+-[]{}|;:,.<>?" 
        alphabet = letters + numbers + symbols
        while True:
            # gera uma senha aleatória
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            # garante que a senha tenha todos os requisitos de complexidade
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_number = any(c.isdigit() for c in password)
            has_symbol = any(c in symbols for c in password)
            # se sim, retorna a senha
            if has_upper and has_lower and has_number and has_symbol:
                return password

    def __save_password(password, filename="mysql.env"):
        # salva a senha em um arquivo no formato CHAVE=VALOR
        content = f"MYSQL_ROOT_PASSWORD='{password}'"
        try:
            with open(os.path.join(os.path.dirname(__file__), "data", filename), "w") as file:
                file.write(content)
            # oculta arquivo no Windows
            try:
                # atributo 0x02 = hidden
                ctypes.windll.kernel32.SetFileAttributesW(os.path.join(os.path.dirname(__file__), "data", filename), 0x02)
            except:
                pass
            print(f"DEBUG: Senha gerada e salva com sucesso em {os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', filename))}")
        except IOError as e:
            print(f"DEBUG: Erro ao salvar o arquivo ({e})")
    def _check_password_file(filename="mysql.env"):
        # verifica se o arquivo de senha já existe
        return os.path.isfile(os.path.join(os.path.dirname(__file__), "data", filename))
    def _main():
        # 1. checa se a senha já foi gerada
        print("DEBUG: Iniciando verificação de senha...")
        if PasswordGenerator._check_password_file():
            print("DEBUG: Arquivo de senha já existe. Nenhuma ação necessária.")
            return
        print("DEBUG: Gerando senha segura para o Root do MySQL...")
        # se não foi gerada, ele gera uma nova
        # 2. gera a senha
        new_password = PasswordGenerator.__generate_password(length=24)
        # 3. salva no arquivo em /database/data/mysql.env
        PasswordGenerator.__save_password(new_password)

if __name__ == "__main__":
    PasswordGenerator._main()