class Instruction:

  def __init__(self, repr, op, dst, src1, src2):
    self.issue = self.read_ops = self.ex_cmplt = self.write_res = -1
    self.op = op          # instruction operation
    self.fi = dst         # destination register
    self.fj = src1        # source register
    self.fk = src2        # source register
    self.repr = repr      # the string representation

"""Load immediate instruction"""
def __branch(inst):
  op = 'branch'
  fi = inst[8:21]
  fj = inst[4:8]
  return Instruction(inst, op, fi, fj, None)

"""Generic load or store instruction"""
def __load_store(inst):
  op = 'memory'
  fi = inst[4:8]
  fj = inst[8:16]
  return Instruction(inst, op, fi, fj, None)

"""add, subtract, multiply or divide instruction"""
def __arithmetic(inst):
  op = 'alu'
  if inst[4] == 0:
    fi = inst[5:9]
    fj = inst[9:13]
    fk = inst[13:17]
    return Instruction(inst, op, fi, fj, fk)
  else: # inmediatos
    fi = inst[5:9]
    fj = inst[9:13]
    return Instruction(inst, op, fi, fj, None)

instructions = {
    '0000':     __branch,               # branch unit
    '0001':     __arithmetic,
    '0010':     __arithmetic,        # ADD unit
    '0011':     __arithmetic,
    '0100':     __arithmetic,    # MULT unit
    '0101':    __arithmetic,       # DIV unit 
    '0110':   __arithmetic,
    '0111':    __arithmetic,
    '1000':   __arithmetic,
    '1001':   __arithmetic,       
    '1010':   __arithmetic,
    '1011':  __load_store,       
    '1100':   __load_store,
    '1101':  __load_store,       
    '1110':   __arithmetic,       
    }