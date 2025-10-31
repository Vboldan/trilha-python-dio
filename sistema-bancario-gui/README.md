# 🏦 Sistema Bancário em Python com Interface Gráfica (GUI)

Este projeto é uma implementação de um sistema bancário simples em Python, inicialmente desenvolvido em console e posteriormente reescrito utilizando Programação Orientada a Objetos (POO) e uma Interface Gráfica de Usuário (GUI) construída com a biblioteca Tkinter.

## ✨ Funcionalidades

O sistema permite as seguintes operações:

* **Depositar (d)**: Adiciona valor ao saldo da conta.
* **Sacar (s)**: Retira valor, respeitando limite de R$ 500.00 por saque e um máximo de 3 saques diários.
* **Extrato (e)**: Exibe o histórico de transações e o saldo atual.
* **Novo Usuário (nu)**: Cria um novo cliente (Pessoa Física).
* **Nova Conta (nc)**: Cria uma nova conta corrente vinculada a um cliente existente (CPF).
* **Listar Contas (lc)**: Exibe a lista de todas as contas criadas.

## ⚙️ Pré-requisitos

Para rodar o projeto, você só precisa ter o **Python 3** instalado no seu sistema.

### 🐍 Instalação do Tkinter (Usuários Linux)

O **Tkinter** é nativo do Python, mas em algumas distribuições Linux (como Debian/Ubuntu), ele precisa ser instalado separadamente do interpretador principal.

Se você receber um erro ao tentar executar o programa, instale o pacote com o seguinte comando no terminal:

```bash
sudo apt install python3-tk
