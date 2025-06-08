from DM import DM as DataMemory
from InstMem import InstMem as InstructionMemory  

class CentralMemory:
    def __init__(self, data_size=1024):
        self.data_mem = DataMemory(size=data_size)
        self.inst_mem = InstructionMemory()

    # Memoria de instrucciones
    def load_instructions(self, instructions):
        self.inst_mem.load_instructions(instructions)

    def fetch_instruction(self, address):
        return self.inst_mem.fetch(address)

    # Memoria de datos
    def read_data(self, address, mem_read=False):
        return self.data_mem.read(address, mem_read)

    def write_data(self, address, data, mem_write=False):
        self.data_mem.write(address, data, mem_write)

    def apply_delta(self, value, dlt_op=False):
        return self.data_mem.add_delta(value, dlt_op)

    # dump
    def dump(self):
        print("=== Instruction Memory ===")
        for i, instr in enumerate(self.inst_mem.memory):
            print(f"Address {i * 4:04}: {instr}")

        print("\n=== Data Memory (non-zero only) ===")
        for i, val in enumerate(self.data_mem.memory):
            if val != 0:
                print(f"Address {i:04}: 0x{val:08X}")

        print("\n=== Stored Keys ===")
        for key_id, key_data in self.data_mem.keys.items():
            print(f"Key[{key_id}]: {[f'0x{v:08X}' for v in key_data]}")