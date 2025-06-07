from fu import FunctionalUnit
#Clase de MULT

class MULT(FunctionalUnit): 

    def _init_(self):  
        super._init_("mult",1)

    def execute(self, opcode: str, val1: int, val2: int):
        try:
            if opcode == "MULT":
                return val1 * val2, ""
            else:
                return 0, f"Opcode no soportado: {opcode}"
        except Exception as e:
            return 0, f"Error de ejecución: {str(e)}"