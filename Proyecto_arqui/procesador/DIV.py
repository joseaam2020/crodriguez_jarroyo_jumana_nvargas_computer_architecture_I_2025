from fu import FunctionalUnit
#Clase de DIV

class DIV(FunctionalUnit): 

    def __init__(self):  
        super().__init__("div",40)

    def execute(self, opcode: str, val1: int, val2: int):
        self.clocks -= 1
        try:
            if opcode == "DIV":
                if val2 == 0:
                    return 0, "Error: División por cero"
                return val1 // val2, ""
            else:
                return 0, f"Opcode no soportado: {opcode}"
        except Exception as e:
            return 0, f"Error de ejecución: {str(e)}"