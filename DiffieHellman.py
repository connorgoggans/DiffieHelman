import random
import socket
import sys
from math import gcd as bltin_gcd

primes = []
MAX_PRIME = 100
numbers = range(2, MAX_PRIME+1)
isServer = False
TCP_PORT = 5000
BUFFER_SIZE = 1024

def primRoots(modulo):
    required_set = {num for num in range(1, modulo) if bltin_gcd(num, modulo) }
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
    # create two prime numbers
    secure_random = random.SystemRandom()
    q = secure_random.choice(primes)
    primitiveRoots = []
    while primitiveRoots.len == 0:
        primitiveRoots = primRoots(q)
    alpha = primitiveRoots[0]
    xa = random.randint(1, q)
    public = pow(alpha, xa) % q

    # set up socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect
    soc.connect((TCP_ADDR, TCP_PORT))
    # send first message
    print("sending: " + str(num1) + " " + str(num2))
    soc.send(str(num1) + " " + str(num2))

    # get response
    data = soc.recv(BUFFER_SIZE)
    print("received " + data)

    num3 = int(data)
    private_num = secure_random.randint(0, 100)

    res = pow(num1, private_num) % num2

    print("sending: " + str(res))
    soc.send(str(res))

    data = soc.recv(BUFFER_SIZE)
    print("received" + data)

    num3 = int(data)

    # final calculation
    print("res = " + str(res))
    key = pow(num3, res) % num2
    print(key)

    # close
    soc.close()

def server():
    # set up socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect
    soc.bind((TCP_ADDR, TCP_PORT))
    soc.listen(1)

    conn, addr = soc.accept()
    num1 = 0
    num2 = 0
    
    secure_random = random.SystemRandom()
    private_num = secure_random.randint(0, 100)

    data = conn.recv(BUFFER_SIZE)
    print("received " + data)
    
    # parse out primes
    nums = data.split()
    num1 = int(nums[0])
    num2 = int(nums[1])

    # mod function
    res = pow(num1, private_num) % num2

    # send back result
    print("sending: " + str(res))
    conn.send(str(res))

    
    data = conn.recv(BUFFER_SIZE)
    print("received " + data)
    num3 = int(data)

    # final calculation
    key = pow(num3, res) % num2
    print("sending: " + str(key))
    conn.send(str(key))

    print(key)

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
    

    