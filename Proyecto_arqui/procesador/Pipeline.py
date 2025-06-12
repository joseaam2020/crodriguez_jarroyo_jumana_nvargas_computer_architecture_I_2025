#from procesador import ALU,DM,InstMem,RegisterFile
import os
from math import ceil
from ALU import ALU
from RegisterFile import RegisterFile
from Safe import Safe
from SAXS import SAXS
from MemoriaCentral import CentralMemory
from ParserMarcador import ScoreboardParser,Scoreboard 
from MEMORY import Memory as MemUnit
from MULT import MULT as MultUnit
from DIV import DIV as DivUnit
from traductor import ensamblar

def save_encrypted_file(sb, data_file):    
    try:
        original_path = data_file
        enc_path = os.path.splitext(original_path)[0] + ".enc"
        
        original_size = os.path.getsize(original_path)
        total_bytes = ceil(original_size / 8) * 8  # padding a múltiplo de 8

        encrypted_data = bytearray()

        for i in range(0, total_bytes, 8):
            # Leer dos palabras de 32 bits (4 bytes cada una)
            word1 = sb.memory.data_mem.read((i // 4) + 4, True)
            word2 = sb.memory.data_mem.read((i // 4) + 5, True)

            # Convertir a bytes en little-endian
            word_bytes1 = word1.to_bytes(4, byteorder='little')
            word_bytes2 = word2.to_bytes(4, byteorder='little')

            encrypted_data.extend(word_bytes1 + word_bytes2)

        with open(enc_path, 'wb') as f:
            f.write(encrypted_data)
        print(f"Archivo encriptado guardado como: {enc_path}")
    
    except Exception as e:
        print(f"Error al guardar archivo encriptado: {str(e)}")

class Pipeline_marcador (Scoreboard):
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, inst, data=None, key=None):
        super().__init__()
        #Estado Arquitectonico
        self.registros = RegisterFile()
        self.safe = Safe()
        self.memory = CentralMemory(15360)
        self.memory.load_instructions(inst)
        if data:
            self.memory.data_mem.load_file(data, start_address=4)
        if key:
            self.memory.data_mem.load_key(key, start_address=0)
        self.scoreboard = ScoreboardParser.parse_from_memory(self.memory.inst_mem.memory, self)

        #Unidades funcionales
        self.alu1 = ALU()
        self.alu2 = ALU()
        self.memu1 = MemUnit(self.safe,self.memory,self.registros) 
        self.memu2 = MemUnit(self.safe,self.memory,self.registros)
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

        if inst.fi is not None:
            fi_index = int(fu.fi, 2)
            fi_val = self.registros.regs[fi_index]
        else:
            fi_index = 0

        if inst.fj is not None:
            fj_index = int(inst.fj, 2)
            if inst.opname != "LOOP":
                fj_val = self.registros.regs[fj_index]
            else:
                fj_val = 0
        
        if inst.fk is not None:
            fk_index = int(inst.fk, 2)
            fk_val = self.registros.regs[fk_index]
        elif inst.is_imm:
            fk_val = inst.imm   

        if (fu.type == "alu" or fu.type == "saxs"):
            result = fu.execute(inst.opname, fj_val, fk_val, fj_index)
            inst.result = result
        elif (fu.type == "memory"):
            result = fu.execute(inst.opname, fj_val, fk_val, fi_val)
            inst.result = result
        else:
            result = fu.execute(inst.opname, fj_val, fk_val)
            inst.result = result

        
        """print(
            f"Name: {inst.opname}",
            f"Is Imm: {inst.is_imm}",
            f"Imm: {inst.imm}",
            f"Clock: {fu.clocks}",
            f"fi_reg: {fi_index}",
            f"fj_val: {fj_val}",
            f"fk_val: {fk_val}",
            f"result: {inst.result}",
        )"""
        
        
        if fu.clocks == 0:
            self.instructions[fu.inst_pc].ex_cmplt = self.clock

    
    """ Writeback stage of the scoreboard"""
    def write_back(self, fu): 
        inst = self.instructions[fu.inst_pc]

        if inst.fi and inst.result is not None and fu.zero_flag == False:
            fi_index = int(inst.fi, 2)
            self.registros.regs[fi_index] = inst.result & 0xFFFFFFFF
        elif (fu.zero_flag == True):
            self.pc = inst.result
            fu.zero_flag = False
            self.wait_branch = False
        else:
            self.wait_branch = False
        
        

        #Write back confirmation 
        fu.write_back(self.units)
        self.instructions[fu.inst_pc].write_res = self.clock
        # clear out the result register status
        del self.reg_status[fu.fi]
        fu.clear()
    
# Obtener el directorio del script actual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Definir rutas a los archivos
dataFile = os.path.join(script_dir, "encrypted_image.png")
llave = os.path.join(script_dir, "key.txt")

ensamblar("Proyecto_arqui/procesador/Desencriptar.txt", "Proyecto_arqui/procesador/salida.txt")
sb = Pipeline_marcador("salida.txt", dataFile, llave)

while not sb.done():
    sb.tick()

save_encrypted_file(sb, dataFile)
#for instruction in sb.instructions:
#    print(str(instruction))

#print(sb.registros.dump())
#print(sb.memory.read_data(0, True))
#print(sb.pc)


