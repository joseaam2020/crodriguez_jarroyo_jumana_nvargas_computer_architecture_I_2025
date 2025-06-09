#from procesador import ALU,DM,InstMem,RegisterFile
from ALU import ALU
from RegisterFile import RegisterFile
from Safe import Safe
from SAXS import SAXS
from MemoriaCentral import CentralMemory
from ParserMarcador import ScoreboardParser,Scoreboard 
from MEMORY import Memory as MemUnit
from MULT import MULT as MultUnit
from DIV import DIV as DivUnit

class Pipeline_marcador (Scoreboard):
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, inst, data=None):
        super().__init__()
        #Estado Arquitectonico
        self.registros = RegisterFile()
        self.safe = Safe()
        self.memory = CentralMemory()
        self.memory.load_instructions(inst)
        self.scoreboard = ScoreboardParser.parse_from_memory(self.memory.inst_mem.memory, self)

        #Unidades funcionales
        self.alu1 = ALU()
        self.alu2 = ALU()
        self.memu1 = MemUnit(self.safe,self.memory,self.registros.regs[1:5]) #Esto puede tirar error, acordarse XD
        self.memu2 = MemUnit(self.safe,self.memory,self.registros.regs[1:5])
        self.saxs = SAXS(self.safe)
        self.mult = MultUnit()
        self.div = DivUnit()

        self.units = [
            self.alu1,
            self.alu2,
            self.memu1,
            self.memu2,
            self.saxs,
            self.mult, 
            self.div
        ]
    
    """ Execute stage of the scoreboard"""
    def execute(self, fu):
        inst = self.instructions[fu.inst_pc]

        fj_val = None
        fk_val = None 

        if inst.fj is not None:
            fj_index = int(inst.fj, 2)
            fj_val = self.registros.regs[fj_index]
        
        if inst.fk is not None:
            fk_index = int(inst.fk, 2)
            fk_val = self.registros.regs[fk_index]
        elif inst.is_imm:
            print(inst.imm)
            fk_val = inst.imm   

        result = fu.execute(inst.opname, fj_val, fk_val)
        inst.result = result
        print(
            f"Name: {inst.opname}",
            f"Is Imm: {inst.is_imm}",
            f"Imm: {inst.imm}",
            f"Clock: {fu.clocks}",
            f"fj_val: {fj_val}",
            f"fk_val: {fk_val}",
            f"result: {result}",
        )
        
        
        if fu.clocks == 0:
            self.instructions[fu.inst_pc].ex_cmplt = self.clock

    
    """ Writeback stage of the scoreboard"""
    def write_back(self, fu): 
        inst = self.instructions[fu.inst_pc]

        if inst.fi and inst.result is not None:
            fi_index = int(inst.fi, 2)
            self.registros.regs[fi_index] = inst.result

        #Write back confirmation 
        fu.write_back(self.units)
        self.instructions[fu.inst_pc].write_res = self.clock
        # clear out the result register status
        del self.reg_status[fu.fi]
        fu.clear()
    
sb = Pipeline_marcador("salida.txt")

"""
print(scoreboard.instructions)
print(scoreboard.instructions[0].op)
print(scoreboard.instructions[1].op)
print(scoreboard.instructions[2].op)
print(scoreboard.instructions[3].op)"""

while not sb.done():
    sb.tick()

for instruction in sb.instructions:
    print(str(instruction))

