import os
from Instruccion import instructions as inst_funcs

class ScoreboardParser:
    def __init__(self, bin_file):
        self.asm = bin_file
        self.sb = Scoreboard()
        self.__init_default_units()

    # Inicializa 2 unidades por tipo
    def __init_default_units(self):
        for _ in range(2):
            #self.sb.units.append(FunctionalUnit('memory', clocks=1))
            #self.sb.units.append(FunctionalUnit('alu', clocks=1))
            #self.sb.units.append(FunctionalUnit('branch', clocks=1))
            return 0

    # Traduce binario a instrucción
    def __parse_inst(self, bin_instr):
        opcode = bin_instr[0:4]
        instruction_func = inst_funcs.get(opcode)
        if instruction_func is None:
            raise ValueError(f"Opcode desconocido: {opcode}")
        instruction = instruction_func(bin_instr)
        self.sb.instructions.append(instruction)

    # Lee el archivo binario y lo parsea
    @staticmethod
    def scoreboard_for_asm(bin_file):
        full_path = os.path.join(os.path.dirname(__file__), bin_file)
        parser = ScoreboardParser(full_path)
        with open(parser.asm, 'r') as f:
            instrucciones_binarias = [line.strip() for line in f if line.strip()]
        for instr_bin in instrucciones_binarias:
            parser.__parse_inst(instr_bin)
        return parser.sb
    
class Scoreboard:

  def __init__(self):
    self.units = []           # array of FunctionalUnit
    self.instructions = []    # array of Instruction
    self.reg_status = {}      # register status table
    self.pc = 0               # program counter
    self.clock = 1            # processor clock
    
scoreboard = ScoreboardParser.scoreboard_for_asm("..\salida.txt")

print(scoreboard.instructions)
print(scoreboard.instructions[0].op)
print(scoreboard.instructions[1].op)
print(scoreboard.instructions[2].op)
print(scoreboard.instructions[3].op)

