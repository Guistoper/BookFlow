from assets.app import BookFlowApp
import customtkinter as ctk


# cores que são utilizadas na classe de login, definidas como constantes para facilitar manutenção e padronização do design
TEXT_COLOR_BLACK="#000000"
TEXT_COLOR_WHITE="#ffffff"
BLUE_COLOR="#206eff"
BLUE_COLOR_HOVER="#1a54c8"
WHITE_COLOR="#f0f0f0"
WHITE_COLOR_HOVER="#cccccc"

# classe de rodar o app do login, onde o usuário insere suas credenciais para acessar o aplicativo principal
# pode ser expandida para incluir mais formas de autenticação e outras funcionalidades relacionadas ao login
class BookFlowLogin(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configurações da janela principal do login
        self.title("BookFlow Login")
        self.geometry("1280x720")
        self.minsize(854, 480)
        self.resizable(True, True)
        self.after(0, lambda: self.state('zoomed'))

        # configuração do layout e widgets da tela de login
        bg = ctk.CTkFrame(self, fg_color=BLUE_COLOR, corner_radius=0)
        bg.pack(fill="both", expand=True)

        close_button = ctk.CTkButton(self, bg_color=BLUE_COLOR, text="X", command=self.destroy, width=50, height=50, corner_radius=15, fg_color=WHITE_COLOR, hover_color=WHITE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        close_button.place(relx=1, x=-50, y=50, anchor="ne")

        frame = ctk.CTkFrame(bg, fg_color="white", corner_radius=25)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # texto de cima
        text_top = ctk.CTkLabel(frame, text="Bookflow Login", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        text_top.pack(pady=(20, 10))

        # texto do campo de colocar o nome de usuário
        user_label = ctk.CTkLabel(frame, text="Nome de Usuário", text_color="gray", anchor="w", font=("Arial", 12))
        user_label.pack(fill="x", padx=20)

        # campo de colocar o nome de usuário, com um bind para permitir o login ao pressionar Enter
        user_entry = ctk.CTkEntry(frame, corner_radius=25, fg_color=WHITE_COLOR, border_width=0, text_color=TEXT_COLOR_BLACK, font=("Arial", 14))
        user_entry.pack(fill="x", padx=20, pady=(0, 5), ipady=5, ipadx=50)
        user_entry.bind("<Return>", lambda e: login())

        # texto do campo de colocar a senha
        word_label = ctk.CTkLabel(frame, text="Senha", text_color="gray", anchor="w", font=("Arial", 12))
        word_label.pack(fill="x", padx=20)

        # campo de colocar a senha, com o show="*" para ocultar os caracteres digitados, e um bind para permitir o login ao pressionar Enter
        word_entry = ctk.CTkEntry(frame, corner_radius=25, fg_color=WHITE_COLOR, border_width=0, text_color=TEXT_COLOR_BLACK, font=("Arial", 14), show="*")
        word_entry.pack(fill="x", padx=20, pady=(0, 15), ipady=5, ipadx=50)
        word_entry.bind("<Return>", lambda e: login())

        # função de exibir uma janela de erro personalizada, que é chamada quando o usuário insere credenciais incorretas ou deixa campos vazios
        def error(wrong):
            # configurações da janela de erro, que é um Toplevel para criar uma janela modal sobre a janela de login, com um design consistente com o restante do aplicativo
            error = ctk.CTkToplevel(self, fg_color=BLUE_COLOR)
            error.title("BookFlow Erro")            
            error.resizable(False, False)
            error.transient(self)
            error.grab_set()
            error.grid_columnconfigure(0, weight=1)
            error.grid_rowconfigure(0, weight=1)

            content_frame = ctk.CTkFrame(error, fg_color=WHITE_COLOR, corner_radius=25)
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)
            content_frame.grid_columnconfigure(0, weight=1)

            # função para fechar a janela de erro, que é chamada ao clicar no botão "Tentar novamente"
            def close_error():
                error.destroy()

            # exibe mensagens de erro diferentes dependendo do tipo de erro (credenciais incorretas ou campos vazios), e centraliza a janela de erro sobre a janela de login
            if wrong == 1:
                error_title = ctk.CTkLabel(content_frame, text="Usuário ou senha incorretos.", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"), justify="center")
                error_title.grid(row=0, column=0, pady=(20, 10), padx=20)

            elif wrong == 2:
                error_title = ctk.CTkLabel(content_frame, text="Preencha os campos obrigatórios.", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"), justify="center")
                error_title.grid(row=0, column=0, pady=(20, 10), padx=20)

            # botão para fechar a janela de erro e permitir que o usuário tente fazer login novamente, com um design consistente com o restante do aplicativo
            try_again = ctk.CTkButton(content_frame, text="Tentar Novamente", fg_color=BLUE_COLOR, width=80, height=40, hover_color=BLUE_COLOR_HOVER, corner_radius=15, text_color=TEXT_COLOR_WHITE, command=close_error, font=("Arial", 16, "bold"))
            try_again.grid(row=1, column=0, sticky="s", pady=(10, 20))

            # centraliza a janela de erro sobre a janela de login, calculando as coordenadas com base nas dimensões da janela de erro e da janela de login, e usando o método geometry para posicionar a janela de erro corretamente
            error.update_idletasks()
            req_width = error.winfo_reqwidth()
            req_height = error.winfo_reqheight()
            x = self.winfo_x() + (self.winfo_width() // 2) - (req_width // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (req_height // 2)
            error.geometry(f"{req_width}x{req_height}+{x}+{y}")
        
        # função de login, que é chamada ao clicar no botão "Entrar" ou pressionar Enter, e verifica as credenciais inseridas pelo usuário comparando com um dicionário de credenciais corretas
        def login():
            # para fins de teste, as credenciais corretas estão hardcoded como "admin" para o nome de usuário e "admin" para a senha
            user = user_entry.get()
            password = word_entry.get()
            right = {user: "admin", password: "admin"}

            # se as credenciais estiverem corretas, a janela de login é fechada e o aplicativo principal é iniciado, passando a janela de login como referência para o aplicativo principal, caso seja necessário retornar à tela de login no futuro
            if user == right[user] and password == right[password]:
                self.withdraw()
                BookFlowApp(login_window=self).mainloop()
            # se o usuário deixar campos vazios, ou inserir credenciais incorretas, a função de erro é chamada com um código diferente para exibir a mensagem de erro apropriada
            elif user == "" or password == "":
                error(2)
            # se as credenciais estiverem incorretas, a função de erro é chamada com um código para exibir a mensagem de erro de credenciais incorretas
            elif user != right[user] or password != right[password]:
                error(1)

        # botão de login, com um design consistente com o restante do aplicativo, e que chama a função de login ao ser clicado
        enter_button = ctk.CTkButton(frame, text="Entrar", command=login, width=80, height=40, corner_radius=15, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_WHITE, font=("Arial", 16, "bold"))
        enter_button.pack(pady=(5, 10))

        # rodapé da tela de login, com um texto indicando que o acesso é apenas para administradores, e com um design consistente com o restante do aplicativo
        footer_label = ctk.CTkLabel(frame, text="Apenas para Administradores", text_color="gray", font=("Arial", 12))
        footer_label.pack(pady=(0, 5))

        # inicia o loop principal da janela de login, que mantém a janela aberta e responsiva, permitindo que o usuário interaja com os widgets e faça login
        self.mainloop()