from Metodos.Metodos_Pesquisa import custo_uniforme as co
from Metodos.Metodos_Pesquisa import aprofundamento_progressivo as ap
from Metodos.Metodos_Pesquisa import procura_sofrega as ps
from Metodos.Metodos_Pesquisa import astar as aStar
from Metodos.Metodos_Pesquisa import reconhecer_matricula

from Cidades.distancia_cidades_km import graph_cidades as gc
from Cidades.coordenadas import coordinates
from Cidades.distancia_linha_reta import distacia_linha_reta

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from PIL import Image, ImageTk
import os
import json
import datetime

class InterfaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Matriculas e Caminhos")
        
        # Criar container principal com scrollbar
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill="both", expand=True)
        
        # Criar canvas com scrollbar
        self.canvas = tk.Canvas(self.main_container)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configurar o scrollable_frame para expandir
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # Criar janela no canvas para o frame rolável
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Dispor componentes no layout
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Configurar rolagem com mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Criar todos os componentes UI, mas inicialmente mostrar apenas OCR
        self.criar_componentes_ui()
        
        # Inicialmente, apenas mostrar o frame OCR
        self.mostrar_apenas_ocr()
        
        # Carregar caminhos salvos na inicialização
        self.carregar_caminhos()

    def _on_mousewheel(self, event):
        """Permite rolagem com a roda do mouse"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def criar_componentes_ui(self):
        """Cria todos os componentes da interface, mas não os exibe inicialmente."""
        # === Frame Principal ===
        self.main_frame = ttk.Frame(self.scrollable_frame)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # === Frame OCR ===
        self.ocr_frame = ttk.LabelFrame(self.main_frame, text="OCR - Reconhecimento da Matrícula")
        
        # Botão para selecionar imagem
        self.select_image_button = ttk.Button(self.ocr_frame, text="Selecionar Imagem", command=self.select_image)
        self.select_image_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Label para exibir a imagem selecionada
        self.image_label = ttk.Label(self.ocr_frame)
        self.image_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Label para exibir a matrícula reconhecida
        self.label_matricula = ttk.Label(self.ocr_frame, text="Matrícula reconhecida:")
        self.label_matricula.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.matricula_var = tk.StringVar()
        self.matricula_entry = ttk.Entry(self.ocr_frame, textvariable=self.matricula_var, width=15)
        self.matricula_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.edit_button = ttk.Button(self.ocr_frame, text="Editar", command=self.enable_edit_matricula)
        self.edit_button.grid(row=2, column=2, padx=5, pady=5)
        
        # Botão para continuar após OCR (inicialmente oculto)
        self.continuar_button = ttk.Button(self.ocr_frame, text="Continuar", 
                                         command=self.continuar_apos_ocr)
        self.continuar_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        self.continuar_button.grid_remove()  # Inicialmente oculto
        
        # Adicionar um separador
        ttk.Separator(self.ocr_frame, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Adicionar texto explicativo
        ttk.Label(self.ocr_frame, text="Ou calcule um caminho diretamente sem OCR:").grid(
            row=5, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        
        # Botão para cálculo direto de caminho
        self.calculo_direto_button = ttk.Button(
            self.ocr_frame, 
            text="Calcular Caminho Diretamente", 
            command=self.calcular_caminho_direto
        )
        self.calculo_direto_button.grid(row=6, column=0, columnspan=3, padx=5, pady=5)
        
        # === Frame de Detalhes para Matrícula Registada ===
        self.detalhes_frame = ttk.LabelFrame(self.scrollable_frame, text="Detalhes do Caminho")
        # Criação dos componentes, mas não adicionamos ao grid ainda
        
        self.matricula_detalhes_label = ttk.Label(self.detalhes_frame, text="Matrícula: ")
        self.origem_destino_label = ttk.Label(self.detalhes_frame, text="Origem → Destino: ")
        self.metodo_label = ttk.Label(self.detalhes_frame, text="Método: ")
        self.custo_label = ttk.Label(self.detalhes_frame, text="Custo: ")
        self.data_label = ttk.Label(self.detalhes_frame, text="Data: ")
        
        self.caminho_detalhes_text = tk.Text(self.detalhes_frame, height=8, width=50)
        
        self.novo_calculo_button = ttk.Button(self.detalhes_frame, text="Novo Cálculo", 
                                           command=self.mostrar_calculo_caminho)
        self.voltar_ocr_button = ttk.Button(self.detalhes_frame, text="Voltar para OCR", 
                                          command=self.mostrar_apenas_ocr)
        
        # === Frame de Cálculo de Caminho ===
        self.calculo_frame = ttk.LabelFrame(self.scrollable_frame, text="Cálculo de Caminho")
        
        # Labels e campos para o cálculo
        self.label_start = ttk.Label(self.calculo_frame, text="Cidade de partida:")
        self.label_start.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.label_goal = ttk.Label(self.calculo_frame, text="Cidade de destino:")
        self.label_goal.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.label_method = ttk.Label(self.calculo_frame, text="Método:")
        self.label_method.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.label_depth_limit = ttk.Label(self.calculo_frame, text="Limite de Profundidade:")
        
        # seleção da cidade de partida
        self.start_var = tk.StringVar()
        self.combobox_start = ttk.Combobox(self.calculo_frame, textvariable=self.start_var)
        self.combobox_start['values'] = tuple(coordinates.keys())
        self.combobox_start.grid(row=0, column=1, padx=5, pady=5)
        self.combobox_start.current(0)
        
        # seleção da cidade de destino
        self.goal_var = tk.StringVar()
        self.combobox_goal = ttk.Combobox(self.calculo_frame, textvariable=self.goal_var)
        self.combobox_goal['values'] = tuple(coordinates.keys())
        self.combobox_goal.grid(row=1, column=1, padx=5, pady=5)
        
        # seleção do método
        self.method_var = tk.StringVar()
        self.method_var.set("Custo Uniforme")  # Define o método padrão como Custo Uniforme
        self.method_combobox = ttk.Combobox(self.calculo_frame, textvariable=self.method_var)
        self.method_combobox['values'] = ("Custo Uniforme", "Aprofundamento progressivo", "Procura Sôfrega", "A*")
        self.method_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.method_combobox.bind("<<ComboboxSelected>>", self.on_method_selected)
        
        # entrada para o limite de profundidade (inicialmente invisível)
        self.depth_limit_entry = ttk.Entry(self.calculo_frame)
        
        # Textbox para exibir o resultado
        self.result_text = tk.Text(self.calculo_frame, height=10, width=50)
        self.result_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        # Botão para o cálculo do caminho
        self.calculate_button = ttk.Button(self.calculo_frame, text="Calcular Caminho", 
                                         command=self.calculate_path_selected)
        self.calculate_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        
        # Botão para registar o caminho (inicialmente invisível)
        self.register_button = ttk.Button(self.calculo_frame, text="registar Caminho", 
                                        command=self.registar_caminho)
        
        # Botão para voltar para OCR
        self.voltar_ocr_button2 = ttk.Button(self.calculo_frame, text="Voltar para OCR", 
                                           command=self.mostrar_apenas_ocr)
        self.voltar_ocr_button2.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        
        # === Frame para Pesquisa de Caminhos ===
        self.pesquisa_frame = ttk.LabelFrame(self.scrollable_frame, text="Pesquisa de Caminhos")
        
        # Criar componentes da pesquisa (como na implementação original)
        # ...

        # Variável para armazenar o caminho da imagem atual
        self.current_image_path = None
        
        # Adicionar estrutura para armazenar caminhos calculados
        self.caminhos_registados = []
        
        # Variável para armazenar o resultado atual
        self.resultado_atual = None

    def mostrar_apenas_ocr(self):
        """Mostra apenas o frame OCR, escondendo os outros."""
        # Esconder todos os frames
        if hasattr(self, 'detalhes_frame'):
            self.detalhes_frame.grid_remove()
        if hasattr(self, 'calculo_frame'):
            self.calculo_frame.grid_remove()
        if hasattr(self, 'pesquisa_frame'):
            self.pesquisa_frame.grid_remove()
        
        # Mostrar apenas o OCR
        self.ocr_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Esconder o botão continuar até que uma matrícula seja reconhecida
        self.continuar_button.grid_remove()

    def mostrar_detalhes_matricula(self, caminho):
        """Mostra os detalhes do caminho para a matrícula já registada."""
        # Esconder outros frames
        self.ocr_frame.grid_remove()
        self.calculo_frame.grid_remove() if hasattr(self, 'calculo_frame') else None
        self.pesquisa_frame.grid_remove() if hasattr(self, 'pesquisa_frame') else None
        
        # Mostrar frame de detalhes
        self.detalhes_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Preencher detalhes
        self.matricula_detalhes_label.config(text=f"Matrícula: {caminho['matricula']}")
        self.matricula_detalhes_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.origem_destino_label.config(text=f"Origem → Destino: {caminho['origem']} → {caminho['destino']}")
        self.origem_destino_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.metodo_label.config(text=f"Método: {caminho['metodo']}")
        self.metodo_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.custo_label.config(text=f"Custo: {caminho['custo']}")
        self.custo_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        self.data_label.config(text=f"Data: {caminho['data']}")
        self.data_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        
        # Mostrar caminho completo
        self.caminho_detalhes_text.delete(1.0, tk.END)
        self.caminho_detalhes_text.insert(tk.END, f"Caminho completo: {caminho['caminho']}\n")
        self.caminho_detalhes_text.grid(row=5, column=0, padx=5, pady=5, sticky="nsew")
        
        # Botões
        self.novo_calculo_button.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.voltar_ocr_button.grid(row=6, column=0, padx=5, pady=5, sticky="e")

    def mostrar_calculo_caminho(self):
        """Mostra a interface para cálculo de caminho."""
        # Esconder outros frames
        self.ocr_frame.grid_remove()
        self.detalhes_frame.grid_remove() if hasattr(self, 'detalhes_frame') else None
        self.pesquisa_frame.grid_remove() if hasattr(self, 'pesquisa_frame') else None
        
        # Mostrar frame de cálculo
        self.calculo_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Limpar campos para novo cálculo
        self.limpar_campos_caminho()
        
        # Configurar matrícula atual
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Matrícula selecionada: {self.matricula_var.get()}\n")
        self.result_text.insert(tk.END, "Selecione as cidades de origem e destino e o método para calcular o caminho.")

    def continuar_apos_ocr(self):
        """Verifica a matrícula após OCR e redireciona para a interface adequada."""
        matricula = self.matricula_var.get()
        if not matricula or matricula == "Não reconhecida":
            messagebox.showerror("Erro", "Por favor, reconheça uma matrícula válida primeiro.")
            return
        
        self.verificar_matricula_registada(matricula, redirecionar=True)

    def on_method_selected(self, event):
        selected_method = self.method_var.get()
        if selected_method == "Aprofundamento Progressivo":
            self.label_depth_limit.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            self.depth_limit_entry.grid(row=3, column=1, padx=5, pady=5)
        else:
            self.label_depth_limit.grid_remove()
            self.depth_limit_entry.grid_remove()

    def calculate_path_selected(self):
        # Initialize variables to avoid UnboundLocalError
        resultado = None
        caminho = None
        custo = 0
        
        # Verificar se tem uma matrícula reconhecida
        matricula = self.matricula_var.get()
        
        # Opções para quando não há matrícula
        if not matricula:
            # Permitir cálculo sem matrícula, mas sem registo automático
            resposta = messagebox.askyesno("Sem Matrícula", 
                                         "Não há matrícula associada. Deseja adicionar uma agora?")
            if resposta:
                matricula = simpledialog.askstring("Matrícula", "Digite uma matrícula para associar ao caminho:")
                if matricula:
                    self.matricula_var.set(matricula)
                else:
                    # Se o usuário cancelar, perguntar se quer prosseguir sem matrícula
                    resposta2 = messagebox.askyesno("Sem Matrícula", 
                                                 "Continuar sem matrícula? O caminho não poderá ser registado.")
                    if not resposta2:
                        return
        
        start_city = self.start_var.get()
        goal_city = self.goal_var.get()  # Sempre usar a cidade selecionada pelo usuário
        selected_method = self.method_var.get()
        depth_limit = None
        
        # Verificar se a cidade de destino foi selecionada
        if not goal_city:
            tk.messagebox.showerror("Erro", "Por favor, selecione uma cidade de destino.")
            return

        # Verificar se a cidade de origem e destino são iguais
        if start_city == goal_city:
            tk.messagebox.showerror("Erro", "As cidades de origem e destino não podem ser iguais.")
            return

        if selected_method == "aprofundamento_progressivo":
            depth_limit = self.depth_limit_entry.get()
            if not depth_limit.isdigit():
                tk.messagebox.showerror("Erro", "Por favor, insira um valor inteiro para o limite de profundidade.")
                return
            depth_limit = int(depth_limit)

        # Limpa o texto anterior
        self.result_text.delete(1.0, tk.END)
        
        # Calcula o caminho com base no método selecionado
        if selected_method == "Custo Uniforme":
            resultado = co(start_city, goal_city)
            caminho, custo = resultado
        elif selected_method == "Aprofundamento progressivo":
            resultado = ap(gc, start_city, goal_city)
            if resultado:
                # The algorithm stores cumulative costs for each node; the
                # final node already contains the total path cost.
                custo = resultado[-1][1]
        elif selected_method == "Procura Sôfrega":
            resultado = ps(coordinates, start_city, goal_city)
            caminho, custo = resultado
        elif selected_method == "A*":
            resultado = aStar(gc, start_city, goal_city, coordinates)
            caminho, custo = resultado
        
        # Se encontrou um caminho, exibir e oferecer para registar (em vez de registar automaticamente)
        if resultado is not None:
            # Exibir resultado
            self.result_text.insert(tk.END, f"Resultado {selected_method}:\n")
            self.result_text.insert(tk.END, f"Matrícula: {matricula}\n")
            
            # Processar o caminho dependendo do método
            caminho_formatado = None
            if selected_method == "Custo Uniforme":
                self.result_text.insert(tk.END, f"Caminho: {caminho}\n")
                self.result_text.insert(tk.END, f"Custo: {custo}\n")
                caminho_formatado = caminho
            elif selected_method == "Aprofundamento progressivo":
                caminho_formatado = [cidade for cidade, _ in resultado]
                self.result_text.insert(tk.END, f"Caminho: {caminho_formatado}\n")
                self.result_text.insert(tk.END, f"Custo: {custo}\n")
            elif selected_method == "Procura Sôfrega":
                self.result_text.insert(tk.END, f"Caminho: {caminho}\n")
                self.result_text.insert(tk.END, f"Custo: {custo}\n")
                caminho_formatado = caminho
            elif selected_method == "A*":
                self.result_text.insert(tk.END, f"Caminho: {caminho}\n")
                self.result_text.insert(tk.END, f"Custo: {custo}\n")
                caminho_formatado = caminho
                
            # Armazenar o resultado atual para registo posterior
            self.resultado_atual = {
                "matricula": matricula,
                "metodo": selected_method,
                "origem": start_city,
                "destino": goal_city,
                "caminho": caminho_formatado,
                "custo": custo
            }
            
            # Mostrar botão para registar
            self.register_button.grid(row=5, column=2, padx=5, pady=5)
        else:
            self.result_text.insert(tk.END, f"Nenhum caminho encontrado para {selected_method}.\n")
            self.register_button.grid_remove()

    def registar_caminho(self):
        """Regista o caminho atual, verificando se já existe um caminho com a mesma matrícula."""
        if not self.resultado_atual:
            return
        
        # Verificar se já existe um caminho registado com esta matrícula
        matricula = self.resultado_atual["matricula"]
        caminho_existente = None
        indice_existente = -1
        
        for i, caminho in enumerate(self.caminhos_registados):
            if caminho["matricula"].upper() == matricula.upper():
                caminho_existente = caminho
                indice_existente = i
                break
        
        if caminho_existente:
            # Pergunta se deseja substituir o caminho existente
            resposta = messagebox.askquestion("Matrícula Duplicada", 
                                            f"A matrícula {matricula} já possui um caminho registado.\n"
                                            f"Método: {caminho_existente['metodo']}\n"
                                            f"Origem: {caminho_existente['origem']} → Destino: {caminho_existente['destino']}\n"
                                            f"Custo: {caminho_existente['custo']}\n\n"
                                            f"Deseja substituir com o novo caminho?")
            if resposta == 'yes':
                # Adiciona a data atual
                self.resultado_atual["data"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Substitui o caminho existente
                self.caminhos_registados[indice_existente] = self.resultado_atual
                messagebox.showinfo("Registo", f"Caminho para a matrícula {matricula} foi substituído com sucesso!")
                self.salvar_caminhos()
                
                # Após registar, mostrar os detalhes do caminho
                self.mostrar_detalhes_matricula(self.resultado_atual)
        else:
            # Regista o novo caminho
            # Adiciona a data atual
            self.resultado_atual["data"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.caminhos_registados.append(self.resultado_atual)
            messagebox.showinfo("Registo", f"Caminho para a matrícula {matricula} foi registado com sucesso!")
            self.salvar_caminhos()
            
            # Após registar, mostrar os detalhes do caminho
            self.mostrar_detalhes_matricula(self.resultado_atual)

    def select_image(self):
        """Abre um diálogo para selecionar uma imagem e realiza OCR para reconhecer a matrícula."""
        file_path = filedialog.askopenfilename(
            title="Selecione uma Imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
        )
        
        if file_path:
            self.current_image_path = file_path
            
            # Redimensiona e exibe a imagem
            img = Image.open(file_path)
            img = img.resize((200, 150), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            self.image_label.configure(image=img_tk)
            self.image_label.image = img_tk  # Mantém uma referência para evitar a coleta de lixo
            
            # Realiza OCR na imagem
            matricula = reconhecer_matricula(file_path)
            if matricula:
                self.matricula_var.set(matricula)
                # Habilita a edição para correções manuais
                self.matricula_entry.configure(state="normal")
                
                # Mostra o botão continuar
                self.continuar_button.grid()
            else:
                self.matricula_var.set("Não reconhecida")
                messagebox.showinfo("OCR", "A matrícula não foi reconhecida. Por favor, edite manualmente.")
                # Esconde o botão continuar até que seja editado manualmente
                self.continuar_button.grid_remove()

    def verificar_matricula_registada(self, matricula, redirecionar=False):
        """Verifica se a matrícula já está registada e redireciona para a interface adequada."""
        # Procurar a matrícula nos registos
        caminho_encontrado = None
        
        for caminho in self.caminhos_registados:
            if caminho["matricula"].upper() == matricula.upper():
                caminho_encontrado = caminho
                break
        
        if caminho_encontrado:
            if redirecionar:
                # Redirecionar para a interface de detalhes
                self.mostrar_detalhes_matricula(caminho_encontrado)
            else:
                # Apenas mostrar mensagem informativa
                resposta = messagebox.askquestion("Matrícula Encontrada", 
                                              f"A matrícula {matricula} já possui um caminho registado. Deseja ver os detalhes?")
                if resposta == 'yes':
                    self.mostrar_detalhes_matricula(caminho_encontrado)
        else:
            if redirecionar:
                # Redirecionar para interface de cálculo
                self.mostrar_calculo_caminho()
            else:
                # Apenas mostrar mensagem informativa
                resposta = messagebox.askquestion("Matrícula Nova", 
                                              f"A matrícula {matricula} não possui caminho registado. Deseja calcular um caminho?")
                if resposta == 'yes':
                    self.mostrar_calculo_caminho()

    def enable_edit_matricula(self):
        """Habilita a edição manual da matrícula reconhecida."""
        self.matricula_entry.configure(state="normal")
        self.matricula_entry.focus_set()
        
        # Mostrar o botão continuar quando o usuário edita a matrícula
        self.continuar_button.grid()

    def salvar_caminhos(self):
        """Salva os caminhos registados em um arquivo JSON."""
        try:
            caminho_arquivo = os.path.join(os.path.dirname(__file__), "caminhos_registados.json")
            with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
                json.dump(self.caminhos_registados, arquivo, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar caminhos: {e}")

    def carregar_caminhos(self):
        """Carrega os caminhos registados de um arquivo JSON."""
        try:
            caminho_arquivo = os.path.join(os.path.dirname(__file__), "caminhos_registados.json")
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                    self.caminhos_registados = json.load(arquivo)
        except Exception as e:
            print(f"Erro ao carregar caminhos: {e}")
            self.caminhos_registados = []

    def calcular_caminho_direto(self):
        """Abre a interface de cálculo de caminho sem necessidade de matrícula OCR."""
        # Pedir uma matrícula manualmente
        matricula = simpledialog.askstring("Matrícula", "Digite uma matrícula para associar ao caminho (opcional):")
        
        # Se cancelar, não prosseguir
        if matricula is None:
            return
        
        # Se foi fornecida uma matrícula, verificar se já existe
        if matricula:
            caminho_existente = None
            for caminho in self.caminhos_registados:
                if caminho["matricula"].upper() == matricula.upper():
                    caminho_existente = caminho
                    break
                    
            if caminho_existente:
                resposta = messagebox.askquestion("Matrícula Existente", 
                                               f"A matrícula {matricula} já possui um caminho registado.\n"
                                               "Deseja ver os detalhes ou calcular um novo caminho?",
                                               icon="info",
                                               type=messagebox.YESNOCANCEL,
                                               default=messagebox.YES)
                
                if resposta == "yes":  # Ver detalhes
                    self.mostrar_detalhes_matricula(caminho_existente)
                    return
                elif resposta == "no":  # Calcular novo
                    pass  # Continua para o cálculo
                else:  # Cancelar
                    return
        
        # Definir a matrícula atual (pode ser vazia)
        self.matricula_var.set(matricula)
        
        # Mostrar a interface de cálculo
        self.mostrar_calculo_caminho()
        
        # Atualizar o texto explicativo na interface
        if matricula:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Matrícula associada: {matricula}\n")
            self.result_text.insert(tk.END, "Selecione as cidades de origem e destino e o método para calcular o caminho.")
        else:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Nenhuma matrícula associada. O caminho não será registado.\n")
            self.result_text.insert(tk.END, "Selecione as cidades de origem e destino e o método para calcular o caminho.")

    def limpar_campos_caminho(self):
        """Limpa os campos para registar um novo caminho."""
        # Seleciona cidade origem padrão
        self.combobox_start.current(0)
        
        # Limpa cidade destino
        self.goal_var.set("")
        
        # Configura método padrão
        self.method_var.set("Custo Uniforme")
        self.on_method_selected(None)  # Atualiza a interface baseado no método selecionado
        
        # Limpa resultado anterior
        self.result_text.delete(1.0, tk.END)
        
        # Remove o botão de registo se estiver visível
        if hasattr(self, 'register_button'):
            self.register_button.grid_remove()
        
        # Limpa o resultado atual armazenado
        self.resultado_atual = None

# Inicializa a interface
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceApp(root)
    root.mainloop()