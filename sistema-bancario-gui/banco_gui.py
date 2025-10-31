import tkinter as tk
from tkinter import messagebox, simpledialog
import textwrap

# ==============================================================================
# 1. MODELO DE DADOS (LÓGICA DE NEGÓCIO - POO)
#    Reestruturação do seu código para classes, mais adequado para GUI.
# ==============================================================================

class Transacao:
    """Classe base para todas as transações."""
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": "Hoje" # Para simplificar, pode adicionar data real se quiser
        })

    def gerar_extrato(self, conta):
        extrato_str = "Não foram realizadas movimentações."
        if self.transacoes:
            extrato_list = []
            for transacao in self.transacoes:
                tipo = transacao["tipo"]
                valor = transacao["valor"]
                extrato_list.append(f"{tipo}:\t\tR$ {valor:.2f}")
            extrato_str = "\n".join(extrato_list)
        
        return extrato_str

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
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

    def sacar(self, valor):
        if valor > self.saldo:
            messagebox.showerror("Erro de Saque", "Você não tem saldo suficiente.")
            return False
        elif valor <= 0:
            messagebox.showerror("Erro de Saque", "O valor informado é inválido.")
            return False

        self._saldo -= valor
        return True

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            return True
        else:
            messagebox.showerror("Erro de Depósito", "O valor informado é inválido.")
            return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
        self._numero_saques = 0

    def sacar(self, valor):
        excedeu_limite = valor > self._limite
        excedeu_saques = self._numero_saques >= self._limite_saques

        if excedeu_limite:
            messagebox.showerror("Erro de Saque", f"O valor do saque excede o limite de R$ {self._limite:.2f}.")
        elif excedeu_saques:
            messagebox.showerror("Erro de Saque", "Número máximo de saques diários excedido.")
        else:
            if super().sacar(valor): # Chama o sacar da classe base (Conta)
                self._numero_saques += 1
                return True
        return False

class Pessoa:
    def __init__(self, nome, data_nascimento, cpf, endereco):
        self._nome = nome
        self._data_nascimento = data_nascimento
        self._cpf = cpf
        self._endereco = endereco

    @property
    def cpf(self):
        return self._cpf
    
    @property
    def nome(self):
        return self._nome

class Cliente(Pessoa):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(nome, data_nascimento, cpf, endereco)
        self._contas = []

    def adicionar_conta(self, conta):
        self._contas.append(conta)

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)


# ==============================================================================
# 2. INTERFACE GRÁFICA (TKINTER)
# ==============================================================================

class BancoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🏦 Sistema Bancário - GUI")
        self.geometry("600x450")
        self.configure(padx=10, pady=10)
        
        # Estado Global da Aplicação
        self.AGENCIA = "0001"
        self.clientes = []
        self.contas = []
        self.conta_selecionada = None # Usado para Depósito/Saque/Extrato
        
        self.setup_ui()
        self.carregar_dados_iniciais()

    def carregar_dados_iniciais(self):
        # Cria um usuário e conta inicial para facilitar o teste
        cliente_teste = Cliente("Maria Silva", "01-01-1990", "12345678900", "Rua A, 1 - Centro - Cidade/SP")
        self.clientes.append(cliente_teste)
        
        conta_teste = ContaCorrente(1, cliente_teste)
        self.contas.append(conta_teste)
        cliente_teste.adicionar_conta(conta_teste)
        
        self.conta_selecionada = conta_teste
        self.atualizar_status()

    def setup_ui(self):
        # Frame Principal de Ações
        frame_acoes = tk.Frame(self)
        frame_acoes.pack(pady=10, fill='x')

        tk.Label(frame_acoes, text="Ações de Conta:", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Botões Principais (d, s, e)
        btn_depositar = tk.Button(frame_acoes, text="💰 Depositar", command=self.handle_depositar, width=15)
        btn_sacar = tk.Button(frame_acoes, text="💸 Sacar", command=self.handle_sacar, width=15)
        btn_extrato = tk.Button(frame_acoes, text="📄 Extrato", command=self.handle_extrato, width=15)
        
        btn_depositar.pack(side=tk.LEFT, padx=5)
        btn_sacar.pack(side=tk.LEFT, padx=5)
        btn_extrato.pack(side=tk.LEFT, padx=5)
        
        # Frame de Gerenciamento (nu, nc, lc)
        frame_gerencia = tk.Frame(self)
        frame_gerencia.pack(pady=10, fill='x')
        
        tk.Label(frame_gerencia, text="Gerenciamento:", font=('Arial', 12, 'bold')).pack(pady=5)
        
        btn_novo_usuario = tk.Button(frame_gerencia, text="🧑 Novo Usuário", command=self.handle_criar_usuario, width=15)
        btn_nova_conta = tk.Button(frame_gerencia, text="💳 Nova Conta", command=self.handle_criar_conta, width=15)
        btn_listar_contas = tk.Button(frame_gerencia, text="📑 Listar Contas", command=self.handle_listar_contas, width=15)

        btn_novo_usuario.pack(side=tk.LEFT, padx=5)
        btn_nova_conta.pack(side=tk.LEFT, padx=5)
        btn_listar_contas.pack(side=tk.LEFT, padx=5)
        
        # Status da Conta Selecionada
        self.status_label = tk.Label(self, text="", font=('Arial', 14, 'bold'), fg="blue", justify=tk.LEFT)
        self.status_label.pack(pady=20, fill='x')
        
        # Botão para selecionar outra conta
        btn_selecionar = tk.Button(self, text="Mudar Conta Selecionada", command=self.handle_mudar_conta)
        btn_selecionar.pack(pady=10)

    def atualizar_status(self):
        """Atualiza o label de status da conta na tela."""
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
        """Procura um cliente pelo CPF na lista de clientes."""
        clientes_filtrados = [c for c in self.clientes if c.cpf == cpf]
        return clientes_filtrados[0] if clientes_filtrados else None

    # --- Handlers de Ação (d, s, e) ---

    def handle_depositar(self):
        if not self.conta_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma conta primeiro.")
            return

        valor = simpledialog.askfloat("Depósito", "Informe o valor do depósito:")
        if valor is not None and valor > 0:
            deposito = Deposito(valor)
            self.conta_selecionada.cliente.realizar_transacao(self.conta_selecionada, deposito)
            self.atualizar_status()
            messagebox.showinfo("Sucesso", f"Depósito de R$ {valor:.2f} realizado.")
        elif valor is not None:
            messagebox.showerror("Erro", "Valor inválido.")

    def handle_sacar(self):
        if not self.conta_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma conta primeiro.")
            return
            
        valor = simpledialog.askfloat("Saque", "Informe o valor do saque:")
        if valor is not None and valor > 0:
            saque = Saque(valor)
            # A lógica de saque da ContaCorrente já trata limites e mensagens de erro
            self.conta_selecionada.cliente.realizar_transacao(self.conta_selecionada, saque)
            self.atualizar_status()
        elif valor is not None:
            messagebox.showerror("Erro", "Valor inválido.")

    def handle_extrato(self):
        if not self.conta_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma conta primeiro.")
            return
            
        extrato_str = self.conta_selecionada.historico.gerar_extrato(self.conta_selecionada)
        
        mensagem = textwrap.dedent(f"""\
            ================ EXTRATO ================
            {extrato_str}
            
            Saldo Atual: R$ {self.conta_selecionada.saldo:.2f}
            =========================================
        """)
        
        messagebox.showinfo("Extrato da Conta", mensagem)

    # --- Handlers de Gerenciamento (nu, nc, lc) ---

    def handle_criar_usuario(self):
        cpf = simpledialog.askstring("Novo Usuário", "Informe o CPF (somente número):")
        if not cpf: return

        if self._filtrar_cliente(cpf):
            messagebox.showerror("Erro", "Já existe usuário com esse CPF!")
            return

        # Coleta os demais dados
        nome = simpledialog.askstring("Novo Usuário", "Informe o nome completo:")
        data_nascimento = simpledialog.askstring("Novo Usuário", "Informe a data de nascimento (dd-mm-aaaa):")
        endereco = simpledialog.askstring("Novo Usuário", "Informe o endereço (logradouro, nro - bairro - cidade/sigla estado):")

        if nome and data_nascimento and endereco:
            novo_cliente = Cliente(nome, data_nascimento, cpf, endereco)
            self.clientes.append(novo_cliente)
            messagebox.showinfo("Sucesso", f"Usuário {nome} criado com sucesso!")
        else:
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios para criar o usuário.")

    def handle_criar_conta(self):
        cpf = simpledialog.askstring("Nova Conta", "Informe o CPF do cliente:")
        if not cpf: return

        cliente = self._filtrar_cliente(cpf)

        if cliente:
            numero_conta = len(self.contas) + 1
            nova_conta = ContaCorrente.nova_conta(cliente, numero_conta)
            
            self.contas.append(nova_conta)
            cliente.adicionar_conta(nova_conta)
            
            messagebox.showinfo("Sucesso", f"Conta {self.AGENCIA}-{numero_conta} criada com sucesso para {cliente.nome}!")
        else:
            messagebox.showerror("Erro", "Cliente não encontrado, fluxo de criação de conta encerrado!")

    def handle_listar_contas(self):
        if not self.contas:
            messagebox.showinfo("Contas", "Nenhuma conta cadastrada.")
            return

        lista_contas = []
        for conta in self.contas:
            lista_contas.append(textwrap.dedent(f"""\
                Agência:\t{conta.agencia}
                C/C:\t\t{conta.numero}
                Titular:\t{conta.cliente.nome}
                Saldo:\t\tR$ {conta.saldo:.2f}
            """))
            
        contas_str = "=" * 30 + "\n" + ("\n" + "=" * 30 + "\n").join(lista_contas)
        messagebox.showinfo("Lista de Contas", contas_str)
        
    def handle_mudar_conta(self):
        if not self.contas:
            messagebox.showwarning("Atenção", "Nenhuma conta cadastrada.")
            return
            
        contas_opcoes = [f"{c.agencia}-{c.numero} | Titular: {c.cliente.nome}" for c in self.contas]
        
        # Usa um loop e simpledialog para simular uma seleção simples
        while True:
            prompt = "Selecione o número da conta (ex: 1 para a primeira conta):\n" + "\n".join(contas_opcoes)
            selecao_str = simpledialog.askstring("Mudar Conta", prompt)
            
            if selecao_str is None: return # Usuário cancelou
            
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
