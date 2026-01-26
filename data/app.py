import customtkinter as ctk
import mysql.connector
import json
import os
from tkinter import messagebox
from CTkTable import *
from install import Install
from datetime import datetime, timedelta

BLUE_COLOR = "#206eff" 
BLUE_COLOR_HOVER = "#0c50ce"  
LIGHT_COLOR = "#4083ff" 
YELLOW_COLOR = "#FFE600" 
YELLOW_COLOR_HOVER = "#DDC700" 
LIGHT_PURPLE_COLOR = "#D2B6FF"
DARK_PURPLE_COLOR = "#C5A0FF"
TEXT_COLOR_BLACK = "#000000"
TEXT_COLOR_WHITE = "#ffffff"
BUTTON_NEUTRAL = "#e0e0e0"

class Database:
    sql = mysql.connector.connect(
            user="root",
            password="admin",
            host="localhost",
            database = Install.main("biblioteca")
    )

class DashboardApp(ctk.CTk):
    def __init__(self, login_window):
        super().__init__()
        
        self.login_window = login_window
        self.title("Sistema Biblioteca")
        self.geometry("1280x720")
        self.minsize(854, 480)
        self.resizable(True, True)

        self.active_button_name = "ADMINISTRAÇÃO"
        self.buttons = {}
        self.sidebar_visible = True
        self.search_after_id = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.main_frame = None
        self.action_menu_frame = None

        directory_app = os.path.dirname(os.path.abspath(__file__))
        self.json_config = os.path.join(directory_app, "config.json")

        self.maxaluno = 3
        self.maxprofessor = 30
        self.datadev = 15
        self.load_info()

        self.date_today = datetime.now()

        self.setup()

    def load_info(self):
        if os.path.exists(self.json_config):
            try:
                with open(self.json_config, 'r', encoding='utf-8') as f:
                    dados = json.load(f)

                    self.maxaluno = dados.get("maxaluno", self.maxaluno)
                    self.maxprofessor = dados.get("maxprofessor", self.maxprofessor)
                    self.datadev = dados.get("datadev", self.datadev)
                    
                    print("Configurações carregadas com sucesso.")
            except Exception as e:
                print(f"Erro ao ler configurações: {e}")
        else:
            print("Arquivo de configuração não encontrado. Criando um novo com padrões...")
            self.save_info()

    def save_info(self):
        dados = {
            "maxaluno": self.maxaluno,
            "maxprofessor": self.maxprofessor,
            "datadev": self.datadev
        }
        
        try:
            with open(self.json_config, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4) 
                print("Configurações salvas no JSON com sucesso.")
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def setup(self):
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=BLUE_COLOR, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.collapse_button = ctk.CTkButton(self.sidebar_frame, text="←", fg_color=LIGHT_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 24), width=20, command=self.toggle_sidebar)
        self.collapse_button.grid(row=0, column=0, padx=20, pady=20, sticky="n")
        self.collapse_button.bind("<Enter>", lambda e: self.collapse_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        self.collapse_button.bind("<Leave>", lambda e: self.collapse_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        self.buttons["ADMINISTRAÇÃO"] = self.create_sidebar_button("ADMINISTRAÇÃO", 1, self.show_admin)
        self.buttons["LIVROS"] = self.create_sidebar_button("LIVROS", 2, self.show_books)
        self.buttons["USUÁRIOS"] = self.create_sidebar_button("USUÁRIOS", 3, self.show_users)        
        self.buttons["EMPRÉSTIMOS"] = self.create_sidebar_button("EMPRÉSTIMOS", 4, self.show_loans)
        self.buttons["DEVOLUÇÕES"] = self.create_sidebar_button("DEVOLUÇÕES", 5, self.show_returns)

        self.buttons["CONFIGURAÇÕES"] = self.create_sidebar_button("CONFIGURAÇÕES", 7, self.show_config)
        self.buttons["SAIR"] = self.create_sidebar_button("SAIR", 8, self.logout)

        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.expand_button_frame = ctk.CTkFrame(self, fg_color=BLUE_COLOR_HOVER, width=50, corner_radius=0)

        self.expand_button = ctk.CTkButton(self.expand_button_frame, text="→", fg_color="transparent", hover_color=BLUE_COLOR, font=("Arial", 24), width=20, command=self.toggle_sidebar)
        self.expand_button.place(relx=0.5, rely=0.5, anchor="center")

        self.set_active_button(self.active_button_name)
        self.show_admin()

        self.lift()
        self.focus_force()

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar_frame.grid_forget()
            self.collapse_button.grid_forget()

            self.expand_button_frame.grid(row=0, column=0, sticky="nsew")

            self.main_frame.grid_forget()
            self.main_frame.grid(row=0, column=1, sticky="nsew", columnspan=1)

            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=1)

            self.sidebar_visible = False

        else:
            self.expand_button_frame.grid_forget()

            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=1)

            self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
            self.collapse_button.grid(row=0, column=0, padx=20, pady=20, sticky="n")

            self.main_frame.grid_forget()
            self.main_frame.grid(row=0, column=1, sticky="nsew")

            self.sidebar_visible = True

    def create_sidebar_button(self, text, row, command_func):
        def wrapped_command():
            if text != "SAIR":
                self.set_active_button(text)
            command_func()

        button = ctk.CTkButton(self.sidebar_frame, text=f"{text}", compound="left", anchor="w", corner_radius=25, fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), command=wrapped_command)
        button.bind("<Enter>", lambda e, b=button: b.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        button.bind("<Leave>", lambda e, b=button: (b.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR)if self.active_button_name != text else None))

        if text == "SAIR":
            button.grid(row=row, column=0, padx=10, pady=10, sticky="sew")
        else:
            button.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        return button

    def set_active_button(self, name):
        if self.active_button_name in self.buttons:
            old_button = self.buttons[self.active_button_name]
            old_button.configure(fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK)
            if self.active_button_name != "SAIR":
                old_button.bind("<Enter>", lambda e: old_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
                old_button.bind("<Leave>", lambda e: old_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        if name != "SAIR" and name in self.buttons:
            new_button = self.buttons[name]
            self.active_button_name = name

            new_button.configure(fg_color=YELLOW_COLOR, text_color=TEXT_COLOR_BLACK)
            new_button.bind("<Enter>", lambda e: new_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=YELLOW_COLOR_HOVER))
            new_button.bind("<Leave>", lambda e: new_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=YELLOW_COLOR))

    def logout(self):
        popup = ctk.CTkToplevel(self, fg_color="white")
        popup.title("Sair")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(popup, fg_color="white", corner_radius=0)
        content_frame.pack(fill="both", expand=True)
        content_frame.grid_columnconfigure((0, 1), weight=1)

        popup_icon = ctk.CTkLabel(content_frame, text="🚪", text_color=TEXT_COLOR_BLACK, font=("Arial", 60))
        popup_icon.grid(row=0, column=0, columnspan=2, pady=(10, 5))

        popup_title = ctk.CTkLabel(content_frame, text="Tem certeza que deseja sair?", text_color=TEXT_COLOR_BLACK, font=("Arial", 14, "bold"), justify="center")
        popup_title.grid(row=1, column=0, columnspan=2, pady=(5, 20), padx=20)

        cancel_button = ctk.CTkButton(content_frame, text="Cancelar", command=popup.destroy, fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        cancel_button.grid(row=2, column=0, padx=10, pady=(0, 25), sticky="e")
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        confirm_button = ctk.CTkButton(content_frame, text="Confirmar", command=self.close, fg_color=BUTTON_NEUTRAL, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        confirm_button.grid(row=2, column=1, padx=10, pady=(0, 25), sticky="w")
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=BUTTON_NEUTRAL)) 

        popup.update_idletasks()
        req_width = popup.winfo_reqwidth()
        req_height = popup.winfo_reqheight()
        x = self.winfo_x() + (self.winfo_width() // 2) - (req_width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (req_height // 2)
        popup.geometry(f"{req_width}x{req_height}+{x}+{y}")

    def close(self):
        self.after(100, self.perform_close)

    def perform_close(self):
        self.destroy()
        self.login_window.deiconify()

    def show_config(self):
        self.clear_main_frame()

        self.main_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=0)

        title = ctk.CTkLabel(self.main_frame, text="CONFIGURAÇÕES", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, columnspan=3, padx=25, pady=(23, 15), sticky="nw")

        form_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
        form_frame.grid(row=2, column=2, sticky="n", padx=20, pady=10)
        form_frame.grid_columnconfigure(0, weight=0)
        form_frame.grid_columnconfigure(1, weight=1)

        row_index = 0

        aluno_max_label = ctk.CTkLabel(form_frame, text="Limite de Livros para Alunos:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        aluno_max_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        aluno_max_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=45, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 2), "%P"))
        aluno_max_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)

        valor_aluno = str(self.maxaluno) if self.maxaluno is not None else 3
        aluno_max_entry.insert(0, valor_aluno)

        row_index += 1

        prof_max_label = ctk.CTkLabel(form_frame, text="Limite de Livros para Professores:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        prof_max_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        prof_max_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=45, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 2), "%P"))
        prof_max_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)

        valor_prof = str(self.maxprofessor) if self.maxprofessor is not None else 30
        prof_max_entry.insert(0, valor_prof)

        row_index += 1

        due_max_label = ctk.CTkLabel(form_frame, text="Tempo para Devolução (em Dias):", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        due_max_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        due_max_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=45, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 2), "%P"))
        due_max_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)

        valor_due = str(self.datadev) if self.datadev is not None else 15
        due_max_entry.insert(0, valor_due)

        row_index += 1

        confirm_button = ctk.CTkButton(form_frame, text="Confirmar", command=lambda: self.save_config(aluno_max_entry, prof_max_entry, due_max_entry), fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        confirm_button.grid(row=row_index, column=0, sticky="nsew", padx=10, pady=(20, 10))
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

    def save_config(self, a_entry, p_entry, d_entry):
        texto_aluno = a_entry.get()
        texto_prof = p_entry.get()
        texto_due = d_entry.get()

        self.maxaluno = int(texto_aluno) if texto_aluno else None
        self.maxprofessor = int(texto_prof) if texto_prof else None
        self.datadev = int(texto_due) if texto_due else None

        self.save_info()

    def show_admin(self):
        self.clear_main_frame()

        self.main_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=0)

        title = ctk.CTkLabel(self.main_frame, text="ADMINISTRAÇÃO", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, columnspan=3, padx=25, pady=(23, 15), sticky="nw")

        total_livros = self.get_db_count("livros")
        total_usuarios = self.get_db_count("usuarios")

        condicao_pendente = "status = 'Pendente'" 
        total_pendentes = self.get_db_count("emprestimos", condicao_pendente)

        condicao_concluido = "status = 'Devolvido'"
        total_concluidos = self.get_db_count("emprestimos", condicao_concluido)

        condicao_atraso = "status = 'Atrasado'"
        total_atrasados = self.get_db_count("emprestimos", condicao_atraso)

        self.create_dashboard_card("LIVROS \nCADASTRADOS", "📖", total_livros, 2, 0)
        self.create_dashboard_card("USUÁRIOS \nCADASTRADOS", "👤", total_usuarios, 2, 1)
        self.create_dashboard_card("EMPRÉSTIMOS \nPENDENTES", "🕛", total_pendentes, 2, 2)
        self.create_dashboard_card("EMPRÉSTIMOS \nCONCLUÍDOS", "👍", total_concluidos, 2, 3)
        self.create_dashboard_card("EMPRÉSTIMOS \nATRASADOS", "⏱️", total_atrasados, 2, 4)

        self.plus_button = ctk.CTkButton(self.main_frame, text="➕", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=self.toggle_action_menu)
        self.plus_button.grid(row=4, column=4, padx=20, pady=20, sticky="se")

    def create_dashboard_card(self, title, symbol, value, row, column):
        card_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=25, border_width=1, width=200, height=150, border_color=BUTTON_NEUTRAL)
        card_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        card_frame.grid_propagate(False)
        card_frame.pack_propagate(False)

        icon_label = ctk.CTkLabel(card_frame, text=symbol, text_color=YELLOW_COLOR, font=("Arial", 48, "bold"), fg_color="transparent")
        icon_label.pack(pady=5)

        value_label = ctk.CTkLabel(card_frame, text=value, text_color=TEXT_COLOR_BLACK, font=("Arial", 24, "bold"))
        value_label.pack(pady=5)

        title_label = ctk.CTkLabel(card_frame, text=title, text_color="gray", font=("Arial", 10))
        title_label.pack(pady=5)

    def get_db_count(self, table, condition=None):
        cursor = Database.sql.cursor()
        query = f"SELECT COUNT(*) FROM {table}"
        if condition:
            query += f" WHERE {condition}"
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        return str(result[0])
    
    def toggle_action_menu(self):
        if self.action_menu_frame and self.action_menu_frame.winfo_exists():
            self.action_menu_frame.destroy()
            self.action_menu_frame = None
        else:
            self.show_action_menu()

    def show_action_menu(self):
        if self.action_menu_frame and self.action_menu_frame.winfo_exists():
            try:
                self.action_menu_frame.destroy()
            except:
                pass

        self.action_menu_frame = ctk.CTkFrame(self.main_frame, fg_color=BLUE_COLOR, corner_radius=25)
        self.action_menu_frame.place(relx=0.98, rely=0.91, anchor="se")

        self.create_action_menu_button("ADICIONAR LIVRO", self.add_book).pack(pady=5, padx=10, fill="x")
        self.create_action_menu_button("ADICIONAR USUÁRIO", self.add_user).pack(pady=5, padx=10, fill="x")
        self.create_action_menu_button("REALIZAR EMPRÉSTIMO", self.make_loan).pack(pady=5, padx=10, fill="x")

    def create_action_menu_button(self, text, command):
        action_button = ctk.CTkButton(self.action_menu_frame, text=text, command=command, fg_color=YELLOW_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, font=("Arial", 11, "bold"))
        action_button.bind("<Enter>", lambda e: action_button.configure(fg_color=YELLOW_COLOR_HOVER))
        action_button.bind("<Leave>", lambda e: action_button.configure(fg_color=YELLOW_COLOR))

        return action_button

    def on_table_click(self, cell):
        if cell["row"] == 0:
            raw_value = cell["value"]
            
            clean_value = raw_value.replace(" ▲", "").replace(" ▼", "").strip()
            
            column_name = clean_value.lower()

            if self.sort_column == column_name:
                if self.sort_direction == "ASC":
                    self.sort_direction = "DESC"
                else:
                    self.sort_direction = "ASC"
            else:
                self.sort_column = column_name
                self.sort_direction = "ASC"

            self.general_filter()

    def general_filter(self, event=None):
        if event:
            search_text = event.widget.get().strip()
        else:
            search_text = self.search_entry.get().strip()

        cursor = Database.sql.cursor()

        if self.active_button_name == "EMPRÉSTIMOS":
            try:
                hoje = self.date_today.strftime("%Y-%m-%d")
                
                query_update = "UPDATE tb_emprestimos SET status = 'Atrasado' WHERE status = 'Pendente' AND prazo < %s"
                
                cursor.execute(query_update, (hoje,))
                Database.sql.commit()
            except Exception as e:
                print(f"Erro ao atualizar atrasos: {e}")

        if self.active_button_name == "EMPRÉSTIMOS":
            try:
                hoje = self.date_today.strftime("%Y-%m-%d")
                
                query_update = "UPDATE tb_emprestimos SET status = 'Pendente' WHERE status = 'Atrasado' AND prazo > %s"
                
                cursor.execute(query_update, (hoje,))
                Database.sql.commit()
            except Exception as e:
                print(f"Erro ao atualizar atrasos: {e}")

        like = f"%{search_text}%"
        query = ""
        params = ()

        order_clause = f"ORDER BY {self.sort_column} {self.sort_direction}"
        
        match self.active_button_name:
            case "LIVROS":
                if search_text == "":
                    query = f"SELECT * FROM livros {order_clause}"
                else:
                    query = f"""
                        SELECT * FROM livros 
                        WHERE (livro LIKE %s OR autor LIKE %s OR genero LIKE %s OR ano LIKE %s OR editora LIKE %s OR sinopse LIKE %s)
                        {order_clause}
                    """
                    params = (like, like, like, like, like, like)

            case "USUÁRIOS":
                if search_text == "":
                    query = f"SELECT * FROM usuarios {order_clause}"
                else:
                    query = f"""
                        SELECT * FROM usuarios 
                        WHERE (nome LIKE %s OR tipo LIKE %s OR sala LIKE %s OR email LIKE %s OR telefone LIKE %s)
                        {order_clause}
                    """
                    params = (like, like, like, like, like)

            case "EMPRÉSTIMOS":
                if search_text == "":
                    query = f"SELECT * FROM emprestimos WHERE (status = 'Pendente' OR status = 'Atrasado') {order_clause}"
                else:
                    query = f"""
                        SELECT * FROM emprestimos 
                        WHERE (status = 'Pendente' OR status = 'Atrasado') AND (nome LIKE %s OR tipo LIKE %s OR livro LIKE %s OR autor LIKE %s OR ano LIKE %s OR data LIKE %s OR prazo LIKE %s)
                        {order_clause}
                    """
                    params = (like, like, like, like, like, like, like)

            case "DEVOLUÇÕES":
                if search_text == "":
                    query = f"SELECT * FROM emprestimos WHERE (status = 'Devolvido') {order_clause}"
                else:
                    query = f"""
                        SELECT * FROM emprestimos 
                        WHERE (status = 'Devolvido') AND (nome LIKE %s OR tipo LIKE %s OR livro LIKE %s OR autor LIKE %s OR ano LIKE %s OR data LIKE %s OR prazo LIKE %s)
                        {order_clause}
                    """
                    params = (like, like, like, like, like, like, like)
        
        if search_text == "":
            cursor.execute(query)
        else:
            cursor.execute(query, params)

        rows = cursor.fetchall()

        if cursor.description:
            raw_column_names = [desc[0] for desc in cursor.description]
            num_columns = len(raw_column_names)
        else:
             raw_column_names = []
             num_columns = 0

        display_headers = []
        for col in raw_column_names:
            if col.lower() == self.sort_column.lower():
                if self.sort_direction == "ASC":
                    display_headers.append(f"{col.upper()} ▲")
                else:
                    display_headers.append(f"{col.upper()} ▼")
            else:
                display_headers.append(col.upper())

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if len(rows) == 0:
            placeholder = ctk.CTkLabel(self.table_frame, text="Nenhum resultado encontrado.", text_color="gray", font=("Arial", 14, "bold"))
            placeholder.pack(pady=20)
            return

        table_values = [display_headers]
        for row in rows:
            table_values.append(list(row))

        table = CTkTable(master=self.table_frame, row=len(table_values), column=num_columns, values=table_values, command=self.on_table_click, header_color=BLUE_COLOR, text_color=TEXT_COLOR_WHITE, hover_color=BLUE_COLOR_HOVER)
        table.pack(expand=True, fill="both", padx=20, pady=20)

        match self.active_button_name:
            case "LIVROS":
                try:
                    col_names_lower = [c.lower() for c in raw_column_names]
                    quantidade_index = col_names_lower.index('quantidade')
                except ValueError:
                    quantidade_index = -1

                if quantidade_index != -1:
                    for i, row_data in enumerate(rows):
                        quantidade_valor = row_data[quantidade_index]

                        if quantidade_valor < 1:
                            row_visual_index = i + 1
                            
                            table.edit_row(row_visual_index, fg_color="#C53030", hover_color="#9B2C2C")
            case "EMPRÉSTIMOS":
                try:
                    col_names_lower = [c.lower() for c in raw_column_names]
                    status_index = col_names_lower.index('status')
                except ValueError:
                    status_index = -1

                if status_index != -1:
                    for i, row_data in enumerate(rows):
                        status_valor = row_data[status_index]

                        if status_valor == 'Atrasado':
                            row_visual_index = i + 1
                            
                            table.edit_row(row_visual_index, fg_color="#C53030", hover_color="#9B2C2C")

    def show_books(self):
        self.clear_main_frame()

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure((1, 2, 3, 4), weight=0)
        self.main_frame.grid_rowconfigure((0, 2, 3), weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.sort_column = "livro"
        self.sort_direction = "ASC"

        row_index = 0

        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.grid(row=row_index, column=0, sticky="ew", padx=25, pady=(17, 15))
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure((2, 3, 4), weight=0)

        title = ctk.CTkLabel(top_frame, text="LIVROS", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=(0, 20))

        search_frame = ctk.CTkFrame(top_frame, fg_color=LIGHT_PURPLE_COLOR, corner_radius=25)
        search_frame.grid(row=0, column=1, sticky="ew")

        search_icon = ctk.CTkLabel(search_frame, text="🔍", text_color="gray", font=("Arial", 16))
        search_icon.pack(side="left", padx=(10, 2))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar... (ex: Dom Quixote)", border_width=0, fg_color="transparent", text_color=TEXT_COLOR_BLACK, height=30)
        self.search_entry.pack(side="left", expand=True, fill="x", ipady=5)
        self.search_entry.bind("<Return>", self.general_filter)

        filter_button = ctk.CTkButton(search_frame, text="⏷", fg_color="transparent", hover_color=DARK_PURPLE_COLOR, text_color="gray", width=10, font=("Arial", 16), command=None)
        filter_button.pack(side="right", padx=10)

        self.remove_button = ctk.CTkButton(top_frame, text="❌", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=None)
        self.remove_button.grid(row=0, column=2, sticky="e", padx=(12, 12))

        self.edit_button = ctk.CTkButton(top_frame, text="✏", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=None)
        self.edit_button.grid(row=0, column=3, sticky="e", padx=(0, 0))

        self.plus_button = ctk.CTkButton(top_frame, text="➕", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=self.add_book)
        self.plus_button.grid(row=0, column=4, sticky="e", padx=(12, 0))

        row_index += 1

        self.table_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.table_frame.grid(row=row_index, column=0, sticky="nsew", padx=25, pady=(0, 20))

        self.general_filter()

    def add_book(self):
        self.popup_book = ctk.CTkToplevel(self, fg_color="white")
        self.popup_book.title("Adicionar Livro")
        self.popup_book.resizable(False, False)
        self.popup_book.transient(self)
        self.popup_book.grab_set()

        self.popup_book.grid_columnconfigure(0, weight=1)
        self.popup_book.grid_columnconfigure((1, 2, 3, 4), weight=0)
        self.popup_book.grid_rowconfigure((0, 2), weight=0)
        self.popup_book.grid_rowconfigure((1, 3), weight=1)

        form_frame = ctk.CTkFrame(self.popup_book, fg_color="white")
        form_frame.grid(row=2, column=0, sticky="n", padx=20, pady=10)
        form_frame.grid_columnconfigure(0, weight=0)
        form_frame.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(self.popup_book, text="ADICIONAR LIVRO", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 0))

        row_index = 0

        obs_label = ctk.CTkLabel(form_frame, text="Os campos com * são obrigatórios", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        obs_label.grid(row=row_index, column=1, ipady=5)

        row_index += 1

        book_label = ctk.CTkLabel(form_frame, text="*Título: \n(ex: Dom Quixote):", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        book_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        book_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        book_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5)

        row_index += 1

        author_label = ctk.CTkLabel(form_frame, text="*Autor \n(Miguel de Cervantes):", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        author_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        author_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        author_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5)

        row_index += 1

        genre_label = ctk.CTkLabel(form_frame, text="*Gênero \n(ex: Romance):", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        genre_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        genre_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        genre_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5)

        row_index += 1

        editora_label = ctk.CTkLabel(form_frame, text="*Editora \n(ex: Editora Garnier):", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        editora_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        editora_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        editora_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5)

        row_index += 1

        ano_label = ctk.CTkLabel(form_frame, text="*Ano: \n(ex: 1605)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        ano_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        ano_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=59, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 4), "%P"))
        ano_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)

        row_index += 1

        quant_label = ctk.CTkLabel(form_frame, text="*Quantidade: \n(ex: 10)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        quant_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        quant_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=53, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 3), "%P"))
        quant_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)

        row_index += 1

        sinop_label = ctk.CTkLabel(form_frame, text="Sinopse:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        sinop_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        sinop_entry = ctk.CTkTextbox(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, height=100, corner_radius=25)
        sinop_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5)
        sinop_entry._textbox.configure(padx=0, pady=0, spacing1=0, spacing2=0, spacing3=0)

        row_index += 1

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=row_index, column=1, columnspan=2, pady=(20, 10))

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=lambda: self.popup_book.destroy(), fg_color=BUTTON_NEUTRAL, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        cancel_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=(0, 10))
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=BUTTON_NEUTRAL))

        confirm_button = ctk.CTkButton(button_frame, text="Confirmar", command=lambda: self.add_book_to_db(book_entry, author_entry, genre_entry, ano_entry, editora_entry, quant_entry, sinop_entry), fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        confirm_button.grid(row=0, column=1, sticky="nsew", padx=10, pady=(0, 10))
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

    def add_book_to_db(self, e_livro, e_autor, e_genero, e_ano, e_editora, e_quant, e_sinopse):
        livro = e_livro.get().strip()
        autor = e_autor.get().strip()
        genero = e_genero.get().strip()
        ano = e_ano.get().strip()
        editora = e_editora.get().strip()
        quantidade = e_quant.get().strip()
        sinopse = e_sinopse.get("0.0", "end").strip()

        if not livro or not autor or not genero or not ano or not editora or not quantidade:
            messagebox.showerror("Erro", "Por favor, preencha os campos obrigatórios (*).")
            return
        
        try:
            ano_int = int(ano)
            quant_int = int(quantidade)
        except ValueError:
            messagebox.showerror("Erro", "Ano e Quantidade devem ser números válidos.")
            return
        
        try:
            query = """
                INSERT INTO tb_livros (livro, autor, genero, ano, editora, quantidade, sinopse)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (livro, autor, genero, ano_int, editora, quant_int, sinopse)
            
            self.confirm_button("books", query, values)

        except Exception as e:
            messagebox.showerror("Erro no Banco de Dados", f"Não foi possível cadastrar o livro.\nErro: {e}")

    def show_users(self):
        self.clear_main_frame()

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure((1, 2, 3, 4), weight=0)
        self.main_frame.grid_rowconfigure((0, 2, 3), weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.sort_column = "nome"
        self.sort_direction = "ASC"

        row_index = 0

        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.grid(row=row_index, column=0, sticky="ew", padx=25, pady=(17, 15))
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure((2, 3, 4), weight=0)

        title = ctk.CTkLabel(top_frame, text="USUÁRIOS", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=(0, 20))

        search_frame = ctk.CTkFrame(top_frame, fg_color=LIGHT_PURPLE_COLOR, corner_radius=25)
        search_frame.grid(row=0, column=1, sticky="ew")

        search_icon = ctk.CTkLabel(search_frame, text="🔍", text_color="gray", font=("Arial", 16))
        search_icon.pack(side="left", padx=(10, 2))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar... (ex: Guilherme Menezes Silva)", border_width=0, fg_color="transparent", text_color=TEXT_COLOR_BLACK, height=30)
        self.search_entry.pack(side="left", expand=True, fill="x", ipady=5)
        self.search_entry.bind("<Return>", self.general_filter)

        filter_button = ctk.CTkButton(search_frame, text="⏷", fg_color="transparent", hover_color=DARK_PURPLE_COLOR, text_color="gray", width=10, font=("Arial", 16), command=None)
        filter_button.pack(side="right", padx=10)

        self.remove_button = ctk.CTkButton(top_frame, text="❌", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=None)
        self.remove_button.grid(row=0, column=2, sticky="e", padx=(12, 12))

        self.edit_button = ctk.CTkButton(top_frame, text="✏", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=None)
        self.edit_button.grid(row=0, column=3, sticky="e", padx=(0, 0))

        self.plus_button = ctk.CTkButton(top_frame, text="➕", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=self.add_user)
        self.plus_button.grid(row=0, column=4, sticky="e", padx=(12, 0))

        row_index += 1

        self.table_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.table_frame.grid(row=row_index, column=0, sticky="nsew", padx=25, pady=(0, 20))

        self.general_filter()

    def add_user(self):
        self.popup_user = ctk.CTkToplevel(self, fg_color="white")
        self.popup_user.title("Adicionar Usuário")
        self.popup_user.resizable(False, False)
        self.popup_user.transient(self)
        self.popup_user.grab_set()

        self.popup_user.grid_columnconfigure(0, weight=1)
        self.popup_user.grid_columnconfigure((1, 2, 3, 4), weight=0)
        self.popup_user.grid_rowconfigure((0, 2), weight=0)
        self.popup_user.grid_rowconfigure((1, 3), weight=1)

        form_frame = ctk.CTkFrame(self.popup_user, fg_color="white")
        form_frame.grid(row=2, column=0, sticky="n", padx=20, pady=10)
        form_frame.grid_columnconfigure(0, weight=0)
        form_frame.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(self.popup_user, text="ADICIONAR USUÁRIO", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 0))

        row_index = 0

        obs_label = ctk.CTkLabel(form_frame, text="Os campos com * são obrigatórios", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        obs_label.grid(row=row_index, column=1, ipady=5)

        row_index += 1

        name_label = ctk.CTkLabel(form_frame, text="*Nome Completo: \n(ex: Guilherme Menezes Silva)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        name_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        nome_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        nome_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5)

        row_index += 1

        type_label = ctk.CTkLabel(form_frame, text="*Tipo de Usuário: \n(ex: Aluno)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        type_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        type_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        type_frame.grid(row=row_index, column=1, sticky="w", pady=15)

        user_type = ctk.StringVar(value="Aluno")

        row_index += 1

        email_aluno_label = ctk.CTkLabel(form_frame, text="*RA: \n(ex: 1199887766)", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        email_aluno_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        general_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        general_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5)

        email_prof_label = ctk.CTkLabel(form_frame, text="*Email: \n(ex: guilherme@email.com)", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        email_prof_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))
        email_prof_label.grid_remove()

        row_index += 1

        room_label = ctk.CTkLabel(form_frame, text="*Série: \n(ex: 3TA)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        room_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        room_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=53, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 3), "%P"))
        room_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        
        def toggle_fields():
            if user_type.get() == "Aluno":
                email_aluno_label.grid()
                room_label.grid()
                room_entry.grid()

                email_prof_label.grid_remove()

            else:
                email_aluno_label.grid_remove()
                room_label.grid_remove()
                room_entry.grid_remove()

                email_prof_label.grid()

        aluno_button = ctk.CTkRadioButton(type_frame, text="Aluno", variable=user_type, value="Aluno", command=toggle_fields, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        aluno_button.pack(side="left")

        professor_button = ctk.CTkRadioButton(type_frame, text="Professor", variable=user_type, value="Professor", fg_color=BLUE_COLOR, command=toggle_fields, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        professor_button.pack(side="left")

        row_index += 1

        telefone_label = ctk.CTkLabel(form_frame, text="Telefone: \n(ex: 11987654321)", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        telefone_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        telefone_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        telefone_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5)

        row_index += 1

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=row_index, column=1, pady=(20, 10))

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=lambda: self.popup_user.destroy(), fg_color=BUTTON_NEUTRAL, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        cancel_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=(0, 10))
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=BUTTON_NEUTRAL))

        confirm_button = ctk.CTkButton(button_frame, text="Confirmar", command=lambda: self.add_user_to_db(nome_entry, user_type, general_entry, room_entry, telefone_entry), fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        confirm_button.grid(row=0, column=1, sticky="nsew", padx=10, pady=(0, 10))
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

    def add_user_to_db(self, e_nome, v_tipo, e_geral, e_sala, e_tel):
        nome = e_nome.get().strip()
        tipo = v_tipo.get()
        dado_geral = e_geral.get().strip()
        sala = e_sala.get().strip()
        telefone = e_tel.get().strip()

        if not nome or not dado_geral:
            messagebox.showerror("Erro", "Por favor, preencha os campos obrigatórios (*).")
            return
        
        if tipo == "Aluno":
            if not sala:
                messagebox.showerror("Erro", "Para alunos, a série é obrigatória.")
                return
        else:
            sala = None
        
        try:
            query = """
                INSERT INTO tb_usuarios (nome, tipo, sala, email, telefone)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (nome, tipo, sala, dado_geral, telefone)
   
            self.confirm_button("users", query, values) 

        except Exception as e:
            messagebox.showerror("Erro no Banco de Dados", f"Não foi possível cadastrar o usuário.\nErro: {e}")

    def show_loans(self):
        self.clear_main_frame()

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure((1, 2, 3, 4), weight=0)
        self.main_frame.grid_rowconfigure((0, 2, 3), weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.sort_column = "data"
        self.sort_direction = "DESC"

        row_index = 0

        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.grid(row=row_index, column=0, sticky="ew", padx=25, pady=(17, 15))
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure((2, 3, 4), weight=0)

        title = ctk.CTkLabel(top_frame, text="EMPRÉSTIMOS", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=(0, 20))

        search_frame = ctk.CTkFrame(top_frame, fg_color=LIGHT_PURPLE_COLOR, corner_radius=25)
        search_frame.grid(row=0, column=1, sticky="ew")

        search_icon = ctk.CTkLabel(search_frame, text="🔍", text_color="gray", font=("Arial", 16))
        search_icon.pack(side="left", padx=(10, 2))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar... (ex: 15112025)", border_width=0, fg_color="transparent", text_color=TEXT_COLOR_BLACK, height=30)
        self.search_entry.pack(side="left", expand=True, fill="x", ipady=5)
        self.search_entry.bind("<Return>", self.general_filter)

        filter_button = ctk.CTkButton(search_frame, text="⏷", fg_color="transparent", hover_color=DARK_PURPLE_COLOR, text_color="gray", width=10, font=("Arial", 16), command=None)
        filter_button.pack(side="right", padx=10)

        self.remove_button = ctk.CTkButton(top_frame, text="❌", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=self.delete_loan)
        self.remove_button.grid(row=0, column=2, sticky="e", padx=(12, 12))

        self.edit_button = ctk.CTkButton(top_frame, text="✏", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=self.edit_loan)
        self.edit_button.grid(row=0, column=3, sticky="e", padx=(0, 0))

        self.plus_button = ctk.CTkButton(top_frame, text="➕", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=self.make_loan)
        self.plus_button.grid(row=0, column=4, sticky="e", padx=(12, 0))

        row_index += 1

        self.table_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.table_frame.grid(row=row_index, column=0, sticky="nsew", padx=25, pady=(0, 20))

        self.general_filter()

    def make_loan(self):
        self.popup_loan = ctk.CTkToplevel(self, fg_color="white")
        self.popup_loan.title("Realizar Empréstimo")
        self.popup_loan.resizable(False, False)
        self.popup_loan.transient(self)
        self.popup_loan.grab_set()

        self.popup_loan.grid_columnconfigure(0, weight=1)
        self.popup_loan.grid_columnconfigure((1, 2, 3, 4), weight=0)
        self.popup_loan.grid_rowconfigure((0, 2), weight=0)
        self.popup_loan.grid_rowconfigure((1, 3), weight=1)

        title = ctk.CTkLabel(self.popup_loan, text="REALIZAR EMPRÉSTIMO", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 0))

        form_frame = ctk.CTkFrame(self.popup_loan, fg_color="white")
        form_frame.grid(row=2, column=0, sticky="n", padx=20, pady=10)
        form_frame.grid_columnconfigure(0, weight=0)
        form_frame.grid_columnconfigure(1, weight=1)

        row_index = 0

        obs_label = ctk.CTkLabel(form_frame, text="Os campos com * são obrigatórios", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        obs_label.grid(row=row_index, column=1, ipady=5)

        row_index += 1

        name_label = ctk.CTkLabel(form_frame, text="*Nome do Usuário: \n(ex: Guilherme Menezes Silva)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        name_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        name_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        name_container.grid(row=row_index, column=1, pady=(10, 5))

        nome_entry = ctk.CTkEntry(name_container, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300,  corner_radius=25)
        nome_entry.pack(side="left", pady=(10, 5), ipady=5)
        nome_entry.bind("<Return>", lambda e: self.add_search_user_data(nome_entry, user_type, general_entry, toggle_fields))

        btn_search_user = ctk.CTkButton(name_container, text="Buscar", width=50, corner_radius=25, fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, command=lambda: self.add_search_user_data(nome_entry, user_type, general_entry, toggle_fields))
        btn_search_user.pack(side="left", padx=(10, 0), pady=(10, 5), ipady=5)
        btn_search_user.bind("<Enter>", lambda e: btn_search_user.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        btn_search_user.bind("<Leave>", lambda e: btn_search_user.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        row_index += 1

        type_label = ctk.CTkLabel(form_frame, text="Tipo do Usuário:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        type_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        type_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        type_frame.grid(row=row_index, column=1, pady=15, sticky="w")

        user_type = ctk.StringVar(value="Aluno")

        row_index += 1

        email_aluno_label = ctk.CTkLabel(form_frame, text="RA do Usuário:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        email_aluno_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        general_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        general_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5, sticky="w")
        general_entry.configure(state="disabled")

        email_prof_label = ctk.CTkLabel(form_frame, text="Email do Usuário:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        email_prof_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))
        email_prof_label.grid_remove()

        def toggle_fields():
            if user_type.get() == "Aluno":
                email_aluno_label.grid()
                email_prof_label.grid_remove()

            else:
                email_aluno_label.grid_remove()
                email_prof_label.grid()

        self.aluno_button = ctk.CTkRadioButton(type_frame, text="Aluno", text_color_disabled=TEXT_COLOR_BLACK, variable=user_type, value="Aluno", command=toggle_fields, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        self.aluno_button.pack(side="left")
        self.aluno_button.configure(state="disabled")

        self.professor_button = ctk.CTkRadioButton(type_frame, text="Professor", text_color_disabled=TEXT_COLOR_BLACK, variable=user_type, value="Professor", fg_color=BLUE_COLOR, command=toggle_fields, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        self.professor_button.pack(side="left")
        self.professor_button.configure(state="disabled")

        row_index += 1        

        book_label = ctk.CTkLabel(form_frame, text="*Título do Livro: \n(ex: Dom Quixote)", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        book_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        book_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        book_container.grid(row=row_index, column=1, pady=(10, 5))

        book_entry = ctk.CTkEntry(book_container, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        book_entry.pack(side="left", pady=(10, 5), ipady=5)
        book_entry.bind("<Return>", lambda e: self.add_search_book_data(book_entry, autor_entry, ano_entry, editora_entry))

        btn_search_book = ctk.CTkButton(book_container, text="Buscar", width=50, corner_radius=25, fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, command=lambda: self.add_search_book_data(book_entry, autor_entry, ano_entry, editora_entry))
        btn_search_book.pack(side="left", padx=(10, 0), pady=(10, 5), ipady=5)
        btn_search_book.bind("<Enter>", lambda e: btn_search_book.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        btn_search_book.bind("<Leave>", lambda e: btn_search_book.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        row_index += 1

        autor_label = ctk.CTkLabel(form_frame, text="Nome do Autor:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        autor_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        autor_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        autor_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        autor_entry.configure(state="disabled")

        row_index += 1

        ano_label = ctk.CTkLabel(form_frame, text="Ano do Livro:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        ano_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        ano_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=59, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 4), "%P"))
        ano_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        ano_entry.configure(state="disabled")

        row_index += 1

        editora_label = ctk.CTkLabel(form_frame, text="Editora do Livro:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        editora_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        editora_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        editora_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        editora_entry.configure(state="disabled")

        row_index += 1

        quant_label = ctk.CTkLabel(form_frame, text="*Quantidade: \n(ex: 2)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        quant_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        quant_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=53, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 3), "%P"))
        quant_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5, sticky="w")

        row_index += 1

        date_label = ctk.CTkLabel(form_frame, text="Data do Empréstimo:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        date_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        date_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=87, corner_radius=25)
        date_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)

        date_entry_today = self.date_today.strftime("%d%m%Y")
        date_entry.delete(0, "end")
        date_entry.insert(0, date_entry_today)
        date_entry.configure(state="disabled")
    
        row_index += 1

        due_label = ctk.CTkLabel(form_frame, text="Prazo de Devolução:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        due_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        due_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=87, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 8), "%P"))
        due_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        
        if self.datadev == None:
            due_entry.configure(state="normal")
        else:
            due_entry_past = self.date_today + timedelta(days=self.datadev)
            due_entry_future = due_entry_past.strftime("%d%m%Y") 
            due_entry.delete(0, "end")
            due_entry.insert(0, due_entry_future)
            due_entry.configure(state="disabled")

        row_index += 1

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=row_index, column=1, columnspan=2, pady=(20, 10))

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=lambda: self.popup_loan.destroy(), fg_color=BUTTON_NEUTRAL, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        cancel_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=(0, 10))
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=BUTTON_NEUTRAL))

        confirm_button = ctk.CTkButton(button_frame, text="Confirmar", command=lambda: self.make_loan_to_db(nome_entry, user_type, general_entry, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry), fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        confirm_button.grid(row=0, column=1, sticky="nsew", padx=10, pady=(0, 10))
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

    def make_loan_to_db(self, e_nome, v_tipo, e_geral, e_livro, e_autor, e_ano, e_editora, e_quant, e_data, e_prazo):
        nome = e_nome.get().strip()
        tipo_selecionado = v_tipo.get()
        dado_geral = e_geral.get().strip()
        livro_nome = e_livro.get().strip()
        autor_nome = e_autor.get().strip()
        livro_ano = e_ano.get().strip()
        editora_nome = e_editora.get().strip()
        quantidade = e_quant.get().strip()
        data_str = e_data.get().strip()
        prazo_str = e_prazo.get().strip()

        if not nome or not dado_geral or not livro_nome or not autor_nome or not livro_ano or not editora_nome or not quantidade or not data_str or not prazo_str:
            messagebox.showerror("Erro", "Por favor, preencha os campos obrigatórios (*).")
            return
        
        try:
            quant_int = int(quantidade)
            if quant_int <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser maior que 0.")
                return
            
            if tipo_selecionado == "Aluno" and quant_int > self.maxaluno:
                messagebox.showerror("Limite Excedido", f"Alunos podem retirar no máximo {self.maxaluno} exemplar(es) por vez.")
                return
            
            if tipo_selecionado == "Professor" and quant_int > self.maxprofessor:
                messagebox.showerror("Limite Excedido", f"Professores podem retirar no máximo {self.maxprofessor} exemplar(es) por vez.")
                return
            data_fmt = datetime.strptime(data_str, "%d%m%Y").strftime("%Y-%m-%d")
            prazo_fmt = datetime.strptime(prazo_str, "%d%m%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Datas inválidas (use DDMMAAAA) ou quantidade inválida.")
            return
        
        try:
            cursor = Database.sql.cursor()

            query_user = "SELECT id_usa, tipo FROM tb_usuarios WHERE nome = %s"
            
            cursor.execute(query_user, (nome,))
            user_res = cursor.fetchone()
            
            id_usa = user_res[0]

            query_book = "SELECT id_liv, quantidade FROM tb_livros WHERE (livro = %s AND autor = %s AND ano = %s AND editora = %s)"
            cursor.execute(query_book, (livro_nome, autor_nome, livro_ano, editora_nome))
            book_res = cursor.fetchone()
            
            id_liv, estoque_atual = book_res

            if quant_int > estoque_atual:
                messagebox.showerror("Estoque Insuficiente", f"Não há exemplares suficientes.\nEstoque atual: {estoque_atual}\nSolicitado: {quant_int}")
                return

            query_insert = """
                INSERT INTO tb_emprestimos (id_usa, id_liv, quantidade, data, prazo, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (id_usa, id_liv, quant_int, data_fmt, prazo_fmt, "Pendente")
            query_update_stock = "UPDATE tb_livros SET quantidade = quantidade - %s WHERE id_liv = %s"
            values_update = (quant_int, id_liv)

            self.confirm_button_add_loan(query_insert, values, query_update_stock, values_update)

        except Exception as e:
            messagebox.showerror("Erro no Banco", f"Falha ao realizar empréstimo: {e}")

    def add_search_user_data(self, nome_entry, user_type, general_entry, func_toggle):
        nome_busca = nome_entry.get().strip()
        
        if not nome_busca:
            return

        try:
            cursor = Database.sql.cursor()
            sql_parts = []
            params = []

            if nome_busca:
                sql_parts.append("nome LIKE %s")
                params.append(f"%{nome_busca}%")

            if not sql_parts: return
            
            query_conditions = " AND ".join(sql_parts)

            query = f"SELECT nome, tipo, email FROM tb_usuarios WHERE {query_conditions}"
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Busca", "Usuário não encontrado.")
            
            elif len(results) == 1:
                self.add_fill_user_fields(results[0], nome_entry, user_type, general_entry, func_toggle)
            
            else:
                self.add_show_user_selection(results, nome_entry, user_type, general_entry, func_toggle)
        
        except Exception as e:
            print(f"Erro na busca: {e}")

    def add_show_user_selection(self, users_list, nome_entry, user_type, general_entry, func_toggle):
        selection_popup = ctk.CTkToplevel(self, fg_color="white")
        selection_popup.title("Selecionar Usuário")
        selection_popup.geometry("600x350")
        selection_popup.resizable(False, False)
        selection_popup.transient(self.popup_loan)
        selection_popup.grab_set()

        if hasattr(self, 'popup_loan') and self.popup_loan.winfo_exists():
            selection_popup.transient(self.popup_loan)
        
        selection_popup.grab_set()

        title = ctk.CTkLabel(selection_popup, text="Múltiplos usuários encontrados.\nSelecione um:", text_color=TEXT_COLOR_BLACK, font=("Arial", 16, "bold"))
        title.pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(selection_popup, width=600, height=350)
        scroll_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        for user in users_list:
            u_nome, u_tipo, u_dado = user

            label_dado = "RA" if u_tipo == "Aluno" else "Email"
            btn_text = f"{u_nome} | {u_tipo} | {label_dado}: {u_dado}"

            btn = ctk.CTkButton(scroll_frame, text=btn_text, fg_color=BLUE_COLOR, anchor="w",height=40,command=lambda u=user, p=selection_popup: self.add_select_user_and_close(u, p, nome_entry, user_type, general_entry, func_toggle))
            btn.pack(pady=5, padx=5, fill="x")

    def add_select_user_and_close(self, user_data, popup, *args):
        popup.destroy()
        self.add_fill_user_fields(user_data, *args)

    def add_fill_user_fields(self, user_data, nome_entry, user_type, general_entry, func_toggle):
        nome_found, tipo_found, email_found = user_data

        nome_entry.delete(0, "end")
        nome_entry.insert(0, nome_found)

        self.update_disabled_entry(general_entry, email_found)

        self.aluno_button.configure(state="normal")
        self.professor_button.configure(state="normal")

        user_type.set(tipo_found)
        func_toggle()

        self.aluno_button.configure(state="disabled")
        self.professor_button.configure(state="disabled")

    def add_search_book_data(self, book_entry, autor_entry, ano_entry, editora_entry):
        livro_busca = book_entry.get().strip()
        
        if not livro_busca:
            return

        try:
            cursor = Database.sql.cursor()
            sql_parts = []
            params = []

            if livro_busca:
                sql_parts.append("livro LIKE %s")
                params.append(f"%{livro_busca}%")

            if not sql_parts: return
            
            query_conditions = " AND ".join(sql_parts)

            query = f"SELECT livro, autor, ano, editora FROM tb_livros WHERE {query_conditions}"
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Busca", "Livro não encontrado.")
            
            elif len(results) == 1:
                self.add_fill_book_fields(results[0], book_entry, autor_entry, ano_entry, editora_entry)
            
            else:
                self.add_show_book_selection(results, book_entry, autor_entry, ano_entry, editora_entry)
        
        except Exception as e:
            print(f"Erro na busca de livro: {e}")

    def add_show_book_selection(self, books_list, book_entry, autor_entry, ano_entry, editora_entry):
        selection_popup = ctk.CTkToplevel(self, fg_color="white")
        selection_popup.title("Selecionar Livro")
        selection_popup.geometry("600x350")
        selection_popup.resizable(False, False)
        selection_popup.transient(self.popup_loan)
        selection_popup.grab_set()
        
        if hasattr(self, 'popup_loan') and self.popup_loan.winfo_exists():
            selection_popup.transient(self.popup_loan)
        else:
            selection_popup.transient(self)
        
        selection_popup.grab_set()

        title = ctk.CTkLabel(selection_popup, text="Múltiplos livros encontrados.\nSelecione um:", text_color=TEXT_COLOR_BLACK, font=("Arial", 16, "bold"))
        title.pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(selection_popup, width=600, height=350)
        scroll_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        for book in books_list:
            b_titulo, b_autor, b_ano, b_editora = book

            btn_text = f"{b_titulo} | {b_autor} | {b_ano} | {b_editora}"

            btn = ctk.CTkButton(scroll_frame, text=btn_text, fg_color=BLUE_COLOR, anchor="w", height=40,command=lambda b=book, p=selection_popup: self.add_select_book_and_close(b, p, book_entry, autor_entry, ano_entry, editora_entry))
            btn.pack(pady=5, padx=5, fill="x")

    def add_select_book_and_close(self, book_data, popup, *args):
        popup.destroy()
        self.add_fill_book_fields(book_data, *args)

    def add_fill_book_fields(self, book_data, book_entry, autor_entry, ano_entry, editora_entry):
        titulo_found, autor_found, ano_found, editora_found = book_data

        book_entry.delete(0, "end")
        book_entry.insert(0, titulo_found)

        self.update_disabled_entry(autor_entry, autor_found)
        self.update_disabled_entry(ano_entry, ano_found)
        self.update_disabled_entry(editora_entry, editora_found)

    def edit_loan(self):
        self.popup_loan = ctk.CTkToplevel(self, fg_color="white")
        self.popup_loan.title("Editar Empréstimo")
        self.popup_loan.resizable(False, False)
        self.popup_loan.transient(self)
        self.popup_loan.grab_set()

        self.popup_loan.grid_columnconfigure(0, weight=1)
        self.popup_loan.grid_columnconfigure((1, 2, 3, 4), weight=0)
        self.popup_loan.grid_rowconfigure((0, 2), weight=0)
        self.popup_loan.grid_rowconfigure((1, 3), weight=1)

        form_frame = ctk.CTkFrame(self.popup_loan, fg_color="white")
        form_frame.grid(row=2, column=0, sticky="n", padx=20, pady=10)
        form_frame.grid_columnconfigure(0, weight=0)
        form_frame.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(self.popup_loan, text="EDITAR EMPRÉSTIMO", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 0))

        row_index = 0

        obs_label = ctk.CTkLabel(form_frame, text="Os campos com * são obrigatórios", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        obs_label.grid(row=row_index, column=1, ipady=5)

        row_index += 1

        name_label = ctk.CTkLabel(form_frame, text="*Nome Completo: \n(ex: Guilherme Menezes Silva)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        name_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        name_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        name_container.grid(row=row_index, column=1, pady=(10, 5))

        nome_entry = ctk.CTkEntry(name_container, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300,  corner_radius=25)
        nome_entry.pack(side="left", pady=(10, 5), ipady=5)
        nome_entry.bind("<Return>", lambda e: self.edit_search_loan_data(nome_entry, user_type, general_entry, toggle_fields, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type))

        btn_search_user = ctk.CTkButton(name_container, text="Buscar", width=50, corner_radius=25, fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, command=lambda: self.edit_search_loan_data(nome_entry, user_type, general_entry, toggle_fields, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type))
        btn_search_user.pack(side="left", padx=(10, 0), pady=(10, 5), ipady=5)
        btn_search_user.bind("<Enter>", lambda e: btn_search_user.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        btn_search_user.bind("<Leave>", lambda e: btn_search_user.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        row_index += 1

        type_label = ctk.CTkLabel(form_frame, text="Tipo de Usuário:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        type_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        type_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        type_frame.grid(row=row_index, column=1, pady=15, sticky="w")

        user_type = ctk.StringVar(value="Aluno")

        row_index += 1

        email_aluno_label = ctk.CTkLabel(form_frame, text="RA:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        email_aluno_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        general_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        general_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5, sticky="w")
        general_entry.configure(state="disabled")

        email_prof_label = ctk.CTkLabel(form_frame, text="Email:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        email_prof_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))
        email_prof_label.grid_remove()

        def toggle_fields():
            if user_type.get() == "Aluno":
                email_aluno_label.grid()
                email_prof_label.grid_remove()

            else:
                email_aluno_label.grid_remove()
                email_prof_label.grid()

        self.aluno_button = ctk.CTkRadioButton(type_frame, text="Aluno", text_color_disabled=TEXT_COLOR_BLACK, variable=user_type, value="Aluno", command=toggle_fields, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        self.aluno_button.pack(side="left")
        self.aluno_button.configure(state="disabled")

        self.professor_button = ctk.CTkRadioButton(type_frame, text="Professor", text_color_disabled=TEXT_COLOR_BLACK, variable=user_type, value="Professor", fg_color=BLUE_COLOR, command=toggle_fields, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        self.professor_button.pack(side="left")
        self.professor_button.configure(state="disabled")

        row_index += 1        

        book_label = ctk.CTkLabel(form_frame, text="Título do Livro:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        book_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        book_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        book_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        book_entry.configure(state="disabled")

        row_index += 1

        autor_label = ctk.CTkLabel(form_frame, text="Nome do Autor:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        autor_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        autor_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        autor_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        autor_entry.configure(state="disabled")

        row_index += 1

        ano_label = ctk.CTkLabel(form_frame, text="Ano do Livro:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        ano_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        ano_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=59, corner_radius=25)
        ano_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        ano_entry.configure(state="disabled")

        row_index += 1

        editora_label = ctk.CTkLabel(form_frame, text="Editora do Livro:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        editora_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        editora_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        editora_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        editora_entry.configure(state="disabled")

        row_index += 1

        quant_label = ctk.CTkLabel(form_frame, text="*Quantidade: \n (ex: 2)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        quant_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        quant_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=53, corner_radius=25, validate="key")
        quant_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5, sticky="w")

        row_index += 1

        date_label = ctk.CTkLabel(form_frame, text="*Data do Empréstimo: \n(ex 15112025)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        date_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        date_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=87, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 8), "%P"))
        date_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
    
        row_index += 1

        due_label = ctk.CTkLabel(form_frame, text="*Prazo de Devolução: \n(ex: 25112025)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        due_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        due_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=87, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 8), "%P"))
        due_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)

        row_index += 1
        
        status_label = ctk.CTkLabel(form_frame, text="*Status do Empréstimo: \n(ex: Pendente)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        status_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        status_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        status_frame.grid(row=row_index, column=1, pady=15, sticky="w")

        status_type = ctk.StringVar(value="Pendente")

        pendente_button = ctk.CTkRadioButton(status_frame, text="Pendente", text_color_disabled=TEXT_COLOR_BLACK, variable=status_type, value="Pendente", fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        pendente_button.pack(side="left")

        devolvido_button = ctk.CTkRadioButton(status_frame, text="Devolvido", text_color_disabled=TEXT_COLOR_BLACK, variable=status_type, value="Devolvido", fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        devolvido_button.pack(side="left")

        atrasado_button = ctk.CTkRadioButton(status_frame, text="Atrasado", text_color_disabled=TEXT_COLOR_BLACK, variable=status_type, value="Atrasado", fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        atrasado_button.pack(side="left")
        atrasado_button.configure(state="disabled")

        row_index += 1

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=row_index, column=1, columnspan=2, pady=(20, 10))

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=lambda: self.popup_loan.destroy(), fg_color=BUTTON_NEUTRAL, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        cancel_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=(0, 10))
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=BUTTON_NEUTRAL))

        confirm_button = ctk.CTkButton(button_frame, text="Confirmar", command=lambda: self.save_loan_changes(quant_entry, date_entry, due_entry, status_type), fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        confirm_button.grid(row=0, column=1, sticky="nsew", padx=10, pady=(0, 10))
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

    def save_loan_changes(self, quant_entry, date_entry, due_entry, status_type):
        if not hasattr(self, 'current_loan_id') or self.current_loan_id is None:
            messagebox.showwarning("Aviso", "Nenhum empréstimo foi selecionado para edição.")
            return

        nova_quant = quant_entry.get()
        nova_data = date_entry.get()
        novo_prazo = due_entry.get()
        novo_status = status_type.get()

        if not nova_quant or not nova_data or not novo_prazo:
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        try:
            dt_emprestimo = datetime.strptime(nova_data, "%d%m%Y").strftime("%Y-%m-%d")
            dt_devolucao = datetime.strptime(novo_prazo, "%d%m%Y").strftime("%Y-%m-%d")

            query_update = """
                UPDATE tb_emprestimos 
                SET quantidade = %s, data = %s, prazo = %s, status = %s 
                WHERE id_emp = %s
            """
            values = (nova_quant, dt_emprestimo, dt_devolucao, novo_status, self.current_loan_id)

            if novo_status == "Devolvido":
                query_stock = "UPDATE tb_livros SET quantidade = quantidade + %s WHERE id_liv = %s"
                values_stock = (self.current_loan_quant, self.current_book_id)

            self.confirm_button_edit_loan(query_update, values, query_stock, values_stock)

        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use apenas números (DDMMAAAA).")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar o banco de dados: {e}")

    def edit_search_loan_data(self, nome_entry, user_type, general_entry, func_toggle, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type):
        nome_busca = nome_entry.get().strip()
        
        if not nome_busca:
            return

        try:
            cursor = Database.sql.cursor()
            query = f"SELECT id_usa, nome, tipo, email FROM tb_usuarios WHERE nome LIKE %s"
            cursor.execute(query, (f"%{nome_busca}%",))
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Busca", "Usuário não encontrado.")
            
            elif len(results) == 1:
                self.continue_edit_with_user(results[0], nome_entry, user_type, general_entry, func_toggle, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type)
            
            else:
                self.edit_show_user_selection(results, nome_entry, user_type, general_entry, func_toggle, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type)
        
        except Exception as e:
            print(f"Erro na busca: {e}")

    def edit_show_user_selection(self, users_list, *args):
        selection_popup = ctk.CTkToplevel(self, fg_color="white")
        selection_popup.title("Selecionar Usuário")
        selection_popup.geometry("650x350")
        selection_popup.resizable(False, False)
        selection_popup.transient(self.popup_loan)
        selection_popup.grab_set()

        title = ctk.CTkLabel(selection_popup, text="Múltiplos usuários encontrados.\nSelecione um:", text_color=TEXT_COLOR_BLACK, font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        scroll_frame = ctk.CTkScrollableFrame(selection_popup, width=600, height=350)
        scroll_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        for user in users_list:
            id_usa, u_nome, u_tipo, u_dado = user

            label_dado = "RA" if u_tipo == "Aluno" else "Email"
            btn_text = f"{u_nome} | {u_tipo} | {label_dado}: {u_dado}"
            
            btn = ctk.CTkButton(scroll_frame, text=btn_text, fg_color=BLUE_COLOR, anchor="w", height=40,command=lambda u=user, p=selection_popup: [p.destroy(), self.continue_edit_with_user(u, *args)])
            btn.pack(pady=5, padx=5, fill="x")

    def continue_edit_with_user(self, user_result, nome_entry, user_type, general_entry, func_toggle, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type):
        try:
            id_usa, nome, tipo, email = user_result

            nome_entry.delete(0, "end")
            nome_entry.insert(0, nome)

            self.aluno_button.configure(state="normal")
            self.professor_button.configure(state="normal")

            user_type.set(tipo)
            func_toggle()

            self.aluno_button.configure(state="disabled")
            self.professor_button.configure(state="disabled")

            self.update_disabled_entry(general_entry, email)

            cursor = Database.sql.cursor()
            query_emp = f"""
                SELECT E. id_emp, E.id_liv, E.quantidade, E.data, E.prazo, L.livro, L.autor, L.ano, L.editora, E.status
                FROM tb_emprestimos E
                JOIN tb_livros L ON E.id_liv = L.id_liv
                WHERE E.id_usa = {id_usa}
                AND E.status IN ('Pendente', 'Atrasado')
            """
            cursor.execute(query_emp)
            loans_result = cursor.fetchall()

            if not loans_result:
                messagebox.showinfo("Info", "Este usuário não possui empréstimos ativos.")
            
            elif len(loans_result) == 1:
                self.edit_fill_loan_fields(loans_result[0], book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type)
            
            else:
                self.edit_show_loan_selection(loans_result, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type)

        except Exception as e:
            print(f"Erro ao carregar empréstimos: {e}")

    def edit_show_loan_selection(self, loans_list, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type):
        selection_popup = ctk.CTkToplevel(self, fg_color="white")
        selection_popup.title("Selecionar Empréstimo")
        selection_popup.geometry("750x350")
        selection_popup.resizable(False, False)
        selection_popup.transient(self.popup_loan)
        selection_popup.grab_set()

        title = ctk.CTkLabel(selection_popup, text="Múltiplos empréstimos encontrados.\nSelecione um:", text_color=TEXT_COLOR_BLACK, font=("Arial", 16, "bold"))
        title.pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(selection_popup, width=750, height=350)
        scroll_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        loans_found = False

        for loan in loans_list:
            id_emp, id_liv, quant_emp, data_emp, prazo_emp, livro_nome, autor_nome, ano_nome, editora_nome, status_emp = loan

            if status_emp not in ["Pendente", "Atrasado"]:
                continue

            loans_found = True

            if isinstance(data_emp, str):
                data_formatada = datetime.strptime(data_emp, "%Y-%m-%d").strftime("%d/%m/%Y")
            else:
                data_formatada = data_emp.strftime("%d/%m/%Y")

            btn_text = f"Título: {livro_nome} | Autor: {autor_nome} | Ano: {ano_nome} | Editora: {editora_nome} | Quantidade: {quant_emp} | Data: {data_formatada}"

            btn = ctk.CTkButton(scroll_frame, text=btn_text, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, anchor="w",height=40,command=lambda l=loan, p=selection_popup: self.edit_select_and_close(l, p, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type))
            btn.pack(pady=5, padx=5, fill="x")

        if not loans_found:
             label_vazia = ctk.CTkLabel(scroll_frame, text="Nenhum empréstimo pendente ou atrasado encontrado.", text_color="gray")
             label_vazia.pack(pady=20)

    def edit_fill_loan_fields(self, loan_data, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry, status_type):
        id_emp, id_liv, quantidade, data, prazo, livro, autor, ano, editora, status = loan_data

        self.current_loan_id = id_emp

        if isinstance(data, str):
            data_new = datetime.strptime(data, "%Y-%m-%d").strftime("%d%m%Y")
        else:
            data_new = data.strftime("%d%m%Y")

        if isinstance(prazo, str):
            prazo_new = datetime.strptime(prazo, "%Y-%m-%d").strftime("%d%m%Y")
        else:
            prazo_new = prazo.strftime("%d%m%Y")

        quant_entry.delete(0, "end")
        quant_entry.insert(0, quantidade)

        date_entry.delete(0, "end")
        date_entry.insert(0, data_new)

        due_entry.delete(0, "end")
        due_entry.insert(0, prazo_new)

        status_type.set(status)

        self.update_disabled_entry(book_entry, livro)
        self.update_disabled_entry(autor_entry, autor)
        self.update_disabled_entry(ano_entry, ano)
        self.update_disabled_entry(editora_entry, editora)

    def edit_select_and_close(self, loan_data, popup, *args):
        popup.destroy()
        self.edit_fill_loan_fields(loan_data, *args)

    def delete_loan(self):
        self.popup_loan = ctk.CTkToplevel(self, fg_color="white")
        self.popup_loan.title("Deletar Empréstimo")
        self.popup_loan.resizable(False, False)
        self.popup_loan.transient(self)
        self.popup_loan.grab_set()

        self.popup_loan.grid_columnconfigure(0, weight=1)
        self.popup_loan.grid_columnconfigure((1, 2, 3, 4), weight=0)
        self.popup_loan.grid_rowconfigure((0, 2), weight=0)
        self.popup_loan.grid_rowconfigure((1, 3), weight=1)

        form_frame = ctk.CTkFrame(self.popup_loan, fg_color="white")
        form_frame.grid(row=2, column=0, sticky="n", padx=20, pady=10)
        form_frame.grid_columnconfigure(0, weight=0)
        form_frame.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(self.popup_loan, text="DELETAR EMPRÉSTIMO", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 0))

        row_index = 0

        obs_label = ctk.CTkLabel(form_frame, text="Os campos com * são obrigatórios", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        obs_label.grid(row=row_index, column=1, ipady=5)

        row_index += 1

        name_label = ctk.CTkLabel(form_frame, text="*Nome completo: \n(ex: Guilherme Menezes Silva)", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        name_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        name_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        name_container.grid(row=row_index, column=1, pady=(10, 5))

        nome_entry = ctk.CTkEntry(name_container, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300,  corner_radius=25)
        nome_entry.pack(side="left", pady=(10, 5), ipady=5)
        nome_entry.bind("<Return>", lambda e: self.delete_search_loan_data(nome_entry, user_type, general_entry, toggle_fields, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry))

        btn_search_user = ctk.CTkButton(name_container, text="Buscar", width=50, corner_radius=25, fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, command=lambda: self.delete_search_loan_data(nome_entry, user_type, general_entry, toggle_fields, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry))
        btn_search_user.pack(side="left", padx=(10, 0), pady=(10, 5), ipady=5)
        btn_search_user.bind("<Enter>", lambda e: btn_search_user.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        btn_search_user.bind("<Leave>", lambda e: btn_search_user.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        row_index += 1

        type_label = ctk.CTkLabel(form_frame, text="Tipo de usuário:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        type_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5), ipady=5)

        type_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        type_frame.grid(row=row_index, column=1, pady=15, sticky="w")

        user_type = ctk.StringVar(value="Aluno")

        row_index += 1

        email_aluno_label = ctk.CTkLabel(form_frame, text="RA:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        email_aluno_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        general_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        general_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5, sticky="w")
        general_entry.configure(state="disabled")

        email_prof_label = ctk.CTkLabel(form_frame, text="Email:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        email_prof_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))
        email_prof_label.grid_remove()

        def toggle_fields():
            if user_type.get() == "Aluno":
                email_aluno_label.grid()
                email_prof_label.grid_remove()

            else:
                email_aluno_label.grid_remove()
                email_prof_label.grid()

        self.aluno_button = ctk.CTkRadioButton(type_frame, text="Aluno", text_color_disabled=TEXT_COLOR_BLACK, variable=user_type, value="Aluno", command=toggle_fields, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        self.aluno_button.pack(side="left")
        self.aluno_button.configure(state="disabled")

        self.professor_button = ctk.CTkRadioButton(type_frame, text="Professor", text_color_disabled=TEXT_COLOR_BLACK, variable=user_type, value="Professor", fg_color=BLUE_COLOR, command=toggle_fields, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        self.professor_button.pack(side="left")
        self.professor_button.configure(state="disabled")

        row_index += 1        

        book_label = ctk.CTkLabel(form_frame, text="Título do Livro:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        book_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        book_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        book_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        book_entry.configure(state="disabled")

        row_index += 1

        autor_label = ctk.CTkLabel(form_frame, text="Nome do Autor:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        autor_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        autor_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        autor_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        autor_entry.configure(state="disabled")

        row_index += 1

        ano_label = ctk.CTkLabel(form_frame, text="Ano do Livro:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        ano_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        ano_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=59, corner_radius=25)
        ano_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        ano_entry.configure(state="disabled")

        row_index += 1

        editora_label = ctk.CTkLabel(form_frame, text="Editora do Livro:", text_color="black", font=("Arial", 11, "bold"), anchor="w")
        editora_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        editora_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=300, corner_radius=25)
        editora_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        editora_entry.configure(state="disabled")

        row_index += 1

        quant_label = ctk.CTkLabel(form_frame, text="Quantidade:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        quant_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        quant_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=53, corner_radius=25, validate="key")
        quant_entry.grid(row=row_index, column=1, pady=(10, 5), ipady=5, sticky="w")
        quant_entry.configure(state="disabled")

        row_index += 1

        date_label = ctk.CTkLabel(form_frame, text="Data do Empréstimo:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        date_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        date_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=87, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 8), "%P"))
        date_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        date_entry.configure(state="disabled")
    
        row_index += 1

        due_label = ctk.CTkLabel(form_frame, text="Prazo de Devolução:", text_color=TEXT_COLOR_BLACK, font=("Arial", 11, "bold"), anchor="w")
        due_label.grid(row=row_index, column=0, padx=(0, 20), pady=(10, 5))

        due_entry = ctk.CTkEntry(form_frame, fg_color="#f0f0f0", text_color=TEXT_COLOR_BLACK, border_width=0, width=87, corner_radius=25, validate="key", validatecommand=(form_frame.register(lambda P: len(P) <= 8), "%P"))
        due_entry.grid(row=row_index, column=1, sticky="w", pady=(10, 5), ipady=5)
        due_entry.configure(state="disabled")

        row_index += 1

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=row_index, column=1, columnspan=2, pady=(20, 10))

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=lambda: self.popup_loan.destroy(), fg_color=BUTTON_NEUTRAL, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        cancel_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=(0, 10))
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=BUTTON_NEUTRAL))

        confirm_button = ctk.CTkButton(button_frame, text="Confirmar", command=lambda: self.make_delete_loan_to_db(), fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=75)
        confirm_button.grid(row=0, column=1, sticky="nsew", padx=10, pady=(0, 10))
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

    def make_delete_loan_to_db(self):
        if not hasattr(self, 'current_loan_id') or self.current_loan_id is None:
            messagebox.showerror("Erro", "Nenhum empréstimo selecionado.")
            return
        
        try:
            query_action = "DELETE FROM tb_emprestimos WHERE id_emp = %s"
            values = (self.current_loan_id, )
            query_stock = "UPDATE tb_livros SET quantidade = quantidade + %s WHERE id_liv = %s"
            values_stock = (self.current_loan_quant, self.current_book_id)

            self.confirm_button_edit_loan(query_action, values, query_stock, values_stock)

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao realizar devolução: {e}")

    def delete_search_loan_data(self, nome_entry, user_type, general_entry, func_toggle, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry):
        nome_busca = nome_entry.get().strip()
        
        if not nome_busca:
            return

        try:
            cursor = Database.sql.cursor()
            query = f"SELECT id_usa, nome, tipo, email FROM tb_usuarios WHERE nome LIKE %s"
            cursor.execute(query, (f"%{nome_busca}%",))
            results = cursor.fetchall()

            if not results:
                messagebox.showinfo("Busca", "Usuário não encontrado.")
            
            elif len(results) == 1:
                self.continue_delete_with_user(results[0], nome_entry, user_type, general_entry, func_toggle, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry)
            
            else:
                self.delete_show_user_selection(results, nome_entry, user_type, general_entry, func_toggle, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry)
        
        except Exception as e:
            print(f"Erro na busca: {e}")

    def delete_show_user_selection(self, users_list, *args):
        selection_popup = ctk.CTkToplevel(self, fg_color="white")
        selection_popup.title("Selecionar Usuário")
        selection_popup.geometry("650x350")
        selection_popup.resizable(False, False)

        if hasattr(self, 'popup_loan') and self.popup_loan.winfo_exists():
            selection_popup.transient(self.popup_loan)
        else:
            selection_popup.transient(self)
            
        selection_popup.grab_set()

        title = ctk.CTkLabel(selection_popup, text="Múltiplos usuários encontrados.\nSelecione um:", text_color=TEXT_COLOR_BLACK, font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        scroll_frame = ctk.CTkScrollableFrame(selection_popup, width=600, height=350)
        scroll_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        for user in users_list:
            id_usa, u_nome, u_tipo, u_dado = user
            label_dado = "RA" if u_tipo == "Aluno" else "Email"
            btn_text = f"{u_nome} | {u_tipo} | {label_dado}: {u_dado}"
            
            btn = ctk.CTkButton(scroll_frame, text=btn_text, fg_color=BLUE_COLOR, anchor="w", height=40, command=lambda u=user, p=selection_popup: [p.destroy(), self.continue_delete_with_user(u, *args)])
            btn.pack(pady=5, padx=5, fill="x")
    
    def continue_delete_with_user(self, user_result, nome_entry, user_type, general_entry, func_toggle, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry):
        try:
            id_usa, nome, tipo, email = user_result

            nome_entry.delete(0, "end")
            nome_entry.insert(0, nome)

            self.aluno_button.configure(state="normal")
            self.professor_button.configure(state="normal")

            user_type.set(tipo)
            func_toggle()

            self.aluno_button.configure(state="disabled")
            self.professor_button.configure(state="disabled")

            self.update_disabled_entry(general_entry, email)

            cursor = Database.sql.cursor()
            query_emp = f"""
                SELECT E.id_emp, E.id_liv, E.quantidade, E.data, E.prazo, L.livro, L.autor, L.ano, L.editora, E.status
                FROM tb_emprestimos E
                JOIN tb_livros L ON E.id_liv = L.id_liv
                WHERE E.id_usa = {id_usa}
                AND E.status IN ('Pendente', 'Atrasado')
            """
            cursor.execute(query_emp)
            loans_result = cursor.fetchall()

            if not loans_result:
                messagebox.showinfo("Info", "Este usuário não possui empréstimos pendentes.")
            
            elif len(loans_result) == 1:
                self.delete_fill_loan_fields(loans_result[0], book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry)
            
            else:
                self.delete_show_loan_selection(loans_result, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry)

        except Exception as e:
            print(f"Erro ao carregar empréstimos: {e}")

    def delete_show_loan_selection(self, loans_list, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry):
        selection_popup = ctk.CTkToplevel(self, fg_color="white")
        selection_popup.title("Selecionar Empréstimo")
        selection_popup.geometry("750x350")
        selection_popup.resizable(False, False)
        selection_popup.transient(self.popup_loan)
        selection_popup.grab_set()
        
        if hasattr(self, 'popup_loan') and self.popup_loan.winfo_exists():
            selection_popup.transient(self.popup_loan)
        else:
            selection_popup.transient(self)

        title = ctk.CTkLabel(selection_popup, text="Múltiplos empréstimos encontrados.\nSelecione um para devolução:", text_color=TEXT_COLOR_BLACK, font=("Arial", 16, "bold"))
        title.pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(selection_popup, width=750, height=350)
        scroll_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        loans_found = False

        for loan in loans_list:
            id_emp, id_liv, quant_emp, data_emp, prazo_emp, livro_nome, autor_nome, ano_nome, editora_nome, status_emp = loan

            if status_emp not in ["Pendente", "Atrasado"]:
                continue

            loans_found = True

            if isinstance(data_emp, str):
                data_formatada = datetime.strptime(data_emp, "%Y-%m-%d").strftime("%d/%m/%Y")
            else:
                data_formatada = data_emp.strftime("%d/%m/%Y")

            btn_text = f"Título: {livro_nome} | Autor: {autor_nome} | Ano: {ano_nome} | Editora: {editora_nome} | Quantidade: {quant_emp} | Data: {data_formatada}"

            btn = ctk.CTkButton(scroll_frame, text=btn_text, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, anchor="w", height=40, command=lambda l=loan, p=selection_popup: self.delete_select_and_close(l, p, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry))
            btn.pack(pady=5, padx=5, fill="x")
        
        if not loans_found:
             label_vazia = ctk.CTkLabel(scroll_frame, text="Nenhum empréstimo pendente ou atrasado encontrado.", text_color="gray")
             label_vazia.pack(pady=20)

    def delete_select_and_close(self, loan_data, popup, *args):
        popup.destroy()
        self.delete_fill_loan_fields(loan_data, *args)

    def delete_fill_loan_fields(self, loan_data, book_entry, autor_entry, ano_entry, editora_entry, quant_entry, date_entry, due_entry):
        id_emp, id_liv, quantidade, data, prazo, livro, autor, ano, editora, status = loan_data

        self.current_loan_id = id_emp
        self.current_book_id = id_liv
        self.current_loan_quant = int(quantidade)

        if isinstance(data, str):
            data_new = datetime.strptime(data, "%Y-%m-%d").strftime("%d%m%Y")
        else:
            data_new = data.strftime("%d%m%Y")

        if isinstance(prazo, str):
            prazo_new = datetime.strptime(prazo, "%Y-%m-%d").strftime("%d%m%Y")
        else:
            prazo_new = prazo.strftime("%d%m%Y")

        self.update_disabled_entry(quant_entry, quantidade)
        self.update_disabled_entry(date_entry, data_new)
        self.update_disabled_entry(due_entry, prazo_new)
        self.update_disabled_entry(book_entry, livro)
        self.update_disabled_entry(autor_entry, autor)
        self.update_disabled_entry(ano_entry, ano)
        self.update_disabled_entry(editora_entry, editora)

    def show_returns(self):
        self.clear_main_frame()

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure((1, 2, 3, 4), weight=0)
        self.main_frame.grid_rowconfigure((0, 2, 3), weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.sort_column = "nome"
        self.sort_direction = "ASC"

        row_index = 0

        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.grid(row=row_index, column=0, sticky="ew", padx=25, pady=(17.5, 15))
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure((2, 3), weight=0)

        title = ctk.CTkLabel(top_frame, text="DEVOLUÇÕES", fg_color="transparent", text_color=TEXT_COLOR_BLACK, font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=(0, 20))

        search_frame = ctk.CTkFrame(top_frame, fg_color=LIGHT_PURPLE_COLOR, corner_radius=25)
        search_frame.grid(row=0, column=1, sticky="ew",)

        search_icon = ctk.CTkLabel(search_frame, text="🔍", text_color="gray", font=("Arial", 16))
        search_icon.pack(side="left", padx=(10, 2))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar... (ex: 25112025)", border_width=0, fg_color="transparent", text_color=TEXT_COLOR_BLACK, height=30)
        self.search_entry.pack(side="left", expand=True, fill="x", ipady=5)
        self.search_entry.bind("<Return>", self.general_filter)

        filter_button = ctk.CTkButton(search_frame, text="⏷", fg_color="transparent", hover_color=DARK_PURPLE_COLOR, text_color="gray", width=10, font=("Arial", 16), command=None)
        filter_button.pack(side="right", padx=10)

        self.remove_button = ctk.CTkButton(top_frame, text="❌", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=None)
        self.remove_button.grid(row=0, column=2, sticky="e", padx=(12, 12))

        self.edit_button = ctk.CTkButton(top_frame, text="✏", width=40, height=40, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, command=None)
        self.edit_button.grid(row=0, column=3, sticky="e", padx=(0, 0))

        row_index += 1

        self.table_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.table_frame.grid(row=row_index, column=0, sticky="nsew", padx=25, pady=(0, 20))

        self.general_filter()

    def update_disabled_entry(self, entry, value):
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, str(value))
            entry.configure(state="disabled")

    def close_screen(self):
        match self.active_button_name:
            case "USUÁRIOS":
                self.show_users()
            case "LIVROS":
                self.show_books()
            case "EMPRÉSTIMOS":
                self.show_loans()
            case "ADMINISTRAÇÃO":
                self.show_admin()
            case "DEVOLUÇÕES":
                self.show_returns()
            case _:
                self.show_admin()

    def confirm_button(self, func, query, values):
        popup = ctk.CTkToplevel(self, fg_color="white")
        popup.title("Confirmação dos Dados")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(popup, fg_color="white", corner_radius=0)
        content_frame.pack(fill="both", expand=True)
        content_frame.grid_columnconfigure((0, 1), weight=1)

        popup_icon = ctk.CTkLabel(content_frame, text="📝", text_color=TEXT_COLOR_BLACK, font=("Arial", 60))
        popup_icon.grid(row=0, column=0, columnspan=2, pady=(15, 5))

        popup_title = ctk.CTkLabel(content_frame, text="Os dados estão corretos?", text_color=TEXT_COLOR_BLACK, font=("Arial", 14, "bold"), justify="center")
        popup_title.grid(row=1, column=0, columnspan=2, pady=(5, 20), padx=20)

        def confirm_and_try():
            popup.destroy()

        cancel_button = ctk.CTkButton(content_frame, text="Não", command=confirm_and_try, fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=50)
        cancel_button.grid(row=2, column=0, padx=10, pady=(0, 25), sticky="e")
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        def confirm_and_close():
            try:
                popup.destroy()     
                if func == "books":
                    cursor = Database.sql.cursor()
                    cursor.execute(query, values)
                    Database.sql.commit()
                    self.popup_book.destroy()
                    self.close_screen()
                if func == "users":
                    cursor = Database.sql.cursor()
                    cursor.execute(query, values)
                    Database.sql.commit()
                    self.popup_user.destroy()
                    self.close_screen()
                if func == "loans":
                    cursor = Database.sql.cursor()
                    cursor.execute(query, values)
                    Database.sql.commit()
                    self.popup_loan.destroy()
                    self.close_screen()
            except Exception as e:
                Database.sql.rollback()
                messagebox.showerror("Erro", f"Erro ao confirmar: {e}")
            
        confirm_button = ctk.CTkButton(content_frame, text="Sim", command=confirm_and_close, fg_color=BUTTON_NEUTRAL, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=50)
        confirm_button.grid(row=2, column=1, padx=10, pady=(0, 25), sticky="w")
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=BUTTON_NEUTRAL))

        popup.update_idletasks()
        req_width = popup.winfo_reqwidth()
        req_height = popup.winfo_reqheight()
        x = self.winfo_x() + (self.winfo_width() // 2) - (req_width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (req_height // 2)
        popup.geometry(f"{req_width}x{req_height}+{x}+{y}")

    def confirm_button_add_loan(self, query_insert, values, query_update_stock, values_update):
        popup = ctk.CTkToplevel(self, fg_color="white")
        popup.title("Confirmação dos Dados")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(popup, fg_color="white", corner_radius=0)
        content_frame.pack(fill="both", expand=True)
        content_frame.grid_columnconfigure((0, 1), weight=1)

        popup_icon = ctk.CTkLabel(content_frame, text="📝", text_color=TEXT_COLOR_BLACK, font=("Arial", 60))
        popup_icon.grid(row=0, column=0, columnspan=2, pady=(15, 5))

        popup_title = ctk.CTkLabel(content_frame, text="Os dados estão corretos?", text_color=TEXT_COLOR_BLACK, font=("Arial", 14, "bold"), justify="center")
        popup_title.grid(row=1, column=0, columnspan=2, pady=(5, 20), padx=20)

        def confirm_and_try():
            popup.destroy()

        cancel_button = ctk.CTkButton(content_frame, text="Não", command=confirm_and_try, fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=50)
        cancel_button.grid(row=2, column=0, padx=10, pady=(0, 25), sticky="e")
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        def confirm_and_close():
            try:
                popup.destroy()     
                cursor = Database.sql.cursor()
                cursor.execute(query_insert, values)
                cursor.execute(query_update_stock, values_update)
                Database.sql.commit()
                self.popup_loan.destroy()
                self.close_screen()
            except Exception as e:
                Database.sql.rollback()
                messagebox.showerror("Erro", f"Erro ao confirmar: {e}")
            
        confirm_button = ctk.CTkButton(content_frame, text="Sim", command=confirm_and_close, fg_color=BUTTON_NEUTRAL, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=50)
        confirm_button.grid(row=2, column=1, padx=10, pady=(0, 25), sticky="w")
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=BUTTON_NEUTRAL))

        popup.update_idletasks()
        req_width = popup.winfo_reqwidth()
        req_height = popup.winfo_reqheight()
        x = self.winfo_x() + (self.winfo_width() // 2) - (req_width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (req_height // 2)
        popup.geometry(f"{req_width}x{req_height}+{x}+{y}")

    def confirm_button_edit_loan(self, query_action, values, query_stock, values_stock):
        popup = ctk.CTkToplevel(self, fg_color="white")
        popup.title("Confirmação dos Dados")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(popup, fg_color="white", corner_radius=0)
        content_frame.pack(fill="both", expand=True)
        content_frame.grid_columnconfigure((0, 1), weight=1)

        popup_icon = ctk.CTkLabel(content_frame, text="📝", text_color=TEXT_COLOR_BLACK, font=("Arial", 60))
        popup_icon.grid(row=0, column=0, columnspan=2, pady=(15, 5))

        popup_title = ctk.CTkLabel(content_frame, text="Os dados estão corretos?", text_color=TEXT_COLOR_BLACK, font=("Arial", 14, "bold"), justify="center")
        popup_title.grid(row=1, column=0, columnspan=2, pady=(5, 20), padx=20)

        def confirm_and_try():
            popup.destroy()

        cancel_button = ctk.CTkButton(content_frame, text="Não", command=confirm_and_try, fg_color=LIGHT_COLOR, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=50)
        cancel_button.grid(row=2, column=0, padx=10, pady=(0, 25), sticky="e")
        cancel_button.bind("<Enter>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        cancel_button.bind("<Leave>", lambda e: cancel_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=LIGHT_COLOR))

        def confirm_and_close():
            try:
                popup.destroy()     
                cursor = Database.sql.cursor()
                cursor.execute(query_action, values)
                cursor.execute(query_stock, values_stock)
                Database.sql.commit()
                self.popup_loan.destroy()
                self.close_screen()
            except Exception as e:
                Database.sql.rollback()
                messagebox.showerror("Erro", f"Erro ao confirmar: {e}")
            
        confirm_button = ctk.CTkButton(content_frame, text="Sim", command=confirm_and_close, fg_color=BUTTON_NEUTRAL, text_color=TEXT_COLOR_BLACK, corner_radius=25, width=50)
        confirm_button.grid(row=2, column=1, padx=10, pady=(0, 25), sticky="w")
        confirm_button.bind("<Enter>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_WHITE, fg_color=BLUE_COLOR_HOVER))
        confirm_button.bind("<Leave>", lambda e: confirm_button.configure(text_color=TEXT_COLOR_BLACK, fg_color=BUTTON_NEUTRAL))

        popup.update_idletasks()
        req_width = popup.winfo_reqwidth()
        req_height = popup.winfo_reqheight()
        x = self.winfo_x() + (self.winfo_width() // 2) - (req_width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (req_height // 2)
        popup.geometry(f"{req_width}x{req_height}+{x}+{y}")
        
class DashboardLogin(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login Biblioteca")
        self.geometry("1280x720")
        self.minsize(854, 480)
        self.resizable(True, True)

        bg = ctk.CTkFrame(self, fg_color=BLUE_COLOR, corner_radius=0)
        bg.pack(fill="both", expand=True)

        frame = ctk.CTkFrame(bg, fg_color="white", corner_radius=25)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        window_title = ctk.CTkLabel(frame, text="Login da Biblioteca", text_color=TEXT_COLOR_BLACK, font=("Arial", 16, "bold"))
        window_title.pack(pady=(20, 10))

        user_label = ctk.CTkLabel(frame, text="Nome de Usuário", text_color="gray", anchor="w")
        user_label.pack(fill="x", padx=30)
        user_entry = ctk.CTkEntry(frame, corner_radius=25, fg_color="#f0f0f0", border_width=0, text_color=TEXT_COLOR_BLACK, font=("Arial", 11))
        user_entry.pack(fill="x", padx=30, pady=(0, 10), ipady=5)
        user_entry.bind("<Return>", lambda e: login())

        word_label = ctk.CTkLabel(frame, text="Senha", text_color="gray", anchor="w")
        word_label.pack(fill="x", padx=30)
        word_entry = ctk.CTkEntry(frame, corner_radius=25, fg_color="#f0f0f0", border_width=0, text_color=TEXT_COLOR_BLACK, font=("Arial", 11), show="*")
        word_entry.pack(fill="x", padx=30, pady=(0, 15), ipady=5)
        word_entry.bind("<Return>", lambda e: login())

        def error(wrong):
            error = ctk.CTkToplevel(self, fg_color=BLUE_COLOR)
            error.title("Login Biblioteca - Erro")            
            error.resizable(False, False)
            error.transient(self)
            error.grab_set()

            error.grid_columnconfigure(0, weight=1)
            error.grid_rowconfigure(0, weight=1)

            content_frame = ctk.CTkFrame(error, fg_color="white", corner_radius=25)
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)
            content_frame.grid_columnconfigure(0, weight=1)

            def close_error():
                error.destroy()

            if wrong == 1:
                error_title = ctk.CTkLabel(content_frame, text="Usuário ou senha incorretos.", text_color=TEXT_COLOR_BLACK, font=("Arial", 14, "bold"), justify="center")
                error_title.grid(row=0, column=0, pady=(17, 5), padx=15)
            elif wrong == 2:
                error_title = ctk.CTkLabel(content_frame, text="Preencha os campos obrigatórios.", text_color=TEXT_COLOR_BLACK, font=("Arial", 14, "bold"), justify="center")
                error_title.grid(row=0, column=0, pady=(17, 5), padx=15)

            try_again = ctk.CTkButton(content_frame, text="Tentar novamente", fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, corner_radius=25, text_color=TEXT_COLOR_WHITE, command=close_error)
            try_again.grid(row=1, column=0, ipady=5, ipadx=7, sticky="s", pady=(5, 20))

            error.update_idletasks()
            req_width = error.winfo_reqwidth()
            req_height = error.winfo_reqheight()
            x = self.winfo_x() + (self.winfo_width() // 2) - (req_width // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (req_height // 2)
            error.geometry(f"{req_width}x{req_height}+{x}+{y}")

        def login():
            user = user_entry.get()
            password = word_entry.get()
            right = {user: "admin", password: "admin"}
            wrong = 0

            if user == right[user] and password == right[password]:
                self.withdraw()
                dashboard_app = DashboardApp(login_window=self)
                dashboard_app.mainloop()
            elif user == "" or password == "":
                wrong = 2
                error(wrong)
            elif user != right[user] or password != right[password]:
                wrong = 1
                error(wrong)
            
        enter_button = ctk.CTkButton(frame, text="Entrar", command=login, corner_radius=25, fg_color=BLUE_COLOR, hover_color=BLUE_COLOR_HOVER, text_color=TEXT_COLOR_WHITE, font=("Arial", 12, "bold"))
        enter_button.pack(pady=(5, 10), ipadx=10, ipady=5)

        footer_label = ctk.CTkLabel(frame, text="Apenas para Administradores", text_color="gray", font=("Arial", 9))
        footer_label.pack(pady=(0, 5))

        self.mainloop()

if __name__ == "__main__":
    app = DashboardApp(login_window=None)
    app.mainloop()