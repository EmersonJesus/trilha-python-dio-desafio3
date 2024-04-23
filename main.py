import textwrap
from abc import ABC, abstractmethod
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 10:
            print("\n@@@ Voce excedeu o numero de transacoes permitidas para hoje! @@@")
            return
        
        transacao.registrar(conta)

    def adicionar_contas(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

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
        try:
            if valor <= 0:
                raise ValueError("O valor do saque deve ser maior que zero.")
            
            if valor > self._saldo:
                raise ValueError("Saldo insuficiente.")
            
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True
        
        except ValueError as e:
            print("\n@@@ Operação falhou! ", e, "@@@")
            return False

    def depositar(self, valor):
        try:
            if valor <= 0:
                raise ValueError("O valor do depósito deve ser maior que zero.")

            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True
        
        except ValueError as e:
            print("\n@@@ Operação falhou! ", e, "@@@")
            return False
        
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        try:
            if valor > self._limite:
                raise ValueError("O valor do saque excede o limite.")
            
            numero_saques = len (
                [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
            )

            if numero_saques >= self._limite_saques:
                raise ValueError("Número máximo de saques excedido.")
            
            sucesso_saque = super().sacar(valor)
            if sucesso_saque:
                self.historico.adicionar_transacao(Saque(valor))
                return True

        except ValueError as e:
            print("\n@@@ Operação falhou! ", e, "@@@")
            return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """
    
class ContaPoupanca(Conta):
    def __init__(self, numero, cliente, limite=0):
        super().__init__(numero, cliente)
        self._limite = limite  # Limite de saque permitido na conta poupança

    def sacar(self, valor):
        try:
            if valor > self.saldo + self._limite:
                raise ValueError("O valor do saque excede o saldo disponível mais o limite.")
            
            if valor <= 0:
                raise ValueError("O valor do saque é inválido.")
            
            sucesso_saque = super().sacar(valor)
            if sucesso_saque:
                self.historico.adicionar_transacao(Saque(valor))
                return True
        
        except ValueError as e:
            print("\n@@@ Operação falhou! ", e, "@@@")
            return False

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
                "data": datetime.now().strftime("%d-%m-%Y %H:%M"),
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    def transacoes_do_dia(self):
        data_atual = datetime.utcnow().date()
        transacoes = []
        for  transacao in self._transacoes:
            data_transacao = datetime.strptime(transacao["data"], "%d-%m-%Y %H:%M:%S").date()
            if data_atual == data_transacao:
                transacoes.append(transacao)
        return transacoes

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @abstractmethod
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

def menu():
    menu = """\n
    ================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNova conta
    [5]\tListar contas
    [6]\tNovo usuário
    [0]\tSair
    => """
    return input(textwrap.dedent(menu))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return
    
    return cliente.contas[0]

def validar_cpf(cpf):
    if not cpf.isdigit() or len(cpf) != 11:
        return False
    return True

def obter_valor(mensagem):
    while True:
        valor = input(mensagem)
        if valor.isdigit() and float(valor) > 0:
            return float(valor)
        else:
            print("\n@@@ Valor inválido! Por favor, insira um número positivo. @@@\n")

def encontrar_cliente_por_cpf(cpf, clientes):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido! Por favor, insira um CPF válido. @@@\n")
        return

    cliente = encontrar_cliente_por_cpf(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@\n")
        return

    valor = obter_valor("Informe o valor do depósito: ")
    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido! Por favor, insira um CPF válido. @@@\n")
        return

    cliente = encontrar_cliente_por_cpf(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@\n")
        return

    valor = obter_valor("Informe o valor do saque: ")
    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\nData: {transacao['data']}\nTipo: {transacao['tipo']}\nValor: R$ {transacao['valor']:.2f}\n"

    print(extrato)
    print(f"\nSaldo: R$ {conta.saldo:.2f}")
    print("==========================================")

def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    if not validar_cpf(cpf):
        print("\n@@@ CPF inválido! Por favor, insira um CPF válido. @@@\n")
        return
    
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    print("Escolha o tipo de conta:")
    print("[1] Conta Corrente")
    print("[2] Conta Poupança")
    tipo_conta = input("=> ")

    if tipo_conta == "1":
        conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    elif tipo_conta == "2":
        conta = ContaPoupanca.nova_conta(cliente=cliente, numero=numero_conta)
    else:
        print("\n@@@ Tipo de conta inválido! @@@")
        return

    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "5":
            listar_contas(contas)

        elif opcao == "6":
            criar_cliente(clientes)

        elif opcao == "0":
            print("\n@@@ Saindo... @@@")
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")

if __name__ == "__main__":
    main()
