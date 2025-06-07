from fu import FunctionalUnit
from Pipeline import Pipeline_marcador
#Clase de SAXS

# Se hace individualmente, primero para v0 y luego para v1
class SAXS(FunctionalUnit): 

    def _init_(self):  
        super._init_("saxs",4)
        self.safe = Pipeline_marcador().safe

    def execute(self, opcode: str, v: int, key: int):
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
