import random
import socket
import sys
from Crypto.Cipher import AES
import md5

primes = []
MAX_PRIME = 1000
numbers = range(2, MAX_PRIME+1)
isServer = False
isMiddle = False
TCP_PORT_CLIENT = 5000
TCP_PORT_SERVER = 3000
BUFFER_SIZE = 1024

# Calculate the greatest common demoninator of a & b
def gcd(a,b):
    while b != 0:
        a, b = b, a % b
    return a

# returns a list of primitive roots of modulo
def primRoots(modulo):
    required_set = {num for num in range(1, modulo) if gcd(num, modulo) }
    return [g for g in range(1, modulo) if required_set == {pow(g, powers, modulo)
            for powers in range(1, modulo)}]

# Use Sieve of Eratosthenes to generate primes up to MAX_PRIME
def generatePrimes():
    while numbers:
        cur = numbers[0]
        primes.append(cur)
        for i in range(cur, MAX_PRIME+1, cur):
            if i in numbers:
                numbers.remove(i)

class client_class:
    soc = 0
    key = 0
    def __init__(self, in_soc):
        self.soc = in_soc
        # create alpha and q
        secure_random = random.SystemRandom()
        primitiveRoots = []
        while len(primitiveRoots) == 0:
            q = secure_random.choice(primes)
            primitiveRoots = primRoots(q)
        alpha = primitiveRoots[0]
        # generate private key xa and public key ya
        xa = random.randint(1, q)
        ya = pow(alpha, xa) % q
        # send first message
        self.soc.send(str(alpha) + " " + str(q))
        # get response
        data = self.soc.recv(BUFFER_SIZE)
        # received b's public key
        yb = int(data)
        # send public key to b
        self.soc.send(str(ya))
        # calculate key
        self.key = pow(yb, xa) % q
        

class server_class:
    soc = 0
    key = 0
    def __init__(self, in_soc):
        self.soc = in_soc
        # receive alpha and q from a
        data = self.soc.recv(BUFFER_SIZE)
    
        # parse out alpha and q
        nums = data.split()
        alpha = int(nums[0])
        q = int(nums[1])

        # generate private key xb and public key yb
        xb = random.randint(1, q)
        yb = pow(alpha, xb) % q

        # send public key to a
        self.soc.send(str(yb))

        # receive a's public key
        data = self.soc.recv(BUFFER_SIZE)
        ya = int(data)

        # calculate key
        self.key = pow(ya, xb) % q

def client():

    # set up socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect
    soc.connect((TCP_ADDR, TCP_PORT_CLIENT))

    client_obj = client_class(soc)

    hash = md5.new(str(client_obj.key)).digest()
    print 'client key: ', client_obj.key
    obj = AES.new(hash, AES.MODE_CBC, 'This is an IV456')

    # start sending messages
    message = raw_input("Message: ")
    while message != "quit":
        ciphertext = obj.encrypt(padMessage(message))
        soc.send(ciphertext)
        message = raw_input("Message: ")

    
    # close
    soc.close()

def server():
    # set up socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect
    soc.bind((TCP_ADDR, TCP_PORT_SERVER))
    soc.listen(1)

    conn, addr = soc.accept()

    server_obj = server_class(conn)

    hash = md5.new(str(server_obj.key)).digest()
    print "server key: ", server_obj.key
    obj = AES.new(hash, AES.MODE_CBC, 'This is an IV456')

    data = conn.recv(BUFFER_SIZE)
    while data:
        print(obj.decrypt(data))
        data = conn.recv(BUFFER_SIZE)

    conn.close()

def middle():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind to client port
    soc.bind((TCP_ADDR, TCP_PORT_CLIENT))

    soc.listen(1)

    client, addr = soc.accept()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.connect((TCP_ADDR, TCP_PORT_SERVER))

    server_attacker = client_class(server)
    client_attacker = server_class(client)

    # start sending/receiving encrypted messages

    server_hash = md5.new(str(server_attacker.key)).digest()
    print "server key: ", server_attacker.key
    client_hash = md5.new(str(client_attacker.key)).digest()
    print "client key: ", client_attacker.key
    client_obj = AES.new(client_hash, AES.MODE_CBC, 'This is an IV456')
    server_obj = AES.new(server_hash, AES.MODE_CBC, 'This is an IV456')


    data = client.recv(BUFFER_SIZE)
    replacements = {
            "isn't": "is",
            "no": "yes",
            "wrong": "correct",
            "hello": "goodbye"
    }
    while data:
        plaintext = client_obj.decrypt(data)
        print("Interrupted Message: " + plaintext)

        for key in replacements.keys():
            plaintext = plaintext.replace(key, replacements[key])

        server.send(server_obj.encrypt(padMessage(plaintext)))
        data = client.recv(BUFFER_SIZE)


def padMessage(text):
    padding_len = 16 - len(text) % 16
    text += '\0' * padding_len
    return text


if __name__ == "__main__":
    # get input args, address will be arg 1
    args = sys.argv
    TCP_ADDR = args[1]

    if(len(args) == 3 and args[2] == '-s'):
        isServer = True
    elif(len(args) == 3 and args[2] == '-m'):
        isMiddle = True

    if(isServer):
        server()
    elif(isMiddle):
        generatePrimes()
        middle()
    else:
        # generate primes
        generatePrimes()
        client()