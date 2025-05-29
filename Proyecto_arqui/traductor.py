#Traductor de Ensamblador a código máquina
#Ingreso el archivo de ensablador que quiero leer

def leer_asm(programa):
    with open(programa, 'r') as archivo:
        lineas = archivo.readlines()
    instrucciones = [linea.strip() for linea in lineas if linea.strip()]
    return instrucciones

instrucciones = leer_asm("programa.asm")
print(instrucciones)

#--------------------------------------------------------------------------------
#Lista de indentificadores de cada instrucción:

opcodes = {
    'LOOP': '0000',
    'SAXS': '0001',
    'ADD':  '0010',
    'SUB':  '0011',
    'MUL':  '0100',
    'DIV':  '0101',
    'AND':  '0110',
    'OR':   '0111',
    'XOR':  '1000',
    'SHRL': '1001',
    'SHLL': '1010',
    'STOR': '1011',
    'LOAD': '1100',
    'STK':  '1101',
    'DLT':  '1110'
}
#--------------------------------------------------------------------------------
#Identificacion de Registros y transformacion de inm en valores bin

def reg_a_bin(reg):
    if not reg.startswith("R"):
        raise ValueError(f"Registro inválido: {reg}")
    num = int(reg[1:])
    if num < 0 or num > 15:
        raise ValueError(f"Registro fuera de rango: {reg}")
    return format(num, '04b')

def imm_a_bin(valor, bits):
    return format(int(valor), f'0{bits}b')
#--------------------------------------------------------------------------------
#Identificacion de tipo de inst (ALU,MEM,Branch)
def tipo_instruccion(nombre):
    if nombre == 'LOOP':
        return 'branch'
    elif nombre in ['LOAD', 'STOR', 'STK', 'DLT']:
        return 'memoria'
    else:
        return 'aritmetica'

#--------------------------------------------------------------------------------
#Instrucciones a binario

def traducir_instruccion(instr):
    partes = instr.replace(',', '').split()
    nombre = partes[0]
    tipo = tipo_instruccion(nombre)
    opcode = opcodes[nombre]

    if tipo == 'branch':
        reg_cond = reg_a_bin(partes[1])
        tag = imm_a_bin(partes[2], 13)
        return opcode + reg_cond + tag

    elif tipo == 'memoria':
        reg_dest = partes[1]
        if reg_dest == "R0":
            raise ValueError("Error: No se puede escribir en R0, es de solo lectura.")

        reg_dest_bin = reg_a_bin(reg_dest)
        reg_dir_bin = reg_a_bin(partes[2])
        reg_offset_bin = reg_a_bin(partes[3])
        return opcode + reg_dest_bin + reg_dir_bin + reg_offset_bin + '00000'

    elif tipo == 'aritmetica':
        reg_dest = partes[1]
        if reg_dest == "R0":
            raise ValueError("Error: No se puede escribir en R0, es de solo lectura.")

        reg_dest_bin = reg_a_bin(reg_dest)
        reg_src1_bin = reg_a_bin(partes[2])
        src2 = partes[3]

        if src2.startswith("R"):
            reg_src2_bin = reg_a_bin(src2)
            return opcode + '0' + reg_dest_bin + reg_src1_bin + reg_src2_bin + '0000'
        else:
            imm = imm_a_bin(src2, 8)
            return opcode + '1' + reg_dest_bin + reg_src1_bin + imm


#-------------------------------------------------------------------------------
#Union de todo
def ensamblar(nombre_entrada, nombre_salida):
    instrucciones = leer_asm(nombre_entrada)
    binarios = []

    for instr in instrucciones:
        binario = traducir_instruccion(instr)
        binarios.append(binario)

    with open(nombre_salida, 'w') as archivo:
        for linea in binarios:
            archivo.write(linea + '\n')


ensamblar("programa.asm", "salida.txt")


