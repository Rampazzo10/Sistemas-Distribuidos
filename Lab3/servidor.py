from socket import *
import os
import select
import sys
import threading

#- Global Variables-----------------------------------------------------------------------------------------------------
host = ''
porta = 4321
#- Functions------------------------------------------------------------------------------------------------------------

def init_server():
    sckt = socket(AF_INET, SOCK_STREAM)
    sckt.bind((host, porta))
    #sckt.setblocking(False)
    sckt.listen(1)

    return sckt


# Camada de dados. Valida a existência do arquivo e retorna o conteúdo
def camada_dados(file_path):
    return os.path.exists(file_path)


# Camada em que o algoritmo de processamento será executado
def camada_processamento(file_path):
    word_frequency = dict()

    file_exists = camada_dados(file_path)

    if not file_exists:
        return "O arquivo não existe"
    else:
        word_frequency = count_words(file_path)
        sorted_word_frequency = sort_words(word_frequency)
        # Seleciona as 10 primeiras palavras da lista
        first_ten_words = sorted_word_frequency[:10]

        return first_ten_words


# Faz a contagem de palavras do arquivo
def count_words(file_path):
    word_frequency = dict()

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = remove_symbols(line)
            for word in line.split():
                if word.lower() not in word_frequency:
                    word_frequency[word.lower()] = 1
                else:
                    word_frequency[word.lower()] += 1

    return word_frequency

# Remove símbolos como '.', ',', '!', '?'
def remove_symbols(line):
    symbol_list = ['.', '?', '!', ',', '\'\'', '\"\"']
    for symbol in symbol_list:
        line = line.replace(symbol, '')


    return line

# Ordena as palavras mais frequentes
def sort_words(word_frequency):
    sorted_word_frequency = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)

    return sorted_word_frequency


def fulfill_requests(newSckt):
    stop = False
    folder_path = 'files'

    while not stop:
        msg = newSckt.recv(1024)
        msg = str(msg, encoding='utf-8')
        if msg == 'closeConnection':
            print('Encerrando conexão com cliente' + str(newSckt.getpeername()))
            newSckt.close()
            stop = True
        else:
            # Constrói caminho completo do arquivo texto
            file_path = os.path.join(os.path.dirname(__file__), folder_path, msg)
            # Resultado será uma lista de tuplas do tipo [('palavra1', <frequencia>), ('palavra2', <frequencia>), ... ,]
            first_ten_words = camada_processamento(file_path)
            # Cast feito para string para retornar a mensagem ao cliente
            first_ten_words = str(first_ten_words)
            newSckt.send(bytes(first_ten_words, encoding='utf-8'))


#- Main-----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    existe_cliente = True
    threads = list()
    msg = ''
    sckt = init_server()
    #inputs = [sckt]
    inputs = [sckt, sys.stdin]

    print('Server ativo. Para fechar, digite "closeServer"')
    while existe_cliente:
        read, write, exception = select.select(inputs, [], [])
        for reading in read:
            if reading == sckt:
                newSckt, address = sckt.accept()
                print('Estabelecendo conexão com cliente' + str(address))
                thread = threading.Thread(target=fulfill_requests, args=(newSckt, ))
                thread.start()
                threads.append(thread)
            elif reading == sys.stdin:
                msg = input()
                if msg == 'closeServer':
                    for cliente in threads:
                        cliente.join()
                        existe_cliente = False

    sckt.close()