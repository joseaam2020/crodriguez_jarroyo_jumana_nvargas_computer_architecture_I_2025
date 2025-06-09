class Instruction:
    def __init__(self, repr, op, dst, src1, src2, opname=None,imm=None,is_imm=False):
        self.issue = self.read_ops = self.ex_cmplt = self.write_res = -1
        self.imm = imm
        self.is_imm = is_imm
        self.op = op          # tipo funcional ('alu', 'memory', etc.)
        self.fi = dst         # destino
        self.fj = src1        # fuente 1
        self.fk = src2        # fuente 2
        self.repr = repr      # instrucción binaria original
        self.opname = opname  # nombre legible, como 'ADD', 'SUB', etc.
        self.result = None

    def __str__(self):
        return (
            f"Instrucción: {self.repr}\n"
            f"  Nombre     : {self.opname}\n"
            f"  Issue      : {self.issue}\n"
            f"  Read Ops   : {self.read_ops}\n"
            f"  Exec Done  : {self.ex_cmplt}\n"
            f"  Write Back : {self.write_res}\n"
            f"  Operación  : {self.op}\n"
            f"  Destino fi : {self.fi}\n"
            f"  Fuente fj  : {self.fj}\n"
            f"  Fuente fk  : {self.fk}\n"
            f"  Is Immeadiate : {self.is_imm}\n"
            f"  Immeadiate : {self.imm}\n"
        )


# Nombres legibles por opcode
opcode_names = {
    '0000': 'LOOP',
    '0001': 'SAXS',
    '0010': 'ADD',
    '0011': 'SUB',
    '0100': 'MUL',
    '0101': 'DIV',
    '0110': 'AND',
    '0111': 'OR',
    '1000': 'XOR',
    '1001': 'SHRL',
    '1010': 'SHLL',
    '1011': 'STOR',
    '1100': 'LOAD',
    '1101': 'STK',
    '1110': 'DLT',
}


def __branch(inst):
    op = 'alu'
    opcode = inst[:4]
    opname = opcode_names.get(opcode, 'UNKNOWN')
    fj = inst[8:21]
    fk = inst[4:8]
    return Instruction(inst, op, "0", fj, fk, opname)


def __mult(inst):
    op = 'mult'
    opcode = inst[:4]
    opname = opcode_names.get(opcode, 'UNKNOWN')
    if inst[4] == '0': 
        fi = inst[5:9]
        fj = inst[9:13]
        fk = inst[13:17]
        return Instruction(inst, op, fi, fj, fk, opname)
    else: #Immediate
        fi = inst[5:9]
        fj = inst[9:13]
        imm = int(inst[13:21], 2) 
        return Instruction(inst, op, fi, fj, None, opname,imm,True)


def __div(inst):
    op = 'div'
    opcode = inst[:4]
    opname = opcode_names.get(opcode, 'UNKNOWN')
    if inst[4] == '0':
        fi = inst[5:9]
        fj = inst[9:13]
        fk = inst[13:17]
        return Instruction(inst, op, fi, fj, fk, opname)
    else: #Immediate
        fi = inst[5:9]
        fj = inst[9:13]
        imm = int(inst[13:21], 2) 
        return Instruction(inst, op, fi, fj, None, opname,imm,True)


def __load_store(inst):
    op = 'memory'
    opcode = inst[:4]
    opname = opcode_names.get(opcode, 'UNKNOWN')
    fi = inst[4:8]
    fj = inst[8:12]
    fk = inst[12:16]
    return Instruction(inst, op, fi, fj, fk, opname)


def __arithmetic(inst):
    op = 'alu'
    opcode = inst[:4]
    opname = opcode_names.get(opcode, 'UNKNOWN')
    if inst[4] == '0': #Immediate
        fi = inst[5:9]
        fj = inst[9:13]
        fk = inst[13:17]
        return Instruction(inst, op, fi, fj, fk, opname)
    else: #Immediate
        fi = inst[5:9]
        fj = inst[9:13]
        imm = int(inst[13:21], 2) 
        return Instruction(inst, op, fi, fj, None, opname,imm,True)


def __specialized(inst):
    op = 'saxs'
    opcode = inst[:4]
    opname = opcode_names.get(opcode, 'UNKNOWN')
    if inst[4] == '0': #Immediate
        fi = inst[5:9]
        fj = inst[9:13]
        fk = inst[13:17]
        return Instruction(inst, op, fi, fj, fk, opname)
    else: #Immediate
        fi = inst[5:9]
        fj = inst[9:13]
        imm = int(inst[13:21], 2) 
        return Instruction(inst, op, fi, fj, None, opname,imm,True)

# Función para decodificar una instrucción binaria
def decode_instruction(binary_string):
    opcode = binary_string[:4]
    decoder = instructions.get(opcode)
    if decoder:
        return decoder(binary_string)
    else:
        return Instruction(binary_string, "unknown", None, None, None, "UNKNOWN")

# Diccionario principal de decodificación
instructions = {
    '0000': __branch,   # LOOP
    '0001': __specialized,  # SAXS
    '0010': __arithmetic,   # ADD
    '0011': __arithmetic,   # SUB
    '0100': __mult,         # MUL
    '0101': __div,          # DIV
    '0110': __arithmetic,   # AND
    '0111': __arithmetic,   # OR
    '1000': __arithmetic,   # XOR
    '1001': __arithmetic,   # SHRL
    '1010': __arithmetic,   # SHLL
    '1011': __load_store,   # STOR
    '1100': __load_store,   # LOAD
    '1101': __load_store,   # STK
    '1110': __load_store,   # DLT
}