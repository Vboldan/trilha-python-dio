import tkinter as tk
from tkinter import messagebox, simpledialog
import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import functools

# ==============================================================================
# 0. DECORADOR DE LOG EM ARQUIVO (REQUISITO NOVO)
# ==============================================================================

def log_transacao(funcao):
    @functools.wraps(funcao)
    def wrapper(*args, **kwargs):
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nome_funcao = funcao.__name__
        
        # 1. Executa a função original e captura o retorno
        resultado = funcao(*args, **kwargs)
        
        # 2. Prepara os argumentos e o retorno para o log
        
        # Exclui 'self' da lista de argumentos
        args_formatados = [f"{arg}" for i, arg in enumerate(args) if i != 0] 
        
        # Tenta formatar a mensagem de retorno se for um tupla (sucesso, mensagem)
        if isinstance(resultado, tuple):
             valor_retornado = f"Sucesso: {resultado[0]} | Mensagem: '{resultado[1]}'"
        else:
             valor_retornado = f"'{resultado}'"

        # 3. Constrói a linha de log
        log_entry = textwrap.dedent(f"""\
            [LOG {data_hora}]
            Função: {nome_funcao}
            Args: ({', '.join(args_formatados)})
            Retorno: {valor_retornado}
            ---
        """)

        # 4. Salva no arquivo log.txt (Modo 'a' para append/adicionar)
        try:
            with open("log.txt", "a") as file:
                file.write(log_entry)
        except Exception as e:
            # Em caso de erro ao escrever no log (permissão, etc.)
            print(f"ERRO AO ESCREVER LOG: {e}") 

        return resultado
    return wrapper


# ==============================================================================
# 1. MODELO DE DADOS AVANÇADO (LÓGICA DE NEGÓCIO - POO, ITERADORES, GERADORES)
# ==============================================================================

# --- ITERADOR para a Lista de Contas ---
class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            self._index += 1
            return f"""\
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
        """
        except IndexError:
            raise StopIteration

# --- Classes de Cliente e Pessoa ---

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    @log_transacao
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta) 

    def adicionar_conta(self, conta):
        self.contas.append(conta)
        
    @property
    def nome(self):
        raise NotImplementedError("A classe filha deve implementar o nome.")

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self._nome = nome
        self.data_nascimento = data_nascimento
        self._cpf = cpf

    @property
    def cpf(self):
        return self._cpf
    
    @property
    def nome(self):
        return self._nome

# --- Classes de Conta ---

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    @log_transacao
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @log_transacao
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            return False, "Você não tem saldo suficiente."
        elif valor <= 0:
            return False, "O valor informado é inválido."
        else:
            self._saldo -= valor
            return True, f"Saque de R$ {valor:.2f} realizado com sucesso."

    @log_transacao
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            return True, f"Depósito de R$ {valor:.2f} realizado com sucesso."
        else:
            return False, "O valor informado é inválido."


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    # Sobrescreve 'sacar' para incluir a lógica de limite e saques
    @log_transacao
    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            return False, f"O valor do saque excede o limite de R$ {self._limite:.2f}."
        elif excedeu_saques:
            return False, "Número máximo de saques diários excedido."
        else:
            # Chama o sacar da Conta (pai)
            return super().sacar(valor) 

# --- Historico (Com Gerador e Data/Hora) ---

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

# --- Classes Abstratas para Transacao ---

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        # A lógica de saque está na conta e será logada lá
        sucesso_transacao, _ = conta.sacar(self.valor) 

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        # A lógica de depósito está na conta e será logada lá
        sucesso_transacao, _ = conta.depositar(self.valor) 

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


# ==============================================================================
# 2. INTERFACE GRÁFICA (TKINTER)
# ==============================================================================

class BancoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Bancário - GUI Responsiva")
        self.geometry("400x600") 
        self.minsize(300, 400) 
        
        self.AGENCIA = "0001"
        self.clientes = []
        self.contas = []
        self.conta_selecionada = None 
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.setup_ui()
        self.carregar_dados_iniciais()

    def carregar_dados_iniciais(self):
        cliente_teste = PessoaFisica("Valdeci Boldan", "01-01-1990", "12345678900", "Rua A, 1 - Centro - Cidade/SP")
        self.clientes.append(cliente_teste)
        
        # Usa o método estático decorado
        conta_teste = ContaCorrente.nova_conta(cliente_teste, 1) 
        self.contas.append(conta_teste)
        cliente_teste.adicionar_conta(conta_teste)
        
        transacao_dep1 = Deposito(100.00)
        cliente_teste.realizar_transacao(conta_teste, transacao_dep1)
        transacao_dep2 = Deposito(100.00)
        cliente_teste.realizar_transacao(conta_teste, transacao_dep2)
        transacao_dep3 = Deposito(50.00)
        cliente_teste.realizar_transacao(conta_teste, transacao_dep3)
        
        self.conta_selecionada = conta_teste
        self.atualizar_status()

    # SETUP UI COM SCROLLBAR E GRID
    def setup_ui(self):
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        pad_x = 20
        
        tk.Label(scrollable_frame, text="Ações de Conta:", font=('Arial', 16, 'bold'), justify=tk.LEFT).grid(row=0, column=0, pady=(15, 5), sticky="w", padx=pad_x)
        
        frame_botoes_conta = tk.Frame(scrollable_frame)
        frame_botoes_conta.grid(row=1, column=0, sticky="ew", padx=pad_x)
        frame_botoes_conta.grid_columnconfigure(0, weight=1)

        btn_depositar = tk.Button(frame_botoes_conta, text="Depositar", command=self.handle_depositar, height=2)
        btn_sacar = tk.Button(frame_botoes_conta, text="Sacar", command=self.handle_sacar, height=2)
        btn_extrato = tk.Button(frame_botoes_conta, text="Extrato", command=self.handle_extrato, height=2)
        
        btn_depositar.pack(fill='x', pady=2)
        btn_sacar.pack(fill='x', pady=2)
        btn_extrato.pack(fill='x', pady=2)
        
        tk.Label(scrollable_frame, text="Gerenciamento:", font=('Arial', 16, 'bold'), justify=tk.LEFT).grid(row=2, column=0, pady=(15, 5), sticky="w", padx=pad_x)
        
        frame_botoes_gerencia = tk.Frame(scrollable_frame)
        frame_botoes_gerencia.grid(row=3, column=0, sticky="ew", padx=pad_x)
        frame_botoes_gerencia.grid_columnconfigure(0, weight=1)

        btn_novo_usuario = tk.Button(frame_botoes_gerencia, text="Novo Usuário", command=self.handle_criar_usuario, height=2)
        btn_nova_conta = tk.Button(frame_botoes_gerencia, text="Nova Conta", command=self.handle_criar_conta, height=2)
        btn_listar_contas = tk.Button(frame_botoes_gerencia, text="Listar Contas", command=self.handle_listar_contas, height=2)

        btn_novo_usuario.pack(fill='x', pady=2)
        btn_nova_conta.pack(fill='x', pady=2)
        btn_listar_contas.pack(fill='x', pady=2)
        
        self.status_label = tk.Label(scrollable_frame, text="", font=('Arial', 14, 'bold'), fg="blue", justify=tk.LEFT)
        self.status_label.grid(row=4, column=0, pady=(15, 5), sticky="ew", padx=pad_x)
        
        btn_selecionar = tk.Button(scrollable_frame, text="Mudar Conta Selecionada", command=self.handle_mudar_conta, height=2)
        btn_selecionar.grid(row=5, column=0, sticky="ew", padx=pad_x, pady=(5, 20))
        
        self.update_idletasks()

    def atualizar_status(self):
        if self.conta_selecionada:
            conta = self.conta_selecionada
            status_text = f"Conta Selecionada: {conta.numero}\n"
            status_text += f"Titular: {conta.cliente.nome}\n"
            status_text += f"Saldo: R$ {conta.saldo:.2f}"
            self.status_label.config(text=status_text)
        else:
            self.status_label.config(text="Nenhuma conta selecionada.")
            
    # --- Funções de Ajuda ---

    def _filtrar_cliente(self, cpf):
        clientes_filtrados = [c for c in self.clientes if c.cpf == cpf]
        return clientes_filtrados[0] if clientes_filtrados else None

    # --- Handlers de Ação (Lógica GUI) ---

    def handle_depositar(self):
        if not self.conta_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma conta primeiro.")
            return

        valor = simpledialog.askfloat("Depósito", "Informe o valor do depósito:")
        if valor is not None:
            # Chama a função de lógica (que é decorada com log)
            sucesso, mensagem = self.conta_selecionada.depositar(valor)
            
            if sucesso:
                transacao = Deposito(valor)
                # A função realizar_transacao também é decorada
                self.conta_selecionada.cliente.realizar_transacao(self.conta_selecionada, transacao)
                self.atualizar_status()
                messagebox.showinfo("Sucesso", mensagem)
            else:
                 messagebox.showerror("Erro de Depósito", mensagem)


    def handle_sacar(self):
        if not self.conta_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma conta primeiro.")
            return
            
        valor = simpledialog.askfloat("Saque", "Informe o valor do saque:")
        if valor is not None:
            # Chama a função de lógica (que é decorada com log)
            sucesso, mensagem = self.conta_selecionada.sacar(valor)
            
            if sucesso:
                transacao = Saque(valor)
                # A função realizar_transacao também é decorada
                self.conta_selecionada.cliente.realizar_transacao(self.conta_selecionada, transacao)
                self.atualizar_status()
                messagebox.showinfo("Sucesso", mensagem)
            else:
                 messagebox.showerror("Erro de Saque", mensagem)


    # MÉTODO EXTRATO CORRIGIDO PARA TELAS ESTREITAS
    def handle_extrato(self):
        if not self.conta_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma conta primeiro.")
            return
            
        extrato_list = []
        tem_transacao = False
        
        for transacao in self.conta_selecionada.historico.gerar_relatorio():
            tem_transacao = True
            
            # Formatação para telas estreitas: Quebra em duas linhas para evitar truncamento
            data_tipo = f"[{transacao['data']}] {transacao['tipo']}:"
            
            valor_formatado = f"R$ {transacao['valor']:.2f}".rjust(12) 
            linha_valor = "    " + valor_formatado # Adiciona um recuo
            
            extrato_list.append(data_tipo)
            extrato_list.append(linha_valor)
            extrato_list.append("-" * 30) # Separador visual

        if tem_transacao:
            extrato_list.pop() 

        if not tem_transacao:
            extrato_str = "Não foram realizadas movimentações."
        else:
            extrato_str = "\n".join(extrato_list)
        
        mensagem = textwrap.dedent(f"""\
            ================ EXTRATO ================
            {extrato_str}
            
            Saldo Atual: R$ {self.conta_selecionada.saldo:.2f}
            =========================================
        """)
        
        messagebox.showinfo("Extrato da Conta (Data/Hora)", mensagem)

    # --- Handlers de Gerenciamento (Lógica GUI) ---

    def handle_criar_usuario(self):
        cpf = simpledialog.askstring("Novo Usuário", "Informe o CPF (somente número):")
        if not cpf: return

        if self._filtrar_cliente(cpf):
            messagebox.showerror("Erro", "Já existe usuário com esse CPF!")
            return

        nome = simpledialog.askstring("Novo Usuário", "Informe o nome completo:")
        data_nascimento = simpledialog.askstring("Novo Usuário", "Informe a data de nascimento (dd-mm-aaaa):")
        endereco = simpledialog.askstring("Novo Usuário", "Informe o endereço (logradouro, nro - bairro - cidade/sigla estado):")

        if nome and data_nascimento and endereco:
            novo_cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
            self.clientes.append(novo_cliente)
            messagebox.showinfo("Sucesso", f"Usuário {nome} criado com sucesso!")
        else:
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios.")

    def handle_criar_conta(self):
        cpf = simpledialog.askstring("Nova Conta", "Informe o CPF do cliente:")
        if not cpf: return

        cliente = self._filtrar_cliente(cpf)

        if cliente:
            numero_conta = len(self.contas) + 1
            # Usa o método estático decorado
            nova_conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta) 
            
            self.contas.append(nova_conta)
            cliente.adicionar_conta(nova_conta)
            
            messagebox.showinfo("Sucesso", f"Conta {self.AGENCIA}-{numero_conta} criada com sucesso para {cliente.nome}!")
        else:
            messagebox.showerror("Erro", "Cliente não encontrado.")

    def handle_listar_contas(self):
        if not self.contas:
            messagebox.showinfo("Contas", "Nenhuma conta cadastrada.")
            return

        lista_contas = []
        for conta_detalhes in ContasIterador(self.contas):
            lista_contas.append(textwrap.dedent(conta_detalhes))
            
        contas_str = "=" * 30 + "\n" + ("\n" + "=" * 30 + "\n").join(lista_contas)
        messagebox.showinfo("Lista de Contas (Iterador)", contas_str)
        
    def handle_mudar_conta(self):
        if not self.contas:
            messagebox.showwarning("Atenção", "Nenhuma conta cadastrada.")
            return
            
        contas_opcoes = [f"{c.agencia}-{c.numero} | Titular: {c.cliente.nome}" for c in self.contas]
        
        while True:
            prompt = "Selecione o número da conta (ex: 1 para a primeira conta):\n" + "\n".join(contas_opcoes)
            selecao_str = simpledialog.askstring("Mudar Conta", prompt)
            
            if selecao_str is None: return 
            
            try:
                indice = int(selecao_str) - 1
                if 0 <= indice < len(self.contas):
                    self.conta_selecionada = self.contas[indice]
                    self.atualizar_status()
                    messagebox.showinfo("Sucesso", f"Conta {self.conta_selecionada.numero} selecionada.")
                    break
                else:
                    messagebox.showerror("Erro", "Número de conta inválido.")
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira um número válido.")


if __name__ == "__main__":
    app = BancoApp()
    app.mainloop()