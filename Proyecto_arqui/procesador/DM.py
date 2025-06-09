import os
#Clase del DataMemory
class DM:
    def __init__(self, size=4096):
        self.memory = [0] * size
        self.size = size
        self.keys = {}

    def read(self, address, mem_read=False):
        if not mem_read:
            return 0
        if address < 0 or address >= self.size:
            return 0
        return self.memory[address]

    def write(self, address, data, mem_write=False):
        if not mem_write:
            return
        if address < 0 or address >= self.size:
            return
        self.memory[address] = data & 0xFFFFFFFF

    def add_delta(self, register_value, dlt_op=False):
        DELTA = 0x9E3779B9
        if not dlt_op:
            return register_value
        return (register_value + DELTA) & 0xFFFFFFFF
    
    def load_file(self, filename: str, start_address: int = 0):
        full_path = os.path.join(os.path.dirname(__file__), filename)
        with open(full_path, "rb") as f:
            data = f.read()
            for i in range(0, len(data), 4):
                # Tomamos bloques de 4 bytes
                word_bytes = data[i:i+4]
                # Rellenamos con ceros si el bloque es menor a 4 bytes (padding)
                word = int.from_bytes(word_bytes.ljust(4, b'\x00'), byteorder="little")
                # Escribimos la palabra en memoria
                dm.write(start_address + (i // 4), word, mem_write=True)

if __name__ == "__main__":
    dm = DM(size=4096)  # Instancia de tu clase de memoria
    dm.load_file("jorge_luis.txt", start_address=0)

    for i in range(0, 3250, 250):
        word = dm.read(i, mem_read=True)
        print(f"Mem[{i}]: {hex(word)}")
    xx = 2862
    word = dm.read(xx, mem_read=True)
    print(f"Mem[{xx}]: {hex(word)}")

