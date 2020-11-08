from socket import *
import select
import sys
import time
import threading

# - Global Variables-----------------------------------------------------------------------------------------------------
port_list = [4321, 4322, 4323, 4324]
message_size = 1024
replica_host = ''
client_host = 'localhost'
id = 0
hat_owner = False
X = None
history = list()

lock = threading.Lock()

# - Functions------------------------------------------------------------------------------------------------------------
def init_replica(id):
    global replica_host, port_list

    port = port_list[id-1]
    sckt = socket(AF_INET, SOCK_STREAM)
    try:
        sckt.bind((replica_host, port))
        sckt.listen(1)
    except Exception as e:
        print("Erro ao fazer o bind da porta: {}".format(e))

    return sckt


def parse_message(msg):
    msg = msg.replace(" ", "")
    function = msg[:msg.find("(")]
    parameters = msg[msg.find("(") + 1:msg.find(")")].split(",")

    return function, parameters


def fullfill_request(function, parameters):
    global message_size, hat_owner, id, lock

    # Requisições feitas pelo cliente da própria réplica
    if function == 'write_value':
        write_value(parameters[0])
    elif function == 'read_value':
        read_value()
    elif function == 'read_history':
        read_history()
    # Requisições feitas por clientes de OUTRAS réplicas
    elif function == 'hat_requested':
        hat_requested(parameters[0])
    elif function == 'update_value':
        # update_value(hat_owner_id, value, hat_requester_id)
        update_value(parameters[0], parameters[1])
        if(id==int(parameters[2])):
            lock.acquire()
            hat_owner = True
            lock.release()
    else:
        print("Função '" + function + " 'indisponível")



# Se possuir o chapéu, concede para a réplica requisitante e dispara a atualização das outras réplicas
def hat_requested(idReplica):
    global hat_owner, id, lock

    if hat_owner:
        send_broadcast_update(idReplica)
        lock.acquire()
        hat_owner = False
        lock.release()


# Apenas envia uma mensagem para todas as outras réplicas
def broadcast(msg):
    global port_list, id

    for i in range(len(port_list)):
        # Pulando a própria réplica
        if i+1 != id:
            nsckt = socket()
            nsckt.connect((client_host, port_list[i]))
            nsckt.sendall(bytes(msg, encoding='utf-8'))
            nsckt.close()



# Faz o broadcast para atualização do valor de X em outras réplicas
def send_broadcast_update(idReplica):
    global id, X
    msg = 'update_value({}, {},{})'.format(id, X, idReplica)
    broadcast(msg)


# Faz o broadcast para requisição do chapéu a outras réplicas
def ask_for_hat():
    global id
    msg = 'hat_requested(' + str(id) + ')'
    broadcast(msg)


# Atualiza o valor de X segundo solicitação da própria réplica
def write_value(value):
    global X, hat_owner, id

    if not hat_owner:
        ask_for_hat()
        # O time.sleep é apenas para não onerar tanto a espera ocupada. Ele não interfere na corretude do código
        while(hat_owner==False):
            time.sleep(0.1)
    update_value(id, value)


# Atualiza o valor de X segundo solicitação de outra réplica e salva no histórico
def update_value(idReplica, value):
    global X, lock
    lock.acquire()
    X = value
    log_history(idReplica, value)
    lock.release()


def read_value():
    global X
    print("X = {}".format(X))


def read_history():
    global history
    print(history)


def log_history(idReplica, value):
    global history
    history.append("id_{}: X = {}".format(idReplica, value))


# - Main----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    existe_cliente = True
    newSckt = ''
    
    while id < 1 or id > 4:
        print("Entre com um id entre 1 e 4")
        id = int(input())
    if id == 1:
        hat_owner = True
    sckt = init_replica(id)
    inputs = [sckt, sys.stdin]

    print("============================================================================================================"
          "===================================================="
          "'\033[1m'\nTutorial - Comandos disponiveis:\n"
          "read_value(): Printa o valor atual de X na própria réplica\n"
          "read_history: Printa o histórico de alterações de X recebidas pela própria réplica (Atualizadas por ela mesma"
          "ou recebidas de um broadcast)\n"
          "write_value(X): Atualiza o valor de X na própria réplica\n"
          "close: Fecha a réplica. Obs.: a saída de uma réplica é considerada uma falha pela aplicação, que não"
          "possui tratamento. Recomenda-se utilizar esse comando apenas caso não deseje mais utilizá-la.\n"
          "Essas são as únicas funcionalidades elegíveis para o cliente. Qualquer outra função neste programa "
          "serve apenas para coordenar o correto funcionamento da aplicação\n"
          "============================================================================================================"
          "====================================================\n\n")

    while existe_cliente:
        read, write, exception = select.select(inputs, [], [])
        for reading in read:
            # Apenas aceita novas requisições
            if reading == sckt:
                newSckt, address = sckt.accept()
                inputs.append(newSckt)
            # Recebe mensagens de outras réplicas: atualização do dado ou pedido do chapéu
            elif reading == newSckt:
                msg = newSckt.recv(message_size)
                msg = str(msg, encoding='utf-8')
                if not msg:
                    print("Réplica em comunicação desconectada")
                else:
                    function, parameters = parse_message(msg)
                    # hat_requested() ou update_value(idReplica, value)
                    fullfill_request(function, parameters)
                newSckt.close()
                inputs.remove(newSckt)
            elif reading == sys.stdin:
                msg = input()
                # close
                if msg == 'close':
                    existe_cliente = False
                else:

                    # read_value(), read_history(), write_value(value)
                    function, parameters = parse_message(msg)
                    thread = threading.Thread(target=fullfill_request, args=(function, parameters))
                    thread.start()
    sckt.close()
