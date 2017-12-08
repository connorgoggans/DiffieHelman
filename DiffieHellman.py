import random
import socket
import sys
from Crypto.Cipher import AES
import md5

primes = []
MAX_PRIME = 100
numbers = range(2, MAX_PRIME+1)
isServer = False
TCP_PORT = 5000
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

def client():
    # create alpha and q
    secure_random = random.SystemRandom()
    q = 0
    primitiveRoots = []
    while len(primitiveRoots) == 0:
        q = secure_random.choice(primes)
        primitiveRoots = primRoots(q)
    alpha = primitiveRoots[0]

    # generate private key xa
    xa = random.randint(1, q)

    # generate public key ya
    ya = pow(alpha, xa) % q

    # set up socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect
    soc.connect((TCP_ADDR, TCP_PORT))
    # send first message
    soc.send(str(alpha) + " " + str(q))

    # get response
    data = soc.recv(BUFFER_SIZE)
    print("received " + data)

    # received b's public key
    yb = int(data)

    # send public key to b
    print("sending: " + str(ya))
    soc.send(str(ya))

    # calculate key
    key = pow(yb, xa) % q
    print(key)

    hash = md5.new(str(key)).digest()
    obj = AES.new(hash, AES.MODE_CBC, 'This is an IV456')
    message = 'The answer is no'
    ciphertext = obj.encrypt(message)

    soc.send(ciphertext)
    # close
    soc.close()

def server():
    # set up socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect
    soc.bind((TCP_ADDR, TCP_PORT))
    soc.listen(1)

    conn, addr = soc.accept()

    # receive alpha and q from a
    data = conn.recv(BUFFER_SIZE)
    print("received " + data)
    
    # parse out alpha and q
    nums = data.split()
    alpha = int(nums[0])
    q = int(nums[1])

    # generate private key xb
    xb = random.randint(1, q)

    # generate public key yb
    yb = pow(alpha, xb) % q

    # send public key to a
    print("sending: " + str(yb))
    conn.send(str(yb))

    # receive a's public key
    data = conn.recv(BUFFER_SIZE)
    print("received " + data)
    ya = int(data)

    # calculate key
    key = pow(ya, xb) % q
    print(key)

    data = conn.recv(BUFFER_SIZE)

    hash = md5.new(str(key)).digest()
    obj = AES.new(hash, AES.MODE_CBC, 'This is an IV456')
    print(obj.decrypt(data))

    conn.close()


if __name__ == "__main__":
    # get input args, address will be arg 1
    args = sys.argv
    TCP_ADDR = args[1]

    if(len(args) == 3 and args[2] == '-s'):
        isServer = True

    # generate primes
    generatePrimes()

    if(isServer):
        server()
    else:
        client()
    

    