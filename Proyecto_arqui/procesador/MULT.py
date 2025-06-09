from fu import FunctionalUnit
#Clase de MULT

class MULT(FunctionalUnit): 

    def __init__(self):  
        super().__init__("mult",1)
        self.zero_flag = False

    def execute(self, opcode: str, val1: int, val2: int, val3: int = 0):
        self.clocks -= 1
        try:
            if opcode == "MULT":
                return val1 * val2, ""
            else:
                return 0, f"Opcode no soportado: {opcode}"
        except Exception as e:
            return 0, f"Error de ejecución: {str(e)}"