from fu import FunctionalUnit
#Clase de ALU
#instrucciones: ADD,SUB,MUL,DIV,AND,OR,XOR,SHRL,SHLL,DLT,SAXS

class ALU(FunctionalUnit): 

    def _init_(self, delta):  
        super._init_("alu",1)
        self.delta = delta
        self.zero_flag = False

    def execute(self, opcode: str, val1: int, val2: int = 0):
        try:
            if opcode == "ADD":
                return val1 + val2, ""
            elif opcode == "SUB":
                return val1 - val2, ""
            elif opcode == "AND":
                return val1 & val2, ""
            elif opcode == "OR":
                return val1 | val2, ""
            elif opcode == "XOR":
                return val1 ^ val2, ""
            elif opcode == "SHRL":
                return val1 >> val2, ""
            elif opcode == "SHLL":
                return val1 << val2, ""
            elif opcode == "LOOP":
                if val1 == 0:
                    self.zero_flag = True
                    return val2
                else:
                    self.zero_flag = False            
            else:
                return 0, f"Opcode no soportado: {opcode}"
        except Exception as e:
            return 0, f"Error de ejecución: {str(e)}"