from socket import *

# - Global Variables----------------------------------------------------------------------------------------------------
host = 'localhost'
porta = 4321

# - Main----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    stop = False
    msg = ''

    sckt = socket()
    sckt.connect((host, porta))

    while not stop:
        msg = input('Digite o nome do arquivo\n')
        # Envia o nome do arquivo com a extensão (e não o caminho, pois não é responsabilidade do cliente saber)
        sckt.send(bytes(msg, encoding='utf-8'))
        if msg == 'closeConnection':
            stop = True
            print('Encerrando conexão...')
        else:
            msg = sckt.recv(1024)
            result = str(msg, encoding='utf-8')
            print(result)

    sckt.close()