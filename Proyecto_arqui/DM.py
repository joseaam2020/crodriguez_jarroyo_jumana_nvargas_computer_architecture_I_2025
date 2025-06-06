#Clase del DataMemory
class DataMemory:
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

    def store_key(self, key_index, reg_r1, reg_r2, reg_r3, reg_r4, stk_op=False):
        if not stk_op:
            return
        key_data = [reg_r1, reg_r2, reg_r3, reg_r4]
        self.keys[key_index] = key_data

    def add_delta(self, register_value, dlt_op=False):
        DELTA = 0x9E3779B9
        if not dlt_op:
            return register_value
        return (register_value + DELTA) & 0xFFFFFFFF

    def saxs_operation(self, reg_r1_value, key_index, saxs_op=False):
        if not saxs_op:
            return 0
        if key_index not in self.keys:
            return 0
        
        key = self.keys[key_index]
        key_low = key[0]
        key_high = key[1]
        
        left_shifted = (reg_r1_value << 4) & 0xFFFFFFFF
        left_part = (left_shifted + key_low) & 0xFFFFFFFF
        
        right_shifted = reg_r1_value >> 5
        right_part = (right_shifted + key_high) & 0xFFFFFFFF
        
        result = left_part ^ right_part
        return result
