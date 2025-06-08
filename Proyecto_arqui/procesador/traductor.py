# ------------------------------------------------------------------------------
# Paso 1: Leer y extraer etiquetas
def leer_asm_con_etiquetas(programa):
    with open(programa, 'r') as archivo:
        lineas = archivo.readlines()

    instrucciones = []
    etiquetas = {}
    linea_real = 0

    for i, linea in enumerate(lineas):
        linea = linea.strip()
        if not linea:
            continue

        if ':' in linea:
            nombre_etiqueta = linea.replace(':', '').strip()
            etiquetas[nombre_etiqueta] = linea_real
        else:
            instrucciones.append(linea)
            linea_real += 1

    return instrucciones, etiquetas

# ------------------------------------------------------------------------------
# Codificación de registros y valores inmediatos
def reg_a_bin(reg):
    if not reg.startswith("R"):
        raise ValueError(f"Registro inválido: {reg}")
    num = int(reg[1:])
    if num < 0 or num > 15:
        raise ValueError(f"Registro fuera de rango: {reg}")
    return format(num, '04b')

def imm_a_bin(valor, bits):
    return format(int(valor), f'0{bits}b')

# ------------------------------------------------------------------------------
# Diccionario de opcodes
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

# ------------------------------------------------------------------------------
# Tipo de instrucción
def tipo_instruccion(nombre):
    if nombre == 'LOOP':
        return 'branch'
    elif nombre in ['LOAD', 'STOR', 'STK', 'DLT']:
        return 'memoria'
    else:
        return 'aritmetica'

# ------------------------------------------------------------------------------
# Traductor con etiquetas
def traducir_instruccion(instr, etiquetas, pc):
    partes = instr.replace(',', '').split()
    nombre = partes[0]
    tipo = tipo_instruccion(nombre)
    opcode = opcodes[nombre]

    if tipo == 'branch':
        reg_cond = reg_a_bin(partes[1])
        destino = partes[2]

        # Convertir etiqueta o valor inmediato a 13 bits
        if destino in etiquetas:
            offset = etiquetas[destino]  # Dirección absoluta de la etiqueta
        elif destino.isdigit():
            offset = int(destino)
        else:
            raise ValueError(f"Etiqueta o número inválido: '{destino}' en instrucción '{instr}'")

        if offset < 0 or offset >= 2**13:
            raise ValueError(f"Offset fuera de rango (0 a 8191): {offset}")

        tag = imm_a_bin(offset, 13)
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

# ------------------------------------------------------------------------------
# Ensamblador principal
def ensamblar(nombre_entrada, nombre_salida):
    instrucciones, etiquetas = leer_asm_con_etiquetas(nombre_entrada)
    binarios = []

    for pc, instr in enumerate(instrucciones):
        binario = traducir_instruccion(instr, etiquetas, pc)
        binarios.append(binario)

    with open(nombre_salida, 'w') as archivo:
        for linea in binarios:
            archivo.write(linea + '\n')

# ------------------------------------------------------------------------------
# Ejecutar
ensamblar("Proyecto_arqui/procesador/programa.asm", "Proyecto_arqui/procesador/salida.txt")



