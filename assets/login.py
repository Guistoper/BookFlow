from assets.app import BookFlowApp
import customtkinter as ctk

# cores que são utilizadas na classe de login, definidas como constantes para facilitar manutenção e padronização do design
TEXT_COLOR_BLACK = "#000000"
TEXT_COLOR_WHITE = "#ffffff"
BLUE_COLOR = "#206eff"
BLUE_COLOR_HOVER = "#1546a8"
WHITE_COLOR = "#f0f0f0"
WHITE_COLOR_HOVER = "#cccccc"

class BookFlowLogin(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configurações da janela principal do login
        self.title("BookFlow Login")
        self.geometry("1280x720")
        self.minsize(854, 480)
        self.resizable(True, True)
        self.after(25, lambda: self.state('zoomed'))

        # intercepta o clique no "X" da janela e encerra o programa
        self.protocol("WM_DELETE_WINDOW", self.quit)

        # definição do background
        background = ctk.CTkFrame(self, fg_color=BLUE_COLOR, corner_radius=0)
        background.pack(fill="both", expand=True)

        close_button = ctk.CTkButton(self, bg_color=BLUE_COLOR, text="X", command=self.destroy, width=50, height=50, corner_radius=15, fg_color=WHITE_COLOR, hover_color=WHITE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        close_button.place(relx=1, x=-50, y=50, anchor="ne")

        white_frame = ctk.CTkFrame(background, fg_color="white", corner_radius=25)
        white_frame.place(relx=0.5, rely=0.5, anchor="center")

        # título do login
        login_title = ctk.CTkLabel(white_frame, text="Bookflow Login", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        login_title.pack(pady=(20, 10))

        # campo do nome de usuário
        userfield = ctk.CTkLabel(white_frame, text="Nome de Usuário", text_color="gray", anchor="w", font=("Arial", 12))
        userfield.pack(fill="x", padx=20)
        
        self.username_entry = ctk.CTkEntry(white_frame, corner_radius=25, fg_color=WHITE_COLOR, border_width=0, text_color=TEXT_COLOR_BLACK, font=("Arial", 14))
        self.username_entry.pack(fill="x", padx=20, pady=(0, 5), ipady=5, ipadx=50)
        self.username_entry.bind("<Return>", self.login)

        # campo da senha
        passfield = ctk.CTkLabel(white_frame, text="Senha", text_color="gray", anchor="w", font=("Arial", 12))
        passfield.pack(fill="x", padx=20)
        
        self.password_entry = ctk.CTkEntry(white_frame, corner_radius=25, fg_color=WHITE_COLOR, border_width=0, text_color=TEXT_COLOR_BLACK, font=("Arial", 14), show="*")
        self.password_entry.pack(fill="x", padx=20, pady=(0, 15), ipady=5, ipadx=50)
        self.password_entry.bind("<Return>", self.login)

        # botão entrar
        enter_button = ctk.CTkButton(white_frame, text="Entrar", command=self.login, width=80, height=40, corner_radius=15, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_WHITE, font=("Arial", 16, "bold"))
        enter_button.pack(pady=(5, 10))

        # texto de rodapé
        footer_text = ctk.CTkLabel(white_frame, text="Apenas para Administradores", text_color="gray", font=("Arial", 12))
        footer_text.pack(pady=(0, 5))

        self.mainloop()

    def login(self, event=None):
        # verifica as credenciais e acessa o sistema
        user = self.username_entry.get()
        password = self.password_entry.get()

        # verifica se há campos vazios
        if user == "" or password == "":
            self.__error(login_error="empty_fields")
            return # interrompe a função aqui

        # verificação de credenciais (substitua pela sua lógica de banco de dados no futuro)
        if user == "admin" and password == "admin": # placeholder para senha, criação de senhas em /actions/password.py
            # limpa os campos do índice 0 até o final ('end')
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.withdraw()
            BookFlowApp(login_window=self).mainloop()

        else:
            self.__error(login_error="username_or_password")

    def __error(self, login_error):
        # exibe popup de erro
        error = ctk.CTkToplevel(self, fg_color=BLUE_COLOR)
        error.title("BookFlow Erro")            
        error.resizable(False, False)
        error.transient(self)
        error.grab_set()

        white_frame = ctk.CTkFrame(error, fg_color=WHITE_COLOR, corner_radius=25)
        white_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # mensagem dinâmica baseada no erro
        if login_error == "username_or_password":
            message = "Usuário ou senha incorretos."
        
        if login_error == "empty_fields":
            message = "Preencha os campos obrigatórios."
        
        error_title = ctk.CTkLabel(white_frame, text=message, text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"), justify="center")
        error_title.pack(pady=(20, 10), padx=20)

        try_again_button = ctk.CTkButton(white_frame, text="Tentar Novamente", fg_color=BLUE_COLOR, width=80, height=40, hover_color=BLUE_COLOR_HOVER, corner_radius=15, text_color=TEXT_COLOR_WHITE, command=error.destroy, font=("Arial", 16, "bold"))
        try_again_button.pack(pady=(10, 20))

        # centraliza a janela de erro
        error.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (error.winfo_reqwidth() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (error.winfo_reqheight() // 2)
        error.geometry(f"+{x}+{y}")