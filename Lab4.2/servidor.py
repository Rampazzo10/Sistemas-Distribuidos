from socket import *
import select
import sys
import threading
from datetime import datetime

#- Global Variables-----------------------------------------------------------------------------------------------------
host = ''
porta = 4321
connections = dict()
message_size = 1024
#- Functions------------------------------------------------------------------------------------------------------------

def init_server():
    sckt = socket(AF_INET, SOCK_STREAM)
    sckt.bind((host, porta))
    sckt.listen(1)

    return sckt


def show_online_clients():
    # Retorna para o cliente a lista de usuários online
    clients = ''
    for client in connections:
        clients += client + ', '

    # Remover a última vírgula e o último espaço em branco
    clients = clients[:-2]

    return clients



# Aceita a conexão com novos cliente, recebe o nome do novo cliente conectado inserindo no dicionário connections e
  # retorna para o cliente a lista de usuários online no bate-papo
def accept_clients(sckt):
    global connections, message_size
    # Estabelece conexão com novo cliente e recebe seu nome
    newSckt, address = sckt.accept()
    msg = receive(newSckt, message_size)
    clientName = msg
    connections[msg] = newSckt
    print('\nEstabelecendo conexão com cliente ' + clientName + ': ' + str(address))
    msg = 'Usuário ' + clientName + ' conectou-se.'
    clients = show_online_clients()
    for clientSckt in connections.values():
        clientSckt.sendall(bytes(msg + "\nLista de usuários online: " + clients + "##", encoding='utf-8'))
    return newSckt, clientName


# Responsável por fechar a conexão com um cliente recém-desconectado
# Além disso, retorna a nova lista de usuários online
def disconnect_client(clientSckt, clientName):
    global connections
    print('Encerrando conexão com cliente ' + clientName + ': ' + str(sckt.getpeername()))
    clientSckt.close()
    msg = 'Usuário ' + clientName + ' desconectou-se.'
    del connections[clientName]

    clients = show_online_clients()
    for clientSckt in connections.values():
        clientSckt.sendall(bytes(msg + "\nLista de usuários online: " + clients + "##", encoding='utf-8'))


# Camada em que o histórico de mensagens será preenchido e recuperado
def camada_dados():
    pass


# Camada em que as mensagens serão trocadas
def camada_processamento():
    pass


def fulfill_requests(senderSckt, senderName):
    global connections, message_size
    stop = False

    while not stop:
        msg = receive(senderSckt, message_size)
        if not msg:
            disconnect_client(senderSckt, senderName)
            stop = True
        else:
            # Split para separar o tipo de requisição do restante da mensagem
            # O split deve ser feito separadamente, pois dependendo do tipo de requisição a quantidade de parâmetros
              # é diferente
            try:
                parameters = msg.split(" ", 1)
                request = parameters[0]
                remainder = parameters[1]
                if request == 'send_message':
                    # remainder contém uma string com o nome do destinatário e a mensagem em si
                    parameters = remainder.split(" ", 1)
                    # Separando o destinatário e a mensagem
                    receiver = parameters[0]

                    now = datetime.now()
                    dt_string = now.strftime("%d/%m %H:%M")

                    msg = "(" + dt_string + ") " + senderName + ": " + parameters[1] + "##"
                    # Usando a chave do nome do destinatário para buscar seu respectivo socket

                    try:
                        receiverSckt = connections[receiver]
                        receiverSckt.sendall(bytes(msg, encoding='utf-8'))
                        remainder.split(" ", 1)
                    except:
                        senderSckt.sendall(bytes("Usuário " + receiver + " não conectado ao bate-papo##", encoding='utf-8'))
                else:
                    senderSckt.sendall(bytes("SERVER_ERROR: Comando não reconhecido pelo servidor##", encoding='utf-8'))
            except:
                senderSckt.sendall(bytes("SERVER_ERROR: Comando não reconhecido pelo servidor##", encoding='utf-8'))


# Executa diversos skct.recv(bytes) até encontrar o caracter delimitador do fim da mensagem
def receive(sckt, size):
    end = False
    str_msg = ''
    while not end:
        msg = sckt.recv(size)
        if not msg:
            return msg
        str_msg+= str(msg, encoding='utf-8')
        last_character = str_msg[-2:]
        if last_character == '##':
            end = True
    str_msg = str_msg[:-2]

    return str_msg


#- Main-----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    existe_cliente = True
    threads = list()
    sckt = init_server()

    #inputs = [sckt]
    inputs = [sckt, sys.stdin]

    print('Server ativo. Para fechar, digite "closeServer"')
    while existe_cliente:
        read, write, exception = select.select(inputs, [], [])
        for reading in read:
            if reading == sckt:
                newSckt, clientName = accept_clients(sckt)

                thread = threading.Thread(target=fulfill_requests, args=(newSckt, clientName))
                thread.start()
                threads.append(thread)
            elif reading == sys.stdin:
                msg = input()
                if msg == 'closeServer':
                    existe_cliente = False
                    print("\n\nAguardando clientes finais para finalizar o servidor")
                    for cliente in threads:
                        cliente.join()

    sckt.close()
