from socket import *
import select
import sys

#- Global Variables-----------------------------------------------------------------------------------------------------
host = 'localhost'
port = 4321
message_size = 1024

#- Classe Cliente-------------------------------------------------------------------------------------------------------
class Cliente(object):
    # O cliente possui os seguintes atributos:
    # ip e port, para conexão
    # nome, para facilitação da comunicação
    # socket. Para facilitar o envio de mensagens, o socket é um atributo do cliente
    def __init__(self, ip, nome):
        self.ip = ip
        self.nome = nome
        self.sckt = socket()


    # Função para conexão com o servidor
    def connection(self):
        global host, port
        self.sckt.connect((host, port))
        self.port = self.sckt.getsockname()[1]

        # Identifica o nome do cliente para o servidor agrupar em um dicionário connections["nome"] = sckt
        self.sckt.sendall(bytes(self.nome + "##", encoding='utf-8'))


    def close_connection(self):
        self.sckt.close()


    # A msg chegará assim no servidor: "send_message Pedro Olá, tudo bem?"
    def send_request(self, msg):
        self.sckt.sendall(bytes(msg + "##", encoding='utf-8'))


    # A msg chegará assim aqui: "Pedro: Olá, tudo bem?"
    def recv_message(self):
        global message_size

        msg = self.receive(message_size)
        print(msg)


    # Executa diversos skct.recv(bytes) até encontrar o caracter delimitador do fim da mensagem
    def receive(self, size):
        end = False
        str_msg = ''
        while not end:
            msg = self.sckt.recv(size)
            str_msg+= str(msg, encoding='utf-8')
            last_character = str_msg[-2:]
            if last_character == '##':
                end = True

        str_msg = str_msg[:-2]

        return str_msg
#- Main-----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    stop = False
    msg = ''

    client = Cliente('localhost', input('Digite seu nome\n'))
    client.connection()
    inputs = [client.sckt, sys.stdin]
    #inputs = [client.sckt]

    while not stop:
        read, write, exception = select.select(inputs, [], [])
        for reading in read:
            if reading == client.sckt:
                client.recv_message()
            elif reading == sys.stdin:
                msg = input()
                if msg == 'closeConnection':
                    stop = True
                    print('Encerrando conexão com o servidor...')
                else:
                    client.send_request(msg)

    client.close_connection()
