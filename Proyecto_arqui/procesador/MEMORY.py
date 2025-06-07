from fu import FunctionalUnit
from Pipeline import Pipeline_marcador
#Clase de MEMORY

class Memory(FunctionalUnit): 

    def _init_(self):  
        super._init_("mem",3)
        self.memory = Pipeline_marcador().memoria
        self.safe = Pipeline_marcador().safe

    def execute(self, opcode: str, address: int = 0, val: int = 0):
        try:
            if opcode == "LOAD":
                return self.memory.read_data(address, False)
            elif opcode == "STOR":
                self.memory.write_data(address, val, False)
            elif opcode == "STK":
                regs = Pipeline_marcador().registros.regs[1:5]
                self.safe.store_key(val, regs[0], regs[1], regs[2], regs[3])
            elif opcode == "DLT":
                return self.memory.apply_delta(val, False)
            else:
                return 0, f"Opcode no soportado: {opcode}"
        except Exception as e:
            return 0, f"Error de ejecución: {str(e)}"