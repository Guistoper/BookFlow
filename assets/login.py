from assets.app import RunApp

class RunAppLogin:
    # por enquanto é um placeholder
    def __init__(self):
        print("LOGIN: Iniciando a aplicação BookFlow...")
        print("LOGIN: Interface de login iniciada.")
        while not RunAppLogin.__enter_login():
            continue
        RunApp()    
    def __enter_login():
        user_input = input("LOGIN: Deseja iniciar o aplicativo BookFlow? (s/n): ")
        if not user_input or user_input.lower() not in ['s', 'sim', 'y', 'yes']:
            return False
        return True