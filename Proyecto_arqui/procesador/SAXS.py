from fu import FunctionalUnit
#Clase de SAXS

# Se hace individualmente, primero para v0 y luego para v1
class SAXS(FunctionalUnit): 

    def __init__(self,safe):  
        super().__init__("saxs",4)
        self.safe = safe
        self.zero_flag = False

    def execute(self, opcode: str, v: int, key: int, val3: int = 0):
        self.clocks -= 1
        try:
            if opcode == "SAXS":
                
                keys = self.safe.load_key(key)
                
                k0 = keys[0]
                k1 = keys[1]

                v_shifted_left = v << 4
                v_shifted_right = v >> 5

                sum1 = v_shifted_left + k0
                sum2 = v_shifted_right + k1

                result = sum1 ^ sum2
                return result
            else:
                return 0, f"Opcode no soportado: {opcode}"
        except Exception as e:
            return 0, f"Error de ejecución: {str(e)}"
