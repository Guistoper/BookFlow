from database.server import MySQLConnect
from database.uncrypto import PasswordReader
from CTkTable import *
from datetime import datetime
from pathlib import Path
import customtkinter as ctk
import json

# cores que são utilizadas na classe principal do aplicativo, definidas como constantes para facilitar manutenção e padronização do design
TEXT_COLOR_BLACK = "#000000"
TEXT_COLOR_WHITE = "#ffffff"
BLUE_COLOR = "#206eff"
BLUE_COLOR_HOVER = "#1546a8"
LIGHT_BLUE_COLOR = "#4687ff"
WHITE_COLOR = "#f0f0f0"
WHITE_COLOR_HOVER = "#cccccc"
YELLOW_COLOR = "#ffcc00"
YELLOW_COLOR_HOVER = "#ffdb4d"
GRAY_COLOR = "#a0a0a0"

class BookFlowApp(ctk.CTk):
    def __init__(self, login_window):
        super().__init__()
        
        self.login_window = login_window
        self.title("BookFlow")
        self.geometry("1280x720")
        self.minsize(854, 480)
        self.resizable(True, True)
        self.after(25, lambda: self.state('zoomed'))

        # intercepta o clique no "X" da janela e encerra o programa
        self.protocol("WM_DELETE_WINDOW", self.__quit_app)

        # variáveis de estado
        self.active_button_name = "ADMINISTRAÇÃO"
        self.buttons = {}
        self.sidebar_visible = True

        # caminho do arquivo de configuração (usando pathlib), e criação da pasta se não existir para evitar erros futuros
        self.json_config = Path(__file__).parent / "data" / "config.json"
        self.json_config.parent.mkdir(parents=True, exist_ok=True)

        # variáveis de configuração com valores padrão
        self.maxaluno = 3
        self.maxprofessor = 30
        self.datadev = 15
        
        self.__load_info()
        self.date_today = datetime.now()

        self.__setup()

    def __load_info(self):
        # lê o JSON e que se não existir ou der erro, salva os padrões
        if self.json_config.exists():
            try:
                with open(self.json_config, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.maxaluno = dados.get("maxaluno", self.maxaluno)
                    self.maxprofessor = dados.get("maxprofessor", self.maxprofessor)
                    self.datadev = dados.get("datadev", self.datadev)
                print("APP: Configurações carregadas com sucesso.")
            except Exception as e:
                print(f"APP: Erro {e}")
        else:
            print("APP: Arquivo não encontrado. Criando padrões...")
            self.__save_info()

    def __save_info(self):
        # salva as configurações atuais no JSON
        dados = {
            "maxaluno": self.maxaluno,
            "maxprofessor": self.maxprofessor,
            "datadev": self.datadev
        }
        try:
            with open(self.json_config, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4) 
            print("APP: Configurações salvas no JSON.")
        except Exception as e:
            print(f"APP: Erro {e}")

    def __clear_main_frame(self):
        # limpa a tela principal destruindo os widgets filhos
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def __setup(self):
        # configuração do grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # definição da sidebar
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=BLUE_COLOR, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) # empurra o botão SAIR para baixo

        self.collapse_button = ctk.CTkButton(
            self.sidebar_frame, text="←", fg_color=LIGHT_BLUE_COLOR, 
            hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, 
            font=("Arial", 24), width=20, command=self.__toggle_sidebar
        )
        self.collapse_button.grid(row=0, column=0, padx=20, pady=20, sticky="n")
        # efeitos de Hover no botão collapse
        self.collapse_button.bind("<Enter>", lambda e: self.collapse_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        self.collapse_button.bind("<Leave>", lambda e: self.collapse_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_BLUE_COLOR))

        # criação dos botões do menu
        menus = ["ADMINISTRAÇÃO", "LIVROS", "USUÁRIOS", "EMPRÉSTIMOS", "DEVOLUÇÕES"]
        for idx, menu in enumerate(menus, start=1):
            self.buttons[menu] = self.__create_sidebar_button(menu, idx)
        self.buttons["CONFIGURAÇÕES"] = self.__create_sidebar_button("CONFIGURAÇÕES", 7) # posição fixa para configurações
        self.buttons["SAIR"] = self.__create_sidebar_button("SAIR", 8, self.__logout)

        # definição do main frame
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        # expand button (escondido inicialmente)
        self.expand_button_frame = ctk.CTkFrame(self, fg_color=BLUE_COLOR_HOVER, width=50, corner_radius=0)
        self.expand_button = ctk.CTkButton(self.expand_button_frame, text="→", fg_color="transparent", hover_color=BLUE_COLOR, font=("Arial", 24), width=20, command=self.__toggle_sidebar)
        self.expand_button.place(relx=0.5, rely=0.5, anchor="center")
        self.__set_active_button(self.active_button_name)

    def __toggle_sidebar(self):
        # alterna a visibilidade da barra lateral de forma otimizada usando grid_remove
        if self.sidebar_visible:
            self.sidebar_frame.grid_remove() # oculta mas lembra a posição
            self.expand_button_frame.grid(row=0, column=0, sticky="nsew")
        else:
            self.expand_button_frame.grid_remove()
            self.sidebar_frame.grid() # restaura com as opções originais
        self.sidebar_visible = not self.sidebar_visible

    def __create_sidebar_button(self, text, row, command_func=None):
        # fábrica de botões para a barra lateral
        def wrapped_command():
            if text != "SAIR":
                self.__set_active_button(text)
            if command_func: # evita erro se command_func for None (placeholder para criação de novas páginas)
                command_func()
        button = ctk.CTkButton(self.sidebar_frame, text=text, anchor="w", corner_radius=25, fg_color=LIGHT_BLUE_COLOR, text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), command=wrapped_command)
        button.bind("<Enter>", lambda e, b=button: b.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        button.bind("<Leave>", lambda e, b=button: b.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_BLUE_COLOR))
        pad_y = 10
        sticky_opt = "sew" if text == "SAIR" else "ew"
        button.grid(row=row, column=0, padx=10, pady=pad_y, sticky=sticky_opt)
        return button

    def __set_active_button(self, name):
        # muda a cor do botão ativo e reseta o anterior
        if self.active_button_name in self.buttons:
            old_button = self.buttons[self.active_button_name]
            old_button.configure(fg_color=LIGHT_BLUE_COLOR, text_color=TEXT_COLOR_BLACK)
            # aplica hover normal ao botão antigo, mas apenas se não for o SAIR, para evitar confusão visual (SAIR sempre tem o mesmo estilo)
            if self.active_button_name != "SAIR":
                old_button.bind("<Enter>", lambda e: old_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
                old_button.bind("<Leave>", lambda e: old_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_BLUE_COLOR))

        # atualiza o novo botão ativo, mas não altera o estilo do botão SAIR para evitar confusão visual (SAIR sempre tem o mesmo estilo)
        if name != "SAIR" and name in self.buttons:
            new_button = self.buttons[name]
            self.active_button_name = name
            new_button.configure(fg_color=YELLOW_COLOR, text_color=TEXT_COLOR_BLACK)
            new_button.bind("<Enter>", lambda e: new_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=YELLOW_COLOR_HOVER))
            new_button.bind("<Leave>", lambda e: new_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=YELLOW_COLOR))

    def __logout(self):
        # cria e exibe o popup de logout
        popup = ctk.CTkToplevel(self, fg_color="white")
        popup.title("BookFlow Logout")            
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        content_frame = ctk.CTkFrame(popup, fg_color="white", corner_radius=0)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        logout_icon = ctk.CTkLabel(content_frame, text="🚪", text_color=TEXT_COLOR_BLACK, font=("Arial", 60))
        logout_icon.pack(pady=(0, 5))

        logout_text = ctk.CTkLabel(content_frame, text="Tem certeza que deseja sair?", text_color=TEXT_COLOR_BLACK, font=("Arial", 14, "bold"))
        logout_text.pack(pady=(0, 20))

        # frame para os botões ficarem lado a lado
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack()

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=popup.destroy, fg_color=LIGHT_BLUE_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=90)
        cancel_button.pack(side="left", padx=10)
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_BLUE_COLOR))

        confirm_button = ctk.CTkButton(button_frame, text="Confirmar", command=self.__close, fg_color=GRAY_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=90)
        confirm_button.pack(side="left", padx=10)
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=GRAY_COLOR))

        # centralização do popup
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_reqwidth() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_reqheight() // 2)
        popup.geometry(f"+{x}+{y}")

    def __close(self):
        # encerra a sessão e transfere a posição/tamanho para a tela de login
        current_geometry = self.geometry()

        # seta o estado da janela para maximizada para a tela de login abrir maximizada ("zoomed")
        current_state = "zoomed"

        # exibe a tela de login novamente
        self.login_window.deiconify()

        # aplica o estado (maximizada/normal) na tela de login
        try:
            self.login_window.state(current_state)
        except Exception as e:
            print(f"APP: Erro {e}")

        # destrói a janela atual do sistema
        self.after(250, self.destroy)

    def __quit_app(self):
        # encerra a aplicação inteira ao fechar a janela principal
        self.login_window.destroy() # destrói a janela de login oculta
        self.destroy()              # destrói a janela atual