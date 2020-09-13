from socket import *

#- Global Variables-----------------------------------------------------------------------------------------------------
host = 'localhost'
porta = 4321

#- Main-----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    stop = False
    msg = ''

    sckt = socket()
    sckt.connect((host, porta))

    while not stop:
        print('Digite uma mensagem para enviar')
        msg = input()
        if msg == 'closeConnection':
            stop = True
            print('Encerrando conexão com o servidor...')
        else:
            sckt.send(bytes(msg, encoding='utf-8'))
            msg = sckt.recv(1024)
            print(str(msg, encoding='utf-8'))

    sckt.close()