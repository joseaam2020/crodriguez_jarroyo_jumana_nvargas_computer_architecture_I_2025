from ParserMarcador import Scoreboard

class Marcador:
    def __init__(self, scoreboard):
        self.scoreboard = scoreboard
        self.pc = 0

    def puede_ejecutar(self, instruccion):
        # Aquí se verifica si no hay dependencias RAW, WAR, WAW, etc.
        
        return True

    def ins_completa(self, instruccion):
        # Marca la instrucción como completada
        instruccion.terminada = True

    def obtener_siguiente(self):
        if self.pc < len(self.scoreboard.instructions):
            instr = self.scoreboard.instructions[self.pc]
            self.pc += 1
            return instr
        else:
            return None
