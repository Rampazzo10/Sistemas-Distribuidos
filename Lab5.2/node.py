from socket import *
import select


#- Global Variables-----------------------------------------------------------------------------------------------------
host = 'localhost'
message_size = 1024

#- Class Node-----------------------------------------------------------------------------------------------------------
class Node(object):
    def __init__(self, label, port):
        self.label = label
        self.ip = 'localhost'
        self.port = port
        self.values = dict()
        self.finger_table = list()

    def hash_key(self, key, n):
        result = 0
        try:
            result = int(float(key))%(2**n)
        except:
            try:
                for char in key:
                    result+= ord(char)
                result%= (2**n)
            except:
                print("Chave fora do padrão. Entre com uma string, inteiro ou float")

        return result


    # Admitiremos que sabe-se que a rede é completa e, portanto, as finger_tables são pré-definidas
    # Portanto, todas as finger_tables serão atualizadas de uma vez
    def fix_finger_table(self, n):
        for i in range(n):
            self.finger_table.append((self.label + 2**i)%(2**n))


    # Retona o valor para uma determinada chave, se existir. Caso contrário retorna "Key not found"
    def get_value(self, key):
        value = None
        if key in self.values:
            value = self.values[key]
        else:
            value = "Key not found"
        return value

    # find(noOrigem = 8, chave = 10) => finger_table[8] = [9, 10, 12, 0]
    # Retorna o nó destinado a armazenar determinada chave, independentemente de ela existir ou não
    def find_node(self, key, n):
        node_label = self.hash_key(key, n)
        next_node = None
        node_found = False
        if self.label == node_label:
            next_node = self.label
            node_found = True
        # Verificar se id está no intervalo (a,b]
          # Se a<b, basta verificar se a<id<=id
          # Se a>b, devemos verificar se id>a ou id<=b
        elif (self.label < self.finger_table[0] and self.label < node_label <= self.finger_table[0]) or \
             (self.label > self.finger_table[0] and (node_label > self.label or node_label <= self.finger_table[0])):
                next_node = self.finger_table[0]
                node_found = True
        else:
            for i in range(n-1, 0, -1):
                if (self.label < node_label and self.label < self.finger_table[i] <= node_label) or \
                   (self.label > node_label and (self.finger_table[0] > self.label or self.finger_table[0] <= node_label)):
                    next_node = self.finger_table[i]
                    break
            else:
                next_node = self.label

        return next_node, node_found


    # Insere o par chave/valor. Se já existir, sobrescreve
    def insert_key(self, key, value):
        self.values[str(key)] = value
