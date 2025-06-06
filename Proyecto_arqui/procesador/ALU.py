#Clase de ALU
#instrucciones: ADD,SUB,MUL,DIV,AND,OR,XOR,SHRL,SHLL,DLT,SAXS

class ALU: 

    def __init__(self, delta):  
        self.delta = delta

    def execute(self, opcode: str, val1: int, val2: int = 0):
        try:
            if opcode == "ADD":
                return val1 + val2, ""
            elif opcode == "SUB":
                return val1 - val2, ""
            elif opcode == "MUL":
                return val1 * val2, ""
            elif opcode == "DIV":
                if val2 == 0:
                    return 0, "División por cero"
                return val1 // val2, ""
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
            elif opcode == "DLT":
                return val1 + self.delta, ""
            elif opcode == "SAXS":
                low = (val2 & 0x00FF) + (val1 << 4)
                high = ((val2 >> 8) & 0x00FF) + (val1 >> 5)
                return low ^ high, ""
            else:
                return 0, f"Opcode no soportado: {opcode}"
        except Exception as e:
            return 0, f"Error de ejecución: {str(e)}"

alu = ALU(delta=10)       
result = alu.execute("ADD",4,5)
print(result)