# Los codigos de ScoreboardParser y Scoreboard estan basados en:
# https://github.com/MJunaidAhmad/scoreboard-simulation
# Autor: MJunaidAhmad
# Repositorio con licencia pública. Se respetan los derechos del autor original.
import os
from Instruccion import instructions as inst_funcs
from fu import FunctionalUnit, FORMAT_HEADER


class ScoreboardParser:
    def __init__(self, bin_file,sb=None):
        self.asm = bin_file
        self.sb = sb if sb is not None else Scoreboard()

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
    def parse_from_memory(instr_list, sb=None):
        parser = ScoreboardParser(None, sb) if sb else ScoreboardParser(None)
        for instr_bin in instr_list:
            parser.__parse_inst(instr_bin)
        return parser.sb

    


class Scoreboard:

  def __init__(self):
    self.units = []           # array of FunctionalUnit
    self.instructions = []    # array of Instruction
    self.reg_status = {}      # register status table
    self.pc = 0               # program counter
    self.clock = 1            # processor clock
    self.wait_branch = False


  def __str__(self):
    result = 'CLOCK: %d\n' % (self.clock)
    result += FORMAT_HEADER + '\n'
    for unit in self.units:
      result += str(unit) + '\n'
    return result


  """ Checks to see if the scoreboard is done executing. Returns True if so"""
  def done(self):
    done_executing = True
    out_of_insts = not self.has_remaining_insts()
    if out_of_insts:
      for fu in self.units:
        if fu.busy:
          done_executing = False
          break
    return out_of_insts and done_executing


  """ Checks to see if there are instructions left to issue to the
  scoreboard and returns True if so"""
  def has_remaining_insts(self):
    return self.pc < len(self.instructions)


  """ Determines if an instruction is able to be issued"""
  def can_issue(self, inst, fu):
    if inst is None:
      return False
    else:
      return inst.op == fu.type and not fu.busy and not (inst.fi in self.reg_status) and not self.wait_branch


  """ Determines if an instruction is able to enter the read operands phase"""
  def can_read_operands(self, fu):
    return fu.busy and fu.rj and fu.rk


  """ Determines if an instruction is able to enter the execute phase"""
  def can_execute(self, fu):
    # check to make sure we've read operands, the functional unit
    # is actually in use, and has clocks remaining
    if not ((not fu.rj and not fu.rk) and fu.issued()):
        return False
    
    # Para la instrucción STK, verificar adicionalmente que R1-R4 estén disponibles
    if fu.opname == "STK":
        # Verificar que los registros R1-R4 no estén siendo escritos por otras unidades
        for reg in ['0001', '0010', '0011', '0100']:  # Representación binaria de R1-R4
            if reg in self.reg_status:
                # Si alguno de los registros está siendo escrito por otra unidad, no podemos ejecutar
                return False
    
    return True


  """ Determines if an instruction is able to enter the writeback phase"""
  def can_write_back(self, fu):
    can_write_back = False
    for f in self.units:
      can_write_back = (f.fj != fu.fi or not f.rj) and (f.fk != fu.fi or not f.rk)
      if not can_write_back:
        break
    return can_write_back


  """ Issues an instruction to the scoreboard"""
  def issue(self, inst, fu):
    fu.issue(inst, self.reg_status)
    self.reg_status[inst.fi] = fu
    self.instructions[self.pc].issue = self.clock
    fu.inst_pc = self.pc
    if inst.opname == "LOOP":
      self.wait_branch = True


  """ Read operands stage of the scoreboard"""
  def read_operands(self, fu):
    fu.read_operands()
    self.instructions[fu.inst_pc].read_ops = self.clock

  """ Tick: simulates a clock cycle in the scoreboard"""
  def tick(self):
    # unlock all functional units
    for fu in self.units:
      fu.lock = False

    # Get the next instruction based on the PC
    next_instruction = self.instructions[self.pc] if self.has_remaining_insts() else None

    for fu in self.units:
      if self.can_issue(next_instruction, fu):
        self.issue(next_instruction, fu)
        self.pc += 1
        fu.lock = True
        #print(f"[{self.clock}] Issued instruction to FU {fu.type}")
      elif self.can_read_operands(fu):
        self.read_operands(fu)
        fu.lock = True
        #print(f"[{self.clock}] Read operands in FU {fu.type}")
      elif self.can_execute(fu):
        self.execute(fu)
        fu.lock = True
        #print(f"[{self.clock}] Executing in FU {fu.type}")
      elif fu.issued():
        # the functional unit is in use but can't do anything
        fu.lock = True
        #print(f"[{self.clock}] Stalled FU {fu.type}, waiting on dependencies")

    for fu in self.units:
      if not fu.lock and self.can_write_back(fu):
        self.write_back(fu)
        #print(f"[{self.clock}] Wrote Back instruction to FU {fu.type}")

    self.clock += 1


"""if __name__ == '__main__':
 #sb = ScoreboardParser.scoreboard_for_asm()

  while not sb.done():
    sb.tick()"""


#scoreboard = ScoreboardParser.scoreboard_for_asm("salida.txt")

"""
print(scoreboard.instructions)
print(scoreboard.instructions[0].op)
print(scoreboard.instructions[1].op)
print(scoreboard.instructions[2].op)
print(scoreboard.instructions[3].op)
"""
