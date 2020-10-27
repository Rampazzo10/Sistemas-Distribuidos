from socket import *
import select
import sys
import multiprocessing
from node import Node
import time

#- Global Variables-----------------------------------------------------------------------------------------------------
host = ''
first_node_port = 4321
main_port = 4320
message_size = 1024
n = 0
last_label = 0
# Key = label; Value = Node
nodes = dict()
# Porta que o cliente escutará para receber a resposta das suas requisições
client_port = 4319
# Lista de processos filhos que representam um nó cada
processes = list()

#- Functions------------------------------------------------------------------------------------------------------------
def init_listen_sckt(port):
    global host

    sckt = socket(AF_INET, SOCK_STREAM)
    sckt.bind((host, port))
    sckt.listen(1)

    return sckt


def create_Chord_network():
    global n, nodes, last_label, first_node_port, processes
    

    n = int(input("Digite o número de 'n' bits da rede de Chord\n"))
    for i in range(2**n):
        node = Node(last_label, first_node_port)
        nodes[last_label] = node
        last_label+=1
        first_node_port+=1

    for i in range(2**n):
        process = multiprocessing.Process(target=start_node, args=(nodes[i],))
        process.start()
        processes.append(process)


# Função que executará o nó
def start_node(node):

    stop = False
    node.fix_finger_table(n)
    sckt = init_listen_sckt(node.port)

    while not stop:
        newSckt, address = sckt.accept()
        inputs = [newSckt]
        read, write, exception = select.select(inputs, [], [])
        for reading in read:
            if reading == newSckt:
                stop = fullfill_request(newSckt, node)
                newSckt.close()
    print("Nó " + str(node.label) + " saindo da rede...")

# Recebe uma chamada de função do cliente em forma de mensagem:
    # busca(chave)
    # insere(chave, valor)
def fullfill_request(sckt, node):
    global message_size, n, client_port, nodes
    stop = False
    node_found = False
    node_label = None

    msg = sckt.recv(message_size)
    msg = str(msg, encoding='utf-8')
    if msg == 'closeConnection':
        stop = True
    else:
        function, parameters = parse_message(msg)
        chave = parameters[0]
        if function == "end_busca":
            msg = "Valor = {}. Nó = {}".format(node.get_value(chave), node.label)
            send_msg(msg, client_port)
        elif function == "end_insere":
            valor = parameters[1]
            node.insert_key(chave, valor)
            msg = "Chave " + chave + " inserida no nó " + str(node.label)
            send_msg(msg, client_port)
        elif function in ['busca', 'insere']:
            node_label, node_found = node.find_node(chave, n)
            port = nodes[node_label].port
            if not node_found:
                # Enviar mensagem pra outro nó continuar a busca
                send_msg(msg, port)
            else:
                # O nó encontrado sempre será o sucessor do node atual
                # Portanto, devemos enviar uma mensagem para ele indicando que ele é o detentor da chave
                if function == "busca":
                    # Enviar mensagem de end(chave) para outro nó, indicando fim da busca
                      # e que trata-se de uma operação de recuperação do valor da chave
                    msg = "end_busca(" + str(chave) + ")"
                    send_msg(msg, port)
                elif function == "insere":
                    valor = parameters[1]
                    # Enviar mensagem de end_insere(chave) para outro nó, indicando o fim da busca
                      # e que trata-se de uma operação de inserção
                    
                    msg = "end_insere(" + str(chave) + ", " + str(valor) + ")"
                    send_msg(msg, port)
        else:
            print("Função '" + function + " 'indisponível")

    return stop

def parse_message(msg):
    msg = msg.replace(" ", "")
    function = msg[:msg.find("(")]
    parameters = msg[msg.find("(") + 1:msg.find(")")].split(",")

    return function, parameters

def send_msg(msg, port):
    global nodes
    
    sckt = socket()
    sckt.connect(('localhost', port))
    sckt.sendall(bytes(msg, encoding='utf-8'))
    sckt.close()
    
    

def close_node_connections():
    global nodes

    for node in nodes.values():
        msg = 'closeConnection'
        send_msg(msg, node.port)


#- Main-----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    existe_cliente = True
    newSckt = ''

    main_sckt = init_listen_sckt(main_port)
    inputs = [main_sckt]
    print('Server ativo. Para fechar, digite "closeServer"')
    create_Chord_network()


    while existe_cliente:
        read, write, exception = select.select(inputs, [], [])
        for reading in read:
            if reading == main_sckt:
                newSckt, address = main_sckt.accept()
                inputs.append(newSckt)
            # busca(noOrigem, chave) ou insere(noOrigem, chave, valor)
            elif reading == newSckt:
                msg = newSckt.recv(message_size)
                msg = str(msg, encoding='utf-8')
                if not msg:
                    existe_cliente = False
                    close_node_connections()
                else:
                    function, parameters = parse_message(msg)
                    try:
                        # busca(node_port, chave) ou insere(node_port, chave, valor)
                        # O caracter '#' é para facilitar o parsing da mensagem do lado cliente com [função, porta]
                        noOrigem = int(parameters[0])
                        node_port = nodes[noOrigem].port
                        msg = function + "(" +  ", ".join(parameters[1:]) + ")#" + str(node_port)   
                    except:
                        msg = "Nó " + parameters[0] + " não elegível na Rede de Chord"
                    
                    newSckt.sendall(bytes(msg, encoding='utf-8'))
    
    
    newSckt.close()
    main_sckt.close()
