#Clase del DataMemory
class DM:
    def __init__(self, size=1024):
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

