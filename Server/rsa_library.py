import random

prime_number_1 = 277
prime_number_2 = 239

ON_low = '0x01'

'''
Euclid's algorithm for determining the greatest common divisor
Use iteration to make it faster for larger integers
'''
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

'''
Euclid's extended algorithm for finding the multiplicative inverse of two numbers
'''
def multiplicative_inverse(e, phi):
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_phi = phi
    
    while e > 0:
        temp1 = temp_phi//e
        temp2 = temp_phi - temp1 * e
        temp_phi = e
        e = temp2
        
        x = x2- temp1* x1
        y = d - temp1 * y1
        
        x2 = x1
        x1 = x
        d = y1
        y1 = y
    
    if temp_phi == 1:
        return d + phi

'''
Tests to see if a number is prime.
'''
def is_prime(num):
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(num**0.5)+2, 2):
        if num % n == 0:
            return False
    return True

def generate_keypair(p, q):
    if not (is_prime(p) and is_prime(q)):
        raise ValueError('Both numbers must be prime.')
    elif p == q:
        raise ValueError('p and q cannot be equal')
    #n = pq
    modulus = p * q

    #Phi is the totient of n
    L = (p-1) * (q-1)
    #print("L=",L)

    #Choose an integer e such that e and L(n) are coprime
    e = random.randrange(2,L)
    #print('E=',e)
    
    #Use Euclid's Algorithm to verify that e and L(n) are comprime
    g = gcd(e, L)
    #print('G=',g)
    while g != 1:
        e = random.randrange(2, L)
        #print("E=",e)
        g = gcd(e, L)
        #print("G=",g)
    #Use Extended Euclid's Algorithm to generate the private key
    d = multiplicative_inverse(e, L)
    #print("D=",d)
    
    #Return public and private keypair
    #Public key is (e, n) and private key is (d, n)
    return ((e, modulus), (d, modulus))
############################### EXERCISE 1 ###############################
def encrypt(public_key, hex_number):
    # Extrage componentele cheii publice
    e, n = public_key
    # Convertește numărul hex în întreg
    m = int(hex_number, 16)
    # Realizează criptarea folosind formula RSA
    c = pow(m, e, n)
    # Convertește textul cifrat înapoi în format hex
    return hex(c)
############################### EXERCISE 2 ###############################
def decrypt(private_key, encrypted_msg):
    # Extrage componentele cheii private
    d, n = private_key
    # Convertește mesajul criptat din hex în întreg
    c = int(encrypted_msg, 16)
    # Realizează decriptarea folosind formula RSA
    m = pow(c, d, n)
    # Convertește textul clar înapoi în format hex
    return hex(m)
############################### EXERCISE 3 ###############################
def low_check(hex_nr):
    # Convertește numărul hex în întreg
    num = int(hex_nr, 16)
    # Obține cel mai mic byte prin aplicarea unei măști de biți
    low_byte = num & 0xFF
    # Verifică dacă byte-ul mic este egal cu 0x01
    return low_byte == 0x01
############################### EXERCISE 4 ###############################
def number_check(hex_nr):
    # Convertește hex în întreg
    num = int(hex_nr, 16)
    # Extrage partea joasă (presupus a fi ultimul byte)
    low = num & 0xFF
    # Calculează partea înaltă prin deplasarea biților la dreapta
    high = num >> 8
    # Verifică dacă partea înaltă este complementul bit-cu-bit al părții joase
    return high == (~low & 0xFF) and low_check(hex_nr)
def test_functions():
    hex_values = ["0xFE01", "0xEE11", "0xFD02", "0xFC01"]

    public_key, private_key  = generate_keypair(277,239)# d și n 

    print("### Testare encrypt și decrypt ###")
    for hex_value in hex_values:
        encrypted = encrypt(public_key, hex_value)
        decrypted = decrypt(private_key, encrypted)
        print(f"Original: {hex_value}, Encrypted: {encrypted}, Decrypted: {decrypted}")

    print("\n### Testare low_check ###")
    for hex_value in hex_values:
        result = low_check(hex_value)
        print(f"{hex_value} low_check: {result}")

    print("\n### Testare number_check ###")
    for hex_value in hex_values:
        result = number_check(hex_value)
        print(f"{hex_value} number_check: {result}")

test_functions()
