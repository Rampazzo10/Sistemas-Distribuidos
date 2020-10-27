from socket import *
import select
import sys

#- Global Variables-----------------------------------------------------------------------------------------------------
host = 'localhost'
message_size = 1024
main_port = 4320
listen_port = 4319


#- Functions------------------------------------------------------------------------------------------------------------
def init_listen_sckt(port):
    global host

    sckt = socket(AF_INET, SOCK_STREAM)
    sckt.bind((host, port))
    sckt.listen(1)

    return sckt


#- Main-----------------------------------------------------------------------------------------------------------------

# Função que recebe a porta do programa principal e repassa a requisição para o noOrigem
def send_request_to_node(sckt):
    global message_size, host

    success = False
    msg = sckt.recv(message_size)
    msg = str(msg, encoding='utf-8')
    
    try:
        parameters = msg.split("#")
        call = parameters[0]
        node_port = int(parameters[1])


        node_sckt = socket()
        node_sckt.connect((host, node_port))

        node_sckt.sendall(bytes(call, encoding='utf-8'))
        success = True
    except:
        print(msg)

    return success
# Função que recebe a resposta da requisição feita (não necessariamente do noOrigem!!!!)
def wait_response_from_node(listen_sckt):
    global message_size
    
    newSckt, address = listen_sckt.accept()
    msg = newSckt.recv(message_size)
    msg = str(msg, encoding='utf-8')

    print(msg)


if __name__ == "__main__":
    stop = False
    msg = ''
    success = False

    listen_sckt = init_listen_sckt(listen_port)

    sckt = socket()
    inputs = [sckt, listen_sckt, sys.stdin]

    sckt.connect((host, main_port))
    while not stop:
        read, write, exception = select.select(inputs, [], [])
        for reading in read:
            if reading == sckt:
                success = send_request_to_node(sckt)
                if success:
                    wait_response_from_node(listen_sckt)
            elif reading == sys.stdin:
                msg = input()
                if msg == 'closeConnection':
                    stop = True
                    print('Encerrando conexão com o servidor...')
                else:
                    # busca(noOrigem, chave) ou insere(noOrigem, chave, valor)
                    sckt.sendall(bytes(msg, encoding='utf-8'))

    sckt.close()
