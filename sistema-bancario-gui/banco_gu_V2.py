import tkinter as tk
from tkinter import messagebox, simpledialog
import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

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

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)
        
    @property
    def nome(self):
        # Propriedade a ser implementada na subclasse
        raise NotImplementedError("A classe filha deve implementar o nome.")

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self._nome = nome
        self.data_nascimento = data_nascimento
        self._cpf = cpf  # CORREÇÃO: Atribuindo ao atributo interno (_cpf)

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
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            messagebox.showerror("Erro de Saque", "Você não tem saldo suficiente.")
            return False
        elif valor > 0:
            self._saldo -= valor
            return True
        else:
            messagebox.showerror("Erro de Saque", "O valor informado é inválido.")
            return False

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

    def sacar(self, valor):
        # Conta saques usando a lista de transacoes do histórico
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            messagebox.showerror("Erro de Saque", f"O valor do saque excede o limite de R$ {self._limite:.2f}.")
        elif excedeu_saques:
            messagebox.showerror("Erro de Saque", "Número máximo de saques diários excedido.")
        else:
            return super().sacar(valor)

        return False

# --- Historico (Com Gerador e Data/Hora) ---

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        # Registro de Transação com Data e Hora
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
            }
        )

    # --- GERADOR para Extrato ---
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
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


# ==============================================================================
# 2. INTERFACE GRÁFICA (TKINTER) - Layout Otimizado para Mobile
# ==============================================================================

class BancoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Bancário - GUI V3")
        self.geometry("400x450") 
        self.configure(padx=10, pady=10)
        
        self.AGENCIA = "0001"
        self.clientes = []
        self.contas = []
        self.conta_selecionada = None 
        
        self.setup_ui()
        self.carregar_dados_iniciais()

    def carregar_dados_iniciais(self):
        # Cria um usuário PessoaFisica com a classe correta
        cliente_teste = PessoaFisica("Valdeci Boldan", "31-03-1981", "123", "Rua Barueri, 51 - Moreninh 2 - Campo Grande/MS")
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
        
        frame_botoes_conta = tk.Frame(frame_acoes)
        frame_botoes_conta.pack(fill='x', padx=10) 

        btn_depositar = tk.Button(frame_botoes_conta, text="Depositar", command=self.handle_depositar)
        btn_sacar = tk.Button(frame_botoes_conta, text="Sacar", command=self.handle_sacar)
        btn_extrato = tk.Button(frame_botoes_conta, text="Extrato", command=self.handle_extrato)
        
        btn_depositar.pack(fill='x', pady=2)
        btn_sacar.pack(fill='x', pady=2)
        btn_extrato.pack(fill='x', pady=2)
        
        # Frame de Gerenciamento (nu, nc, lc)
        frame_gerencia = tk.Frame(self)
        frame_gerencia.pack(pady=10, fill='x')
        
        tk.Label(frame_gerencia, text="Gerenciamento:", font=('Arial', 12, 'bold')).pack(pady=5)
        
        frame_botoes_gerencia = tk.Frame(frame_gerencia)
        frame_botoes_gerencia.pack(fill='x', padx=10)

        btn_novo_usuario = tk.Button(frame_botoes_gerencia, text="Novo Usuário", command=self.handle_criar_usuario)
        btn_nova_conta = tk.Button(frame_botoes_gerencia, text="Nova Conta", command=self.handle_criar_conta)
        btn_listar_contas = tk.Button(frame_botoes_gerencia, text="Listar Contas", command=self.handle_listar_contas)

        btn_novo_usuario.pack(fill='x', pady=2)
        btn_nova_conta.pack(fill='x', pady=2)
        btn_listar_contas.pack(fill='x', pady=2)
        
        # Status da Conta Selecionada
        self.status_label = tk.Label(self, text="", font=('Arial', 14, 'bold'), fg="blue", justify=tk.LEFT)
        self.status_label.pack(pady=10, fill='x', padx=10)
        
        # Botão para selecionar outra conta
        btn_selecionar = tk.Button(self, text="Mudar Conta Selecionada", command=self.handle_mudar_conta)
        btn_selecionar.pack(fill='x', padx=10, pady=5)
        
        self.update_idletasks()
        self.geometry(f"{self.winfo_width()}x{self.winfo_height()}")

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
        if valor is not None:
            transacao = Deposito(valor)
            self.conta_selecionada.cliente.realizar_transacao(self.conta_selecionada, transacao)
            self.atualizar_status()
            # Mensagem de sucesso é exibida apenas se a transação for bem-sucedida dentro da classe.

    def handle_sacar(self):
        if not self.conta_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma conta primeiro.")
            return
            
        valor = simpledialog.askfloat("Saque", "Informe o valor do saque:")
        if valor is not None:
            transacao = Saque(valor)
            self.conta_selecionada.cliente.realizar_transacao(self.conta_selecionada, transacao)
            self.atualizar_status()

    def handle_extrato(self):
        if not self.conta_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma conta primeiro.")
            return
            
        # Implementação do Gerador (gerar_relatorio) no Extrato
        extrato_list = []
        tem_transacao = False
        
        # O gerador retorna cada transação uma por vez
        for transacao in self.conta_selecionada.historico.gerar_relatorio():
            tem_transacao = True
            # Detalhes da Data e Hora (Nova Característica)
            extrato_list.append(
                f"[{transacao['data']}] {transacao['tipo']}:\t\tR$ {transacao['valor']:.2f}"
            )

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

    # --- Handlers de Gerenciamento (nu, nc, lc) ---

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

        # --- Implementação do Iterador (ContasIterador) ---
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