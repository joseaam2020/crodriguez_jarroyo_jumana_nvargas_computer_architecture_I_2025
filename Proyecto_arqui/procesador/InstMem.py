import os

class InstMem:
    def __init__(self):
        self.memory = []

    def load_instructions(self, filename):
        full_path = os.path.join(os.path.dirname(__file__), filename)
        with open(full_path, 'r') as f:
            self.memory = [line.strip() for line in f if line.strip()]

    def fetch(self, address):
        index = address // 4  # Cada instrucción ocupa 4 bytes
        if index < 0 or index >= len(self.memory):
            raise IndexError("No existen más instrucciones")
        return self.memory[index]
"""
# Uso
imem = InstMem()
imem.load_instructions("salida.txt")

# Prueba de lectura secuencial
pc = 0
try:
    while True:
        inst = imem.fetch(pc)
        print(f"Instrucción en dirección {pc}: {inst}")
        pc += 4
except IndexError:
    print("Fin de instrucciones.")"""

