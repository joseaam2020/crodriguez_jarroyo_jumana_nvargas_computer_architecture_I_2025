import struct
import os

# Constante delta para TEA (derivada del número áureo)
DELTA = 0x9E3779B9

def tea_encrypt(v, key):
    v0, v1 = v[0], v[1]
    sum_ = 0
    mask = 0xFFFFFFFF  # Máscara de 32 bits
    
    for _ in range(32):
        sum_ = (sum_ + DELTA) & mask
        v0 = (v0 + (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & mask
        v1 = (v1 + (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & mask
    
    return [v0, v1]

def tea_decrypt(v, key):
    v0, v1 = v[0], v[1]
    sum_ = (DELTA * 32) & 0xFFFFFFFF
    mask = 0xFFFFFFFF
    
    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & mask
        v0 = (v0 - (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & mask
        sum_ = (sum_ - DELTA) & mask
    
    return [v0, v1]

def encrypt_file(input_file, output_file, key):
    """
    Encripta un archivo usando TEA
    :param input_file: Ruta del archivo a encriptar
    :param output_file: Ruta del archivo encriptado de salida
    :param key: Clave de encriptación (lista de 4 enteros de 32 bits)
    """
    if len(key) != 4:
        raise ValueError("La clave debe tener exactamente 4 elementos (128 bits)")
    
    block_size = 8
    
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        while True:
            block = fin.read(block_size)
            if not block:
                break
            
            if len(block) < block_size:
                block = block.ljust(block_size, b'\0')
            
            v0, v1 = struct.unpack('!2I', block)
            encrypted = tea_encrypt([v0, v1], key)
            fout.write(struct.pack('!2I', *encrypted))

def decrypt_file(input_file, output_file, key):
    """
    Desencripta un archivo usando TEA
    :param input_file: Ruta del archivo encriptado
    :param output_file: Ruta del archivo desencriptado de salida
    :param key: Clave de encriptación (lista de 4 enteros de 32 bits)
    """
    if len(key) != 4:
        raise ValueError("La clave debe tener exactamente 4 elementos (128 bits)")
    
    block_size = 8
    
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        while True:
            block = fin.read(block_size)
            if not block:
                break
            
            v0, v1 = struct.unpack('!2I', block)
            decrypted = tea_decrypt([v0, v1], key)
            fout.write(struct.pack('!2I', *decrypted))

# Ejemplo de uso
if __name__ == "__main__":
    # Clave de 128 bits (4 palabras de 32 bits)
    key = [0xDEADBEEF, 0xDEADBEEF, 0xDEADBEEF, 0xDEADBEEF]
    
    # Archivos de entrada y salida
    input_file = 'jorge_luis.txt'
    encrypted_file = 'documento.enc'
    decrypted_file = 'documento_dec.txt'
    
    # Encriptar el archivo
    encrypt_file(input_file, encrypted_file, key)
    print(f"Archivo encriptado guardado como: {encrypted_file}")
    
    # Desencriptar el archivo
    decrypt_file(encrypted_file, decrypted_file, key)
    print(f"Archivo desencriptado guardado como: {decrypted_file}")
