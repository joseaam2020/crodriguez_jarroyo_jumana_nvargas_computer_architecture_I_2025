from fu import FunctionalUnit
#Clase de MEMORY

class Memory(FunctionalUnit): 

    def __init__(self,safe,memory, registros):  
        super().__init__("memory",3)
        self.zero_flag = False
        self.memory = memory
        self.safe = safe 
        self.regs = registros 

    def execute(self, opcode: str, address: int = 0, val: int = 0, val2: int = 0):
        self.clocks -= 1
        try:
            if opcode == "LOAD":
                addr = address + val
                return self.memory.read_data(address, True)
            elif opcode == "STOR":
                addr = address + val
                self.memory.write_data(addr, val2, True)
            elif opcode == "STK":
                self.safe.store_key(val2, self.regs.regs[1], self.regs.regs[2], self.regs.regs[3], self.regs.regs[4])
            elif opcode == "DLT":
                return self.memory.apply_delta(val2, True)
            else:
                return 0, f"Opcode no soportado: {opcode}"
        except Exception as e:
            return 0, f"Error de ejecución: {str(e)}"