from socket import *

#- Global Variables-----------------------------------------------------------------------------------------------------
host = ''
porta = 4321

#- Main-----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    stop = False
    msg = ''

    sckt = socket(AF_INET, SOCK_STREAM)
    sckt.bind((host, porta))
    sckt.listen(1)

    newSckt, address = sckt.accept()

    while not stop:
        msg = newSckt.recv(100)
        if str(msg, encoding='utf-8') == 'closeConnection':
            stop = True
            print('Encerrando conexão...')
        else:
            newSckt.send(msg)

    sckt.close()
    newSckt.close()